"""Telemetry pipelines and console bridge."""

from __future__ import annotations

import copy
import importlib.resources
import json
import logging
import threading
from collections import deque
from collections.abc import Callable, Iterable, Mapping
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING, Any

from townlet.agents.models import PersonalityProfiles
from townlet.config import SimulationConfig
from townlet.console.auth import ConsoleAuthenticationError, ConsoleAuthenticator
from townlet.console.command import ConsoleCommandEnvelope, ConsoleCommandResult
from townlet.telemetry.aggregation import (
    StreamPayloadBuilder,
    TelemetryAggregator,
)
from townlet.telemetry.event_dispatcher import TelemetryEventDispatcher
from townlet.telemetry.events import (
    RELATIONSHIP_FRIENDSHIP_EVENT,
    RELATIONSHIP_RIVALRY_EVENT,
    RELATIONSHIP_SOCIAL_ALERT_EVENT,
)
from townlet.telemetry.narration import NarrationRateLimiter
from townlet.telemetry.transform import (
    EnsureFieldsTransform,
    RedactFieldsTransform,
    SchemaValidationTransform,
    SnapshotEventNormalizer,
    TelemetryTransformPipeline,
    TransformPipelineConfig,
    compile_json_schema,
    copy_relationship_snapshot,
    normalize_perturbations_payload,
)
from townlet.config.loader import TelemetryTransformEntry
from townlet.telemetry.transport import (
    TelemetryTransportError,
    TransportBuffer,
    create_transport,
)
from townlet.telemetry.worker import TelemetryWorkerManager
from townlet.world.core.runtime_adapter import ensure_world_adapter

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from townlet.world.grid import WorldState
    from townlet.world.observations.interfaces import WorldRuntimeAdapterProtocol


class TelemetryPublisher:
    """Publish telemetry snapshots, manage console ingress, and track health."""

    def __init__(self, config: SimulationConfig) -> None:
        """Capture world snapshots and emit telemetry for a simulation tick."""
        self.config = config
        self.schema_version = "0.9.7"
        self._relationship_narration_cfg = self.config.telemetry.relationship_narration
        self._personality_narration_cfg = self.config.telemetry.personality_narration
        self._console_buffer: list[object] = []
        self._latest_queue_metrics: dict[str, int] | None = None
        self._latest_embedding_metrics: dict[str, float] | None = None
        self._latest_events: list[dict[str, object]] = []
        self._latest_policy_metadata_event: dict[str, object] | None = None
        self._latest_policy_anneal_event: dict[str, object] | None = None
        self._event_subscribers: list[Callable[[list[dict[str, object]]], None]] = []
        self._latest_employment_metrics: dict[str, object] = {}
        self._latest_conflict_snapshot: dict[str, object] = {
            "queues": {"cooldown_events": 0, "ghost_step_events": 0, "rotation_events": 0},
            "queue_history": [],
            "rivalry": {},
            "rivalry_events": [],
        }
        self._latest_relationship_metrics: dict[str, object] | None = None
        self._latest_job_snapshot: dict[str, object] = {}
        self._latest_economy_snapshot: dict[str, object] = {}
        self._latest_relationship_snapshot: dict[str, dict[str, dict[str, float]]] = {}
        self._latest_relationship_updates: list[dict[str, object]] = []
        self._previous_relationship_snapshot: dict[str, dict[str, dict[str, float]]] = {}
        self._narration_limiter = NarrationRateLimiter(self.config.telemetry.narration)
        self._latest_narrations: list[dict[str, object]] = []
        self._latest_anneal_status: dict[str, object] | None = None
        self._latest_relationship_overlay: dict[str, list[dict[str, object]]] = {}
        self._latest_policy_snapshot: dict[str, dict[str, object]] = {}
        self._kpi_history: dict[str, list[float]] = {
            "queue_conflict_intensity": [],
            "employment_lateness": [],
            "late_help_events": [],
        }
        self._latest_affordance_manifest: dict[str, object] = {}
        self._latest_affordance_runtime: dict[str, object] = {
            "tick": 0,
            "running": {},
            "running_count": 0,
            "active_reservations": {},
            "event_counts": {
                "start": 0,
                "finish": 0,
                "fail": 0,
                "precondition_fail": 0,
            },
        }
        self._latest_reward_breakdown: dict[str, dict[str, float]] = {}
        self._latest_stability_inputs: dict[str, object] = {}
        self._latest_stability_metrics: dict[str, object] = {}
        self._latest_perturbations: dict[str, object] = {}
        self._latest_policy_identity: dict[str, object] | None = None
        self._latest_snapshot_migrations: list[str] = []
        self._queue_fairness_history: list[dict[str, object]] = []
        self._rivalry_event_history: list[dict[str, object]] = []
        self._latest_possessed_agents: list[str] = []
        self._latest_precondition_failures: list[dict[str, object]] = []
        self._console_results_batch: list[dict[str, Any]] = []
        self._console_results_history: deque[dict[str, Any]] = deque(maxlen=200)
        self._console_audit_path = Path("logs/console/commands.jsonl")
        self._latest_health_status: dict[str, object] = {}
        self._latest_economy_settings: dict[str, float] = {
            str(key): float(value) for key, value in self.config.economy.items()
        }
        self._latest_price_spikes: dict[str, dict[str, object]] = {}
        self._latest_utilities: dict[str, bool] = {"power": True, "water": True}
        self._console_auth = ConsoleAuthenticator(config.console_auth)
        self._social_event_history: deque[dict[str, object]] = deque(maxlen=60)
        self._latest_relationship_summary: dict[str, object] = {}
        self._latest_personality_snapshot: dict[str, object] = {}
        self._current_tick: int = 0
        self._pending_manual_narrations: list[dict[str, object]] = []
        self._manual_narration_lock = threading.Lock()
        self._runtime_variant: str | None = None
        self._event_dispatcher = TelemetryEventDispatcher()
        self._event_dispatcher.register_subscriber(self._handle_event)
        transport_cfg = self.config.telemetry.transport
        self._transport_config = transport_cfg
        self._transport_retry = transport_cfg.retry
        self._transport_buffer = TransportBuffer(
            max_batch_size=int(transport_cfg.buffer.max_batch_size),
            max_buffer_bytes=int(transport_cfg.buffer.max_buffer_bytes),
        )
        worker_cfg = self.config.telemetry.worker
        self._transport_status: dict[str, Any] = {
            "connected": False,
            "dropped_messages": 0,
            "last_error": None,
            "last_failure_tick": None,
            "last_success_tick": None,
            "queue_length": 0,
            "last_flush_duration_ms": None,
            "last_flush_payload_bytes": 0,
            "last_batch_count": 0,
            "payloads_flushed_total": 0,
            "bytes_flushed_total": 0,
            "queue_length_peak": 0,
            "consecutive_send_failures": 0,
            "send_failures_total": 0,
            "tls_enabled": bool(getattr(transport_cfg, "enable_tls", False)),
            "verify_hostname": bool(getattr(transport_cfg, "verify_hostname", True)),
            "allow_plaintext": bool(getattr(transport_cfg, "allow_plaintext", False)),
            "worker_alive": True,
            "worker_error": None,
            "worker_restart_count": 0,
            "last_worker_error": None,
            "auth_enabled": bool(config.console_auth.enabled),
            "backpressure_strategy": str(getattr(worker_cfg, "backpressure", "drop_oldest")),
        }
        if transport_cfg.type == "tcp" and not self._transport_status["tls_enabled"]:
            endpoint = getattr(transport_cfg, "endpoint", None) or ""
            logger.warning(
                "telemetry_transport_plaintext host=%s message='TLS disabled; plaintext transport is intended for localhost dev only.'",
                endpoint,
            )
        self._transport_client = self._build_transport_client()
        poll_interval = float(getattr(transport_cfg, "worker_poll_seconds", 0.5))
        # Expose the flush poll interval for tests/diagnostics (legacy compatibility)
        self._flush_poll_interval = poll_interval
        self._worker_manager = TelemetryWorkerManager(
            buffer=self._transport_buffer,
            retry_policy=self._transport_retry,
            status=self._transport_status,
            send_callable=lambda payload: self._transport_client.send(payload),
            reset_callable=self._reset_transport_client,
            poll_interval_seconds=poll_interval,
            flush_interval_ticks=int(transport_cfg.buffer.flush_interval_ticks),
            backpressure_strategy=str(getattr(worker_cfg, "backpressure", "drop_oldest")),
            block_timeout_seconds=float(getattr(worker_cfg, "block_timeout_seconds", 0.5)),
            restart_limit=int(getattr(worker_cfg, "restart_limit", 3)),
        )
        self._diff_enabled = bool(getattr(config.telemetry, "diff_enabled", False))
        self._payload_builder = StreamPayloadBuilder(
            schema_version=self.schema_version,
            diff_enabled=self._diff_enabled,
        )
        self._aggregator = TelemetryAggregator(
            self._payload_builder,
            console_sink=self._store_console_results,
            failure_sink=self._store_loop_failure,
        )
        configured_transforms = self._build_transforms_from_config()
        self._transform_config = TransformPipelineConfig(transforms=tuple(configured_transforms))
        self._transform_pipeline = self._transform_config.build_pipeline()
        self._worker_manager.start()

    def _build_transforms_from_config(self) -> list[object]:
        """Instantiate telemetry transforms based on configuration."""

        transforms_cfg = getattr(self.config.telemetry, "transforms", None)
        if transforms_cfg is None or not transforms_cfg.pipeline:
            return list(self._default_transforms())
        instantiated: list[object] = []
        for entry in transforms_cfg.pipeline:
            instantiated.append(self._instantiate_transform(entry))
        return instantiated

    def _default_transforms(self) -> tuple[object, ...]:
        builtin_schemas = self._load_builtin_schemas()
        transforms: list[object] = [
            SnapshotEventNormalizer(),
            RedactFieldsTransform(fields=("policy_identity",), apply_to_kinds=("snapshot", "diff")),
            EnsureFieldsTransform(
                required_fields_by_kind={
                    "snapshot": {"schema_version", "tick"},
                    "diff": {"schema_version", "tick", "changes"},
                },
                default_required_fields=("tick",),
            ),
        ]
        if builtin_schemas:
            transforms.append(
                SchemaValidationTransform(
                    schema_by_kind=builtin_schemas,
                    mode="drop",
                )
            )
        return tuple(transforms)

    def _load_builtin_schemas(self) -> dict[str, object]:
        schema_map: dict[str, object] = {}
        try:
            package = importlib.resources.files("townlet.telemetry.schemas")
        except (AttributeError, ModuleNotFoundError):  # pragma: no cover - best effort fallback
            return schema_map
        for kind, filename in (("snapshot", "snapshot"), ("diff", "diff")):
            try:
                with importlib.resources.as_file(package / f"{filename}.schema.json") as path:
                    payload = json.loads(path.read_text())
            except FileNotFoundError:  # pragma: no cover - optional asset
                continue
            except json.JSONDecodeError as exc:  # pragma: no cover - invalid asset
                logger.error("Failed to parse builtin telemetry schema %s: %s", filename, exc)
                continue
            schema_map[kind] = compile_json_schema(payload)
        return schema_map

    def _instantiate_transform(self, entry: TelemetryTransformEntry) -> object:
        transform_id = entry.id
        options = entry.options or {}

        if transform_id == "snapshot_normalizer":
            return SnapshotEventNormalizer()

        if transform_id == "redact_fields":
            fields = options.get("fields")
            if not fields:
                raise ValueError("telemetry.transforms.redact_fields requires 'fields' option")
            if not isinstance(fields, Iterable) or isinstance(fields, (str, bytes)):
                raise TypeError("telemetry.transforms.redact_fields.fields must be a sequence of field names")
            kinds = options.get("kinds")
            apply_to_kinds: Iterable[str] | None
            if kinds is None:
                apply_to_kinds = ("snapshot", "diff")
            else:
                if not isinstance(kinds, Iterable) or isinstance(kinds, (str, bytes)):
                    raise TypeError("telemetry.transforms.redact_fields.kinds must be a sequence of event kinds")
                apply_to_kinds = [str(kind) for kind in kinds]
            return RedactFieldsTransform(fields=[str(field) for field in fields], apply_to_kinds=apply_to_kinds)

        if transform_id == "ensure_fields":
            required_by_kind = options.get("required_fields_by_kind") or {}
            if not isinstance(required_by_kind, Mapping):
                raise TypeError("telemetry.transforms.ensure_fields.required_fields_by_kind must be a mapping")
            processed_required = {
                str(kind): {str(field) for field in fields}
                for kind, fields in required_by_kind.items()
            }
            default_required = options.get("default_required_fields")
            if default_required is not None:
                if not isinstance(default_required, Iterable) or isinstance(default_required, (str, bytes)):
                    raise TypeError("telemetry.transforms.ensure_fields.default_required_fields must be a sequence")
                default_required_set = {str(field) for field in default_required}
            else:
                default_required_set = ("tick",)
            return EnsureFieldsTransform(
                required_fields_by_kind=processed_required,
                default_required_fields=default_required_set,
            )

        if transform_id == "schema_validator":
            schema_option = options.get("schemas")
            if not isinstance(schema_option, Mapping) or not schema_option:
                raise ValueError("telemetry.transforms.schema_validator requires a 'schemas' mapping")
            compiled: dict[str, object] = {}
            for kind, schema_path in schema_option.items():
                path = Path(str(schema_path)).expanduser()
                if not path.is_absolute():
                    path = (Path.cwd() / path).resolve()
                if not path.exists():
                    raise FileNotFoundError(f"Telemetry schema file not found: {path}")
                try:
                    schema_payload = json.loads(path.read_text())
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Failed to parse telemetry schema at {path}: {exc}") from exc
                compiled[str(kind)] = compile_json_schema(schema_payload)
            mode = str(options.get("mode", "drop")).lower()
            return SchemaValidationTransform(schema_by_kind=compiled, mode=mode)

        raise ValueError(f"Unsupported telemetry transform id '{transform_id}'")

    def queue_console_command(self, command: object) -> None:
        """Authorise and enqueue an incoming console command payload."""
        try:
            sanitized, _principal = self._console_auth.authorise(command)
        except ConsoleAuthenticationError as exc:
            identity = exc.identity
            envelope = ConsoleCommandEnvelope(
                name=identity.get("name") or "unknown",
                args=[],
                kwargs={},
                cmd_id=identity.get("cmd_id"),
                issuer=identity.get("issuer"),
            )
            result = ConsoleCommandResult.from_error(
                envelope,
                code="unauthorized",
                message=exc.message,
                details={"reason": "auth_failed"},
            )
            self.emit_event("console.result", result.to_dict())
            logger.warning(
                "Rejected console command due to authentication failure: name=%s issuer=%s",
                identity.get("name"),
                identity.get("issuer"),
            )
            return
        except TypeError as exc:
            logger.warning("Rejected malformed console command: %s", exc)
            return
        except Exception:  # pragma: no cover - defensive
            logger.exception("Unexpected error while authenticating console command")
            return

        self._console_buffer.append(sanitized)

    def drain_console_buffer(self) -> Iterable[object]:
        """Return queued console commands and clear the buffer."""
        drained = list(self._console_buffer)
        self._console_buffer.clear()
        return drained

    def export_state(self) -> dict[str, object]:
        state: dict[str, object] = {
            "queue_metrics": dict(self._latest_queue_metrics or {}),
            "embedding_metrics": dict(self._latest_embedding_metrics or {}),
            "conflict_snapshot": dict(self._latest_conflict_snapshot),
            "relationship_metrics": dict(self._latest_relationship_metrics or {}),
            "job_snapshot": dict(getattr(self, "_latest_job_snapshot", {})),
            "economy_snapshot": dict(getattr(self, "_latest_economy_snapshot", {})),
            "economy_settings": dict(self._latest_economy_settings),
            "price_spikes": {
                event_id: {
                    "magnitude": float(data.get("magnitude", 0.0)),
                    "targets": list(data.get("targets", ())),
                }
                for event_id, data in self._latest_price_spikes.items()
            },
            "utilities": {key: bool(value) for key, value in self._latest_utilities.items()},
            "employment_metrics": dict(self._latest_employment_metrics or {}),
            "events": list(self._latest_events),
            "affordance_runtime": self.latest_affordance_runtime(),
            "relationship_snapshot": copy_relationship_snapshot(
                self._latest_relationship_snapshot
            ),
            "relationship_updates": [dict(update) for update in self._latest_relationship_updates],
            "narrations": [dict(entry) for entry in self._latest_narrations],
            "narration_state": self._narration_limiter.export_state(),
            "reward_breakdown": self.latest_reward_breakdown(),
            "perturbations": self.latest_perturbations(),
            "relationship_summary": dict(self._latest_relationship_summary),
            "social_events": [dict(event) for event in self._social_event_history],
        }
        if self._latest_affordance_manifest:
            state["affordance_manifest"] = dict(self._latest_affordance_manifest)
        if self._latest_personality_snapshot:
            state["personalities"] = copy.deepcopy(self._latest_personality_snapshot)
        if self._latest_anneal_status is not None:
            state["anneal_status"] = dict(self._latest_anneal_status)
        if self._latest_policy_snapshot:
            state["policy_snapshot"] = {
                agent: dict(entry) for agent, entry in self._latest_policy_snapshot.items()
            }
        if self._latest_relationship_overlay:
            state["relationship_overlay"] = {
                agent: [dict(item) for item in entries]
                for agent, entries in self._latest_relationship_overlay.items()
            }
        if any(self._kpi_history.values()):
            state["kpi_history"] = self.kpi_history()
        if self._latest_policy_identity is not None:
            state["policy_identity"] = dict(self._latest_policy_identity)
        if self._latest_snapshot_migrations:
            state["snapshot_migrations"] = list(self._latest_snapshot_migrations)
        state["transport_status"] = dict(self._transport_status)
        state["transport_buffer_pending"] = self._worker_manager.queue_length()
        if self._latest_health_status:
            state["health"] = dict(self._latest_health_status)
        state["queue_history"] = list(self._queue_fairness_history)
        state["rivalry_events"] = list(self._rivalry_event_history)
        state["console_results"] = list(self._console_results_batch)
        state["possessed_agents"] = list(self._latest_possessed_agents)
        if self._latest_policy_metadata_event is not None:
            state["policy_metadata_event"] = copy.deepcopy(self._latest_policy_metadata_event)
        if self._latest_policy_anneal_event is not None:
            state["policy_anneal_event"] = copy.deepcopy(self._latest_policy_anneal_event)
        if self._latest_precondition_failures:
            state["precondition_failures"] = [
                dict(entry) for entry in self._latest_precondition_failures
            ]
        promotion_state = self.latest_promotion_state()
        if promotion_state is not None:
            state["promotion_state"] = promotion_state
        return state

    def import_state(self, payload: dict[str, object]) -> None:
        self._latest_queue_metrics = payload.get("queue_metrics") or None
        if self._latest_queue_metrics is not None:
            self._latest_queue_metrics = dict(self._latest_queue_metrics)

        self._latest_embedding_metrics = payload.get("embedding_metrics") or None
        if self._latest_embedding_metrics is not None:
            self._latest_embedding_metrics = dict(self._latest_embedding_metrics)

        conflict_snapshot = payload.get("conflict_snapshot") or {}
        self._latest_conflict_snapshot = dict(conflict_snapshot)

        relationship_metrics = payload.get("relationship_metrics")
        self._latest_relationship_metrics = (
            dict(relationship_metrics) if relationship_metrics else None
        )
        summary_payload = payload.get("relationship_summary") or {}
        if isinstance(summary_payload, Mapping):
            self._latest_relationship_summary = dict(summary_payload)
        social_events_payload = payload.get("social_events") or []
        if isinstance(social_events_payload, list):
            self._social_event_history = deque(
                [dict(entry) for entry in social_events_payload],
                maxlen=self._social_event_history.maxlen,
            )

        self._latest_job_snapshot = dict(payload.get("job_snapshot", {}))
        self._latest_economy_snapshot = dict(payload.get("economy_snapshot", {}))
        economy_settings = payload.get("economy_settings", {})
        if isinstance(economy_settings, Mapping):
            self._latest_economy_settings = {
                str(key): float(value) for key, value in economy_settings.items()
            }
        else:
            self._latest_economy_settings = {
                str(key): float(value) for key, value in self.config.economy.items()
            }
        price_spikes_payload = payload.get("price_spikes", {})
        if isinstance(price_spikes_payload, Mapping):
            converted: dict[str, dict[str, object]] = {}
            for event_id, data in price_spikes_payload.items():
                if not isinstance(data, Mapping):
                    continue
                targets = data.get("targets", [])
                if isinstance(targets, (list, tuple)):
                    target_list = [str(entry) for entry in targets]
                else:
                    target_list = [str(targets)] if targets is not None else []
                converted[str(event_id)] = {
                    "magnitude": float(data.get("magnitude", 0.0)),
                    "targets": target_list,
                }
            self._latest_price_spikes = converted
        else:
            self._latest_price_spikes = {}
        utilities_payload = payload.get("utilities", {})
        if isinstance(utilities_payload, Mapping):
            self._latest_utilities = {
                str(key): bool(value) for key, value in utilities_payload.items()
            }
        else:
            self._latest_utilities = {"power": True, "water": True}
        self._latest_employment_metrics = dict(payload.get("employment_metrics", {}))
        self._latest_events = list(payload.get("events", []))
        runtime_payload = payload.get("affordance_runtime") or {}
        if isinstance(runtime_payload, Mapping):
            running_section = runtime_payload.get("running") or {}
            self._latest_affordance_runtime = {
                "tick": int(runtime_payload.get("tick", 0)),
                "running_count": int(runtime_payload.get("running_count", 0)),
                "running": {
                    str(object_id): dict(entry)
                    for object_id, entry in running_section.items()
                    if isinstance(entry, Mapping)
                },
                "active_reservations": dict(
                    runtime_payload.get("active_reservations", {}) or {}
                ),
                "event_counts": dict(runtime_payload.get("event_counts", {}) or {}),
            }
        else:
            self._latest_affordance_runtime = {
                "tick": 0,
                "running_count": 0,
                "running": {},
                "active_reservations": {},
                "event_counts": {
                    "start": 0,
                    "finish": 0,
                    "fail": 0,
                    "precondition_fail": 0,
                },
            }
        snapshot_payload = payload.get("relationship_snapshot") or {}
        if isinstance(snapshot_payload, dict):
            snapshot_copy = copy_relationship_snapshot(snapshot_payload)
            self._latest_relationship_snapshot = snapshot_copy
            self._previous_relationship_snapshot = copy_relationship_snapshot(snapshot_copy)
        updates_payload = payload.get("relationship_updates", [])
        if isinstance(updates_payload, list):
            self._latest_relationship_updates = [dict(update) for update in updates_payload]
        narrations_payload = payload.get("narrations", [])
        if isinstance(narrations_payload, list):
            self._latest_narrations = [dict(entry) for entry in narrations_payload]
        else:
            self._latest_narrations = []
        narration_state = payload.get("narration_state")
        if isinstance(narration_state, dict):
            self._narration_limiter.import_state(narration_state)
        anneal_status = payload.get("anneal_status")
        if isinstance(anneal_status, dict):
            self._latest_anneal_status = dict(anneal_status)
        else:
            self._latest_anneal_status = None
        policy_snapshot = payload.get("policy_snapshot")
        if isinstance(policy_snapshot, Mapping):
            self._latest_policy_snapshot = {
                str(agent): dict(data)
                for agent, data in policy_snapshot.items()
                if isinstance(data, Mapping)
            }
        else:
            self._latest_policy_snapshot = {}
        overlay_payload = payload.get("relationship_overlay")
        if isinstance(overlay_payload, Mapping):
            self._latest_relationship_overlay = {
                str(agent): [dict(item) for item in entries]
                for agent, entries in overlay_payload.items()
                if isinstance(entries, list)
            }
        else:
            self._latest_relationship_overlay = {}
        manifest_payload = payload.get("affordance_manifest")
        if isinstance(manifest_payload, Mapping):
            self._latest_affordance_manifest = dict(manifest_payload)
        else:
            self._latest_affordance_manifest = {}
        reward_payload = payload.get("reward_breakdown")
        if isinstance(reward_payload, Mapping):
            self._latest_reward_breakdown = {
                str(agent): dict(data)
                for agent, data in reward_payload.items()
                if isinstance(data, Mapping)
            }
        else:
            self._latest_reward_breakdown = {}

        perturbations_payload = payload.get("perturbations")
        if isinstance(perturbations_payload, Mapping):
            self._latest_perturbations = normalize_perturbations_payload(
                perturbations_payload
            )
        else:
            self._latest_perturbations = {}

        policy_identity_payload = payload.get("policy_identity")
        if isinstance(policy_identity_payload, Mapping):
            self._latest_policy_identity = dict(policy_identity_payload)
        else:
            self._latest_policy_identity = None

        migrations_payload = payload.get("snapshot_migrations")
        if isinstance(migrations_payload, list):
            self._latest_snapshot_migrations = [str(item) for item in migrations_payload]
        else:
            self._latest_snapshot_migrations = []

        kpi_payload = payload.get("kpi_history")
        if isinstance(kpi_payload, Mapping):
            history: dict[str, list[float]] = {}
            for name, values in kpi_payload.items():
                if isinstance(values, list):
                    coerced = [float(value) for value in values if isinstance(value, (int, float))]
                    history[str(name)] = coerced
            if history:
                self._kpi_history = history
        transport_status = payload.get("transport_status")
        if isinstance(transport_status, Mapping):
            self._transport_status.update(
                connected=bool(transport_status.get("connected", False)),
                dropped_messages=int(transport_status.get("dropped_messages", 0)),
                last_error=transport_status.get("last_error"),
                last_failure_tick=transport_status.get("last_failure_tick"),
                last_success_tick=transport_status.get("last_success_tick"),
            )
        else:
            self._transport_status.update(
                connected=False,
                last_error=None,
                last_failure_tick=None,
                last_success_tick=None,
            )
        pending = payload.get("transport_buffer_pending")
        if isinstance(pending, int) and pending > 0:
            self._transport_status["dropped_messages"] += int(pending)
        self._worker_manager.clear_buffer()
        health_payload = payload.get("health")
        if isinstance(health_payload, Mapping):
            self._latest_health_status = {
                str(key): value for key, value in health_payload.items()
            }
        else:
            self._latest_health_status = {}

        history_payload = payload.get("queue_history")
        if isinstance(history_payload, list):
            self._queue_fairness_history = [
                {
                    "tick": int(item.get("tick", 0)),
                    "delta": dict(item.get("delta", {})),
                    "totals": dict(item.get("totals", {})),
                }
                for item in history_payload
                if isinstance(item, Mapping)
            ]
        else:
            self._queue_fairness_history = []

        rivalry_payload = payload.get("rivalry_events")
        if isinstance(rivalry_payload, list):
            self._rivalry_event_history = [
                {
                    "tick": int(item.get("tick", 0)),
                    "agent_a": str(item.get("agent_a", "")),
                    "agent_b": str(item.get("agent_b", "")),
                    "intensity": float(item.get("intensity", 0.0)),
                    "reason": str(item.get("reason", "unknown")),
                }
                for item in rivalry_payload
                if isinstance(item, Mapping)
            ]
        else:
            self._rivalry_event_history = []

        console_payload = payload.get("console_results")
        if isinstance(console_payload, list):
            self._console_results_batch = [
                dict(entry) for entry in console_payload if isinstance(entry, Mapping)
            ]
        else:
            self._console_results_batch = []
        possessed_payload = payload.get("possessed_agents")
        if isinstance(possessed_payload, list):
            self._latest_possessed_agents = [str(agent) for agent in possessed_payload]
        else:
            self._latest_possessed_agents = []
        metadata_event_payload = payload.get("policy_metadata_event")
        if isinstance(metadata_event_payload, Mapping):
            self._latest_policy_metadata_event = copy.deepcopy(dict(metadata_event_payload))
        else:
            self._latest_policy_metadata_event = None
        anneal_event_payload = payload.get("policy_anneal_event")
        if isinstance(anneal_event_payload, Mapping):
            self._latest_policy_anneal_event = copy.deepcopy(dict(anneal_event_payload))
        else:
            self._latest_policy_anneal_event = None
        failures_payload = payload.get("precondition_failures")
        if isinstance(failures_payload, list):
            self._latest_precondition_failures = [
                dict(entry) for entry in failures_payload if isinstance(entry, Mapping)
            ]
        else:
            self._latest_precondition_failures = []
        promotion_state_payload = payload.get("promotion_state")
        if isinstance(promotion_state_payload, Mapping):
            metrics = dict(self._latest_stability_metrics or {})
            metrics["promotion_state"] = dict(promotion_state_payload)
            self._latest_stability_metrics = metrics

        self._payload_builder.reset()

    def export_console_buffer(self) -> list[object]:
        return list(self._console_buffer)

    def import_console_buffer(self, buffer: Iterable[object]) -> None:
        self._console_buffer = list(buffer)

    def _ingest_console_results(self, results: Iterable[ConsoleCommandResult]) -> None:
        """Persist console results for audit logs and downstream subscribers."""

        self._aggregator.record_console_results(results)

    def _store_console_results(self, results: Iterable[ConsoleCommandResult]) -> None:
        batch: list[dict[str, Any]] = []
        for result in results:
            payload = result.to_dict()
            batch.append(payload)
            self._console_results_history.append(payload)
            self._append_console_audit(payload)
        self._console_results_batch = batch if batch else []

    def set_runtime_variant(self, variant: str | None) -> None:
        """Record which runtime variant produced the latest telemetry."""

        self._runtime_variant = variant

    def latest_console_results(self) -> list[dict[str, Any]]:
        return list(self._console_results_batch)

    def console_history(self) -> list[dict[str, Any]]:
        return list(self._console_results_history)

    def _ingest_possessed_agents(self, agents: Iterable[str]) -> None:
        self._latest_possessed_agents = sorted({str(agent) for agent in agents})

    def latest_possessed_agents(self) -> list[str]:
        return list(self._latest_possessed_agents)

    def latest_precondition_failures(self) -> list[dict[str, object]]:
        return [dict(entry) for entry in self._latest_precondition_failures]

    def latest_transport_status(self) -> dict[str, object]:
        """Return transport health and backlog counters for observability."""

        return dict(self._transport_status)


    def _ingest_loop_failure(self, payload: Mapping[str, object]) -> None:
        """Persist loop failure telemetry and append a failure event."""

        failure_events = list(self._aggregator.record_loop_failure(payload))
        transformed_events = self._transform_pipeline.process(failure_events)
        for event in transformed_events:
            self._enqueue_stream_payload(event.payload, tick=int(event.tick))

    def _store_loop_failure(self, payload: Mapping[str, object]) -> None:
        failure_data = dict(payload)
        failure_data.setdefault("status", "error")
        self._latest_health_status = failure_data
        event = {
            "kind": "loop_failure",
            "tick": failure_data.get("tick"),
            "error": failure_data.get("error"),
        }
        self._latest_events.append(event)
        if len(self._latest_events) > 128:
            self._latest_events = self._latest_events[-128:]
        logger.error(
            "simulation_loop_failure tick=%s error=%s",
            failure_data.get("tick"),
            failure_data.get("error"),
        )

    def _ingest_health_metrics(self, metrics: Mapping[str, object]) -> None:
        """Update health telemetry derived from the simulation loop."""

        self._latest_health_status = dict(metrics)

    def latest_health_status(self) -> dict[str, object]:
        """Return the most recently recorded health payload."""
        return dict(self._latest_health_status)

    def _build_transport_client(self):
        cfg = self._transport_config
        try:
            client = create_transport(
                transport_type=str(cfg.type),
                file_path=cfg.file_path,
                endpoint=getattr(cfg, "endpoint", None),
                connect_timeout=float(cfg.connect_timeout_seconds),
                send_timeout=float(cfg.send_timeout_seconds),
                enable_tls=bool(getattr(cfg, "enable_tls", False)),
                verify_hostname=bool(getattr(cfg, "verify_hostname", True)),
                ca_file=getattr(cfg, "ca_file", None),
                cert_file=getattr(cfg, "cert_file", None),
                key_file=getattr(cfg, "key_file", None),
                allow_plaintext=bool(getattr(cfg, "allow_plaintext", False)),
                websocket_url=getattr(cfg, "websocket_url", None),
            )
            start = getattr(client, "start", None)
            if callable(start):
                start()
            return client
        except TelemetryTransportError as exc:  # pragma: no cover - init failure
            message = f"Failed to initialise telemetry transport '{cfg.type}': {exc}"
            logger.error(message)
            raise RuntimeError(message) from exc

    def _reset_transport_client(self) -> None:
        client = getattr(self, "_transport_client", None)
        if client is not None:
            try:
                client.stop()
            except Exception:  # pragma: no cover - logging only
                logger.debug("Closing telemetry transport failed", exc_info=True)
        self._transport_client = self._build_transport_client()

    def _enqueue_stream_payload(self, payload: Mapping[str, Any], *, tick: int) -> None:
        encoded = json.dumps(
            payload,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        if not encoded.endswith(b"\n"):
            encoded += b"\n"
        self._worker_manager.enqueue(encoded, tick=int(tick))

    def stop_worker(self, *, wait: bool = True, timeout: float = 2.0) -> None:
        """Stop the background flush worker without closing transports."""

        self._worker_manager.stop(wait=wait, timeout=timeout)

    def close(self) -> None:
        self._worker_manager.close()
        try:
            self._transport_client.stop()
        except Exception:  # pragma: no cover - shutdown cleanup
            logger.debug("Closing telemetry transport failed", exc_info=True)

    def _capture_affordance_runtime(
        self,
        *,
        world: WorldState | WorldRuntimeAdapterProtocol,
        events: Iterable[Mapping[str, object]] | None,
        tick: int,
    ) -> None:
        adapter = ensure_world_adapter(world)
        runtime_snapshot = adapter.running_affordances_snapshot()
        running_payload = {
            str(object_id): asdict(state)
            for object_id, state in runtime_snapshot.items()
        }
        event_counts = {
            "start": 0,
            "finish": 0,
            "fail": 0,
            "precondition_fail": 0,
        }
        for event in events or ():
            if not isinstance(event, Mapping):
                continue
            name = str(event.get("event", ""))
            if name == "affordance_start":
                event_counts["start"] += 1
            elif name == "affordance_finish":
                event_counts["finish"] += 1
            elif name == "affordance_fail":
                event_counts["fail"] += 1
            elif name == "affordance_precondition_fail":
                event_counts["precondition_fail"] += 1
        self._latest_affordance_runtime = {
            "tick": int(tick),
            "running": running_payload,
            "running_count": len(running_payload),
            "active_reservations": dict(adapter.active_reservations),
            "event_counts": event_counts,
        }

    def _ingest_loop_tick(
        self,
        *,
        tick: int,
        world: WorldState,
        observations: dict[str, object],
        rewards: dict[str, float],
        events: Iterable[dict[str, object]] | None = None,
        policy_snapshot: Mapping[str, Mapping[str, object]] | None = None,
        kpi_history: bool = False,
        reward_breakdown: Mapping[str, Mapping[str, float]] | None = None,
        stability_inputs: Mapping[str, object] | None = None,
        perturbations: Mapping[str, object] | None = None,
        policy_identity: Mapping[str, object] | None = None,
        possessed_agents: Iterable[str] | None = None,
        social_events: Iterable[dict[str, object]] | None = None,
        runtime_variant: str | None = None,
    ) -> None:
        # Observations and rewards are consumed for downstream side effects.
        _ = observations, rewards
        tick = int(tick)
        if runtime_variant is not None:
            self._runtime_variant = runtime_variant
        self._current_tick = tick
        adapter = ensure_world_adapter(world)
        raw_world = getattr(adapter, "_world", world)
        self._narration_limiter.begin_tick(tick)
        manual_narrations = self._consume_manual_narrations()
        self._latest_narrations = manual_narrations
        previous_queue_metrics = dict(self._latest_queue_metrics or {})
        try:
            queue_metrics = adapter.queue_manager.metrics()
        except Exception:  # pragma: no cover - defensive guard for stubs
            logger.debug("Telemetry queue metrics unavailable; defaulting to zeros", exc_info=True)
            queue_metrics = {
                "cooldown_events": 0,
                "ghost_step_events": 0,
                "rotation_events": 0,
            }
        self._latest_queue_metrics = queue_metrics
        fairness_delta = {
            "cooldown_events": max(
                0,
                int(queue_metrics.get("cooldown_events", 0))
                - int(previous_queue_metrics.get("cooldown_events", 0)),
            ),
            "ghost_step_events": max(
                0,
                int(queue_metrics.get("ghost_step_events", 0))
                - int(previous_queue_metrics.get("ghost_step_events", 0)),
            ),
            "rotation_events": max(
                0,
                int(queue_metrics.get("rotation_events", 0))
                - int(previous_queue_metrics.get("rotation_events", 0)),
            ),
        }
        rivalry_snapshot = dict(adapter.rivalry_snapshot())
        self._queue_fairness_history.append(
            {
                "tick": int(tick),
                "delta": fairness_delta,
                "totals": dict(queue_metrics),
            }
        )
        if len(self._queue_fairness_history) > 120:
            self._queue_fairness_history.pop(0)

        new_events = adapter.consume_rivalry_events()
        for event in new_events:
            if not isinstance(event, Mapping):
                continue
            payload = {
                "tick": int(event.get("tick", tick)),
                "agent_a": str(event.get("agent_a", "")),
                "agent_b": str(event.get("agent_b", "")),
                "intensity": float(event.get("intensity", 0.0)),
                "reason": str(event.get("reason", "unknown")),
            }
            self._rivalry_event_history.append(payload)
        if len(self._rivalry_event_history) > 120:
            self._rivalry_event_history = self._rivalry_event_history[-120:]

        self._latest_conflict_snapshot = {
            "queues": dict(queue_metrics),
            "queue_history": list(self._queue_fairness_history[-20:]),
            "rivalry": rivalry_snapshot,
            "rivalry_events": list(self._rivalry_event_history[-20:]),
        }
        metrics_snapshot = adapter.relationship_metrics_snapshot()
        if metrics_snapshot:
            self._latest_relationship_metrics = dict(metrics_snapshot)
        else:
            logger.debug(
                "Telemetry relationship metrics unavailable; retaining previous snapshot",
            )
        relationship_snapshot = self._capture_relationship_snapshot(adapter)
        self._latest_relationship_updates = self._compute_relationship_updates(
            self._previous_relationship_snapshot,
            relationship_snapshot,
        )
        self._latest_relationship_snapshot = relationship_snapshot
        self._previous_relationship_snapshot = copy_relationship_snapshot(
            relationship_snapshot
        )
        self._latest_relationship_overlay = self._build_relationship_overlay()
        self._latest_relationship_summary = self._build_relationship_summary(
            relationship_snapshot, adapter
        )
        try:
            raw_embedding_metrics = adapter.embedding_allocator.metrics()
        except Exception:  # pragma: no cover - defensive guard for stub adapters
            logger.debug(
                "Telemetry embedding metrics unavailable; defaulting to empty metrics",
                exc_info=True,
            )
            raw_embedding_metrics = {}
        processed_embedding_metrics: dict[str, object] = {}
        for key, value in raw_embedding_metrics.items():
            if isinstance(value, (int, float)):
                processed_embedding_metrics[str(key)] = float(value)
            else:
                processed_embedding_metrics[str(key)] = value
        self._latest_embedding_metrics = processed_embedding_metrics
        if events is not None:
            self._latest_events = list(events)
        else:
            self._latest_events = []
        latest_social_events: list[dict[str, object]] = []
        if social_events is not None:
            for event in social_events:
                if isinstance(event, Mapping):
                    payload = dict(event)
                    self._social_event_history.append(payload)
                    latest_social_events.append(payload)
        personality_enabled = False
        try:
            personality_enabled = self.config.personality_channels_enabled()
        except Exception:  # pragma: no cover - defensive
            personality_enabled = False
        if personality_enabled or self.config.personality_profiles_enabled():
            self._latest_personality_snapshot = self._build_personality_snapshot(adapter)
        else:
            self._latest_personality_snapshot = {}
        self._capture_affordance_runtime(
            world=world,
            events=self._latest_events,
            tick=tick,
        )
        self._latest_precondition_failures = [
            dict(event)
            for event in self._latest_events
            if isinstance(event, Mapping)
            and str(event.get("event")) == "affordance_precondition_fail"
        ]
        self._process_narrations(
            self._latest_events,
            latest_social_events,
            self._latest_relationship_updates,
            int(tick),
        )
        for subscriber in self._event_subscribers:
            subscriber(list(self._latest_events))
        if policy_snapshot is not None:
            self._latest_policy_snapshot = {
                str(agent): dict(data)
                for agent, data in policy_snapshot.items()
                if isinstance(data, Mapping)
            }
        else:
            self._latest_policy_snapshot = {}
        if possessed_agents is not None:
            self._ingest_possessed_agents(possessed_agents)
        self._latest_job_snapshot = {
            agent_id: {
                "job_id": snapshot.job_id,
                "on_shift": snapshot.on_shift,
                "wallet": snapshot.wallet,
                "lateness_counter": snapshot.lateness_counter,
                "wages_earned": snapshot.inventory.get("wages_earned", 0),
                "meals_cooked": snapshot.inventory.get("meals_cooked", 0),
                "meals_consumed": snapshot.inventory.get("meals_consumed", 0),
                "basket_cost": snapshot.inventory.get("basket_cost", 0.0),
                "shift_state": snapshot.shift_state,
                "attendance_ratio": snapshot.attendance_ratio,
                "late_ticks_today": snapshot.late_ticks_today,
                "absent_shifts_7d": snapshot.absent_shifts_7d,
                "wages_withheld": snapshot.wages_withheld,
                "exit_pending": snapshot.exit_pending,
                "needs": {
                    str(need): float(value)
                    for need, value in snapshot.needs.items()
                },
            }
            for agent_id, snapshot in adapter.agent_snapshots_view().items()
        }
        self._latest_economy_snapshot = {
            object_id: {
                "type": obj.object_type,
                "stock": dict(obj.stock),
            }
            for object_id, obj in raw_world.objects.items()
        }
        if hasattr(raw_world, "economy_settings"):
            self._latest_economy_settings = raw_world.economy_settings()
        else:
            self._latest_economy_settings = {
                str(key): float(value) for key, value in self.config.economy.items()
            }
        if hasattr(raw_world, "active_price_spikes"):
            self._latest_price_spikes = raw_world.active_price_spikes()
        else:
            self._latest_price_spikes = {}
        if hasattr(raw_world, "utility_snapshot"):
            self._latest_utilities = raw_world.utility_snapshot()
        else:
            self._latest_utilities = {"power": True, "water": True}
        if hasattr(raw_world, "employment_queue_snapshot"):
            self._latest_employment_metrics = raw_world.employment_queue_snapshot()
        else:
            self._latest_employment_metrics = {}
        if reward_breakdown is not None:
            self._latest_reward_breakdown = {
                agent: dict(components) for agent, components in reward_breakdown.items()
            }
        else:
            self._latest_reward_breakdown = {}
        manifest_getter = getattr(world, "affordance_manifest_metadata", None)
        if callable(manifest_getter):
            manifest_meta = manifest_getter() or {}
            self._latest_affordance_manifest = dict(manifest_meta)
        else:
            self._latest_affordance_manifest = {}
        if kpi_history:
            self._update_kpi_history(adapter)
            self._kpi_history.setdefault("queue_rotation_events", []).append(
                fairness_delta["rotation_events"]
            )
            self._kpi_history.setdefault("queue_ghost_step_events", []).append(
                fairness_delta["ghost_step_events"]
            )

        if stability_inputs is not None:
            self._latest_stability_inputs = {
                "hunger_levels": dict(stability_inputs.get("hunger_levels", {}) or {}),
                "option_switch_counts": dict(
                    stability_inputs.get("option_switch_counts", {}) or {}
                ),
                "reward_samples": {
                    agent: float(value)
                    for agent, value in ((stability_inputs.get("reward_samples") or {}).items())
                },
            }

        if isinstance(perturbations, Mapping):
            self._latest_perturbations = normalize_perturbations_payload(perturbations)

        if policy_identity is not None:
            self.update_policy_identity(policy_identity)

        latest_reward_breakdown = self.latest_reward_breakdown()
        latest_stability_metrics = self.latest_stability_metrics()
        latest_stability_alerts = self.latest_stability_alerts()
        latest_stability_inputs = self.latest_stability_inputs()
        latest_promotion_state = self.latest_promotion_state()
        latest_policy_identity = self.latest_policy_identity()
        latest_anneal_status = self.latest_anneal_status()
        latest_kpi_history = self.kpi_history()
        latest_perturbations = self.latest_perturbations()

        aggregated_events = list(
            self._aggregator.collect_tick(
                tick=tick,
                world=world,
                observations=observations,
                rewards=rewards,
                events=self._latest_events,
                policy_snapshot=self._latest_policy_snapshot,
                kpi_history=kpi_history,
                reward_breakdown=latest_reward_breakdown,
                stability_inputs=latest_stability_inputs,
                perturbations=latest_perturbations,
                policy_identity=latest_policy_identity or {},
                possessed_agents=possessed_agents or (),
                social_events=self._latest_events,
                runtime_variant=self._runtime_variant,
                queue_metrics=self._latest_queue_metrics or {},
                embedding_metrics=self._latest_embedding_metrics or {},
                employment_metrics=self._latest_employment_metrics or {},
                conflict_snapshot=self.latest_conflict_snapshot(),
                relationship_metrics=self._latest_relationship_metrics or {},
                relationship_snapshot=self._latest_relationship_snapshot,
                relationship_updates=self._latest_relationship_updates,
                relationship_overlay=self._latest_relationship_overlay,
                narrations=self._latest_narrations,
                job_snapshot=self._latest_job_snapshot,
                economy_snapshot=self._latest_economy_snapshot,
                economy_settings=self._latest_economy_settings,
                price_spikes=self._latest_price_spikes,
                utilities=self._latest_utilities,
                affordance_manifest=self._latest_affordance_manifest,
                stability_metrics=latest_stability_metrics,
                stability_alerts=latest_stability_alerts,
                promotion=latest_promotion_state,
                anneal_status=latest_anneal_status,
                kpi_history_payload=latest_kpi_history,
            )
        )
        transformed_events = self._transform_pipeline.process(aggregated_events)
        for event in transformed_events:
            self._enqueue_stream_payload(event.payload, tick=int(event.tick))

    def latest_queue_metrics(self) -> dict[str, int] | None:
        """Expose the most recent queue-related telemetry counters."""
        if self._latest_queue_metrics is None:
            return None
        return dict(self._latest_queue_metrics)

    def latest_queue_history(self) -> list[dict[str, object]]:
        if not self._queue_fairness_history:
            return []
        return [dict(entry) for entry in self._queue_fairness_history[-50:]]

    def latest_rivalry_events(self) -> list[dict[str, object]]:
        if not self._rivalry_event_history:
            return []
        return [dict(entry) for entry in self._rivalry_event_history[-50:]]

    def latest_affordance_runtime(self) -> dict[str, object]:
        runtime = self._latest_affordance_runtime
        running_section = runtime.get("running") or {}
        event_counts = dict(runtime.get("event_counts", {}))
        for key in ("start", "finish", "fail", "precondition_fail"):
            event_counts.setdefault(key, 0)
        return {
            "tick": int(runtime.get("tick", 0)),
            "running_count": int(runtime.get("running_count", 0)),
            "running": {
                str(object_id): dict(entry)
                for object_id, entry in running_section.items()
            },
            "active_reservations": dict(runtime.get("active_reservations", {})),
            "event_counts": event_counts,
        }

    def update_anneal_status(self, status: Mapping[str, object] | None) -> None:
        """Record the latest anneal status payload for observer dashboards."""
        self._latest_anneal_status = dict(status) if status else None

    def kpi_history(self) -> dict[str, list[float]]:
        return {key: list(values) for key, values in self._kpi_history.items()}

    def latest_conflict_snapshot(self) -> dict[str, object]:
        """Return the conflict-focused telemetry payload (queues + rivalry)."""

        snapshot = dict(self._latest_conflict_snapshot)
        queues = snapshot.get("queues")
        if isinstance(queues, dict):
            snapshot["queues"] = dict(queues)
        history = snapshot.get("queue_history")
        if isinstance(history, list):
            snapshot["queue_history"] = [
                {
                    "tick": int(entry.get("tick", 0)),
                    "delta": dict(entry.get("delta", {})),
                    "totals": dict(entry.get("totals", {})),
                }
                for entry in history
                if isinstance(entry, Mapping)
            ]
        events = snapshot.get("rivalry_events")
        if isinstance(events, list):
            snapshot["rivalry_events"] = [
                {
                    "tick": int(entry.get("tick", 0)),
                    "agent_a": str(entry.get("agent_a", "")),
                    "agent_b": str(entry.get("agent_b", "")),
                    "intensity": float(entry.get("intensity", 0.0)),
                    "reason": str(entry.get("reason", "unknown")),
                }
                for entry in events
                if isinstance(entry, Mapping)
            ]
        return snapshot

    def latest_affordance_manifest(self) -> dict[str, object]:
        """Expose the most recent affordance manifest metadata."""

        return dict(self._latest_affordance_manifest)

    def latest_reward_breakdown(self) -> dict[str, dict[str, float]]:
        return {
            agent: dict(components) for agent, components in self._latest_reward_breakdown.items()
        }

    def latest_social_events(self) -> list[dict[str, object]]:
        return [dict(event) for event in self._social_event_history]

    def latest_personality_snapshot(self) -> dict[str, object]:
        return copy.deepcopy(self._latest_personality_snapshot)

    def latest_relationship_summary(self) -> dict[str, object]:
        return dict(self._latest_relationship_summary)

    def latest_stability_inputs(self) -> dict[str, object]:
        if not self._latest_stability_inputs:
            return {}
        result: dict[str, object] = {}
        hunger = self._latest_stability_inputs.get("hunger_levels")
        if isinstance(hunger, dict):
            result["hunger_levels"] = {str(agent): float(value) for agent, value in hunger.items()}
        option_counts = self._latest_stability_inputs.get("option_switch_counts")
        if isinstance(option_counts, dict):
            result["option_switch_counts"] = {
                str(agent): int(value) for agent, value in option_counts.items()
            }
        reward_samples = self._latest_stability_inputs.get("reward_samples")
        if isinstance(reward_samples, dict):
            result["reward_samples"] = {
                str(agent): float(value) for agent, value in reward_samples.items()
            }
        return result

    def _ingest_stability_metrics(self, metrics: Mapping[str, object]) -> None:
        self._latest_stability_metrics = dict(metrics)

    def latest_stability_metrics(self) -> dict[str, object]:
        return dict(self._latest_stability_metrics)

    def latest_promotion_state(self) -> dict[str, object] | None:
        metrics = self._latest_stability_metrics
        promotion_state = metrics.get("promotion_state") if isinstance(metrics, dict) else None
        if promotion_state is None:
            return None
        if isinstance(promotion_state, Mapping):
            return dict(promotion_state)
        return None

    def _append_console_audit(self, payload: Mapping[str, Any]) -> None:
        try:
            self._console_audit_path.parent.mkdir(parents=True, exist_ok=True)
            with self._console_audit_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload) + "\n")
        except Exception:  # pragma: no cover - audit is best-effort
            logger.exception("Failed to append console audit entry")

    def latest_stability_alerts(self) -> list[str]:
        metrics = self.latest_stability_metrics()
        alerts = metrics.get("alerts")
        if isinstance(alerts, list):
            return [str(alert) for alert in alerts]
        return []

    def latest_perturbations(self) -> dict[str, object]:
        return {
            "active": {
                event_id: dict(data)
                for event_id, data in self._latest_perturbations.get("active", {}).items()
            },
            "pending": [dict(entry) for entry in self._latest_perturbations.get("pending", [])],
            "cooldowns": {
                "spec": dict(self._latest_perturbations.get("cooldowns", {}).get("spec", {})),
                "agents": dict(self._latest_perturbations.get("cooldowns", {}).get("agents", {})),
            },
        }

    def update_policy_identity(self, identity: Mapping[str, object] | None) -> None:
        if identity is None:
            self._latest_policy_identity = None
            return
        payload = {
            "config_id": identity.get("config_id", self.config.config_id),
            "policy_hash": identity.get("policy_hash"),
            "observation_variant": identity.get("observation_variant"),
            "anneal_ratio": identity.get("anneal_ratio"),
        }
        self._latest_policy_identity = payload

    def latest_policy_identity(self) -> dict[str, object] | None:
        if self._latest_policy_identity is None:
            return None
        return dict(self._latest_policy_identity)

    def _ingest_policy_metadata(self, payload: Mapping[str, Any]) -> None:
        metadata_payload = payload.get("metadata")
        if not isinstance(metadata_payload, Mapping):
            self._latest_policy_metadata_event = None
            return
        metadata_copy = copy.deepcopy(dict(metadata_payload))
        option_counts = metadata_copy.get("option_switch_counts")
        if isinstance(option_counts, Mapping):
            metadata_copy["option_switch_counts"] = {
                str(agent): int(count)
                for agent, count in sorted(option_counts.items())
            }
        possessed_payload = metadata_copy.get("possessed_agents")
        if isinstance(possessed_payload, Iterable) and not isinstance(
            possessed_payload, (str, bytes)
        ):
            agents = sorted({str(agent) for agent in possessed_payload})
            metadata_copy["possessed_agents"] = agents
        event_payload: dict[str, object] = {
            "tick": int(payload.get("tick", -1)),
            "provider": str(payload.get("provider", "")),
            "metadata": metadata_copy,
        }
        self._latest_policy_metadata_event = copy.deepcopy(event_payload)
        identity_payload = metadata_copy.get("identity")
        if isinstance(identity_payload, Mapping):
            self.update_policy_identity(identity_payload)

    def latest_policy_metadata(self) -> dict[str, object] | None:
        if self._latest_policy_metadata_event is None:
            return None
        return copy.deepcopy(self._latest_policy_metadata_event)

    def _ingest_policy_anneal(self, payload: Mapping[str, Any]) -> None:
        event_payload: dict[str, object] = {
            "tick": int(payload.get("tick", -1)),
            "provider": str(payload.get("provider", "")),
        }
        if "ratio" in payload:
            ratio_value = payload.get("ratio")
            if isinstance(ratio_value, (int, float)):
                event_payload["ratio"] = float(ratio_value)
            elif ratio_value is None:
                event_payload["ratio"] = None
        context_payload = payload.get("context")
        if isinstance(context_payload, Mapping):
            event_payload["context"] = copy.deepcopy(dict(context_payload))
        else:
            event_payload["context"] = {}
        self._latest_policy_anneal_event = copy.deepcopy(event_payload)

    def latest_policy_anneal(self) -> dict[str, object] | None:
        if self._latest_policy_anneal_event is None:
            return None
        return copy.deepcopy(self._latest_policy_anneal_event)

    def _ingest_snapshot_migrations(self, applied: Iterable[str]) -> None:
        self._latest_snapshot_migrations = [str(item) for item in applied]

    def latest_snapshot_migrations(self) -> list[str]:
        return list(self._latest_snapshot_migrations)

    def latest_policy_snapshot(self) -> dict[str, dict[str, object]]:
        return {agent: dict(data) for agent, data in self._latest_policy_snapshot.items()}

    def latest_anneal_status(self) -> dict[str, object] | None:
        if self._latest_anneal_status is None:
            return None
        return dict(self._latest_anneal_status)

    def latest_relationship_metrics(self) -> dict[str, object] | None:
        """Expose relationship churn payload captured during publish."""
        if self._latest_relationship_metrics is None:
            return None
        payload = dict(self._latest_relationship_metrics)
        history = payload.get("history")
        if isinstance(history, list):
            payload["history"] = [dict(entry) for entry in history]
        return payload

    def latest_relationship_snapshot(self) -> dict[str, dict[str, dict[str, float]]]:
        return copy_relationship_snapshot(self._latest_relationship_snapshot)

    def latest_relationship_updates(self) -> list[dict[str, object]]:
        return [dict(update) for update in self._latest_relationship_updates]

    def update_relationship_metrics(self, payload: dict[str, object]) -> None:
        """Allow external callers to seed the latest relationship metrics."""
        self._latest_relationship_metrics = dict(payload)

    def latest_relationship_overlay(self) -> dict[str, list[dict[str, object]]]:
        return {
            agent: [dict(item) for item in entries]
            for agent, entries in self._latest_relationship_overlay.items()
        }

    def latest_narrations(self) -> list[dict[str, object]]:
        """Expose narration entries emitted during the latest publish call."""

        return [dict(entry) for entry in self._latest_narrations]

    def latest_embedding_metrics(self) -> dict[str, float] | None:
        """Expose embedding allocator counters."""
        if self._latest_embedding_metrics is None:
            return None
        return dict(self._latest_embedding_metrics)

    def latest_events(self) -> Iterable[dict[str, object]]:
        """Return the most recent event batch."""
        return getattr(self, "_latest_events", [])

    def latest_narration_state(self) -> dict[str, object]:
        """Return the narration limiter state for snapshot export."""

        return self._narration_limiter.export_state()

    def current_tick(self) -> int:
        """Return the most recent tick processed by telemetry."""

        return int(self._current_tick)

    def emit_manual_narration(
        self,
        *,
        message: str,
        category: str = "operator_story",
        tick: int | None = None,
        priority: bool = False,
        data: Mapping[str, object] | None = None,
        dedupe_key: str | None = None,
    ) -> dict[str, object] | None:
        """Inject an operator narration entry respecting rate limits."""

        if not isinstance(message, str) or not message.strip():
            raise ValueError("narration message must be a non-empty string")

        message_text = message.strip()
        category_name = str(category or "operator_story").strip() or "operator_story"
        target_tick = int(self._current_tick if tick is None else tick)
        self._narration_limiter.begin_tick(target_tick)
        allowed = self._narration_limiter.allow(
            category_name,
            message=message_text,
            priority=bool(priority),
            dedupe_key=dedupe_key,
        )
        if not allowed:
            return None

        entry: dict[str, object] = {
            "tick": target_tick,
            "category": category_name,
            "message": message_text,
            "priority": bool(priority),
        }
        if data:
            if not isinstance(data, Mapping):
                raise ValueError("narration data payload must be a mapping")
            entry["data"] = {str(key): value for key, value in data.items()}
        if dedupe_key is not None:
            entry["dedupe_key"] = str(dedupe_key)

        with self._manual_narration_lock:
            self._pending_manual_narrations.append(dict(entry))

        self._latest_narrations.append(dict(entry))
        return entry

    def _consume_manual_narrations(self) -> list[dict[str, object]]:
        with self._manual_narration_lock:
            if not self._pending_manual_narrations:
                return []
            entries = [dict(entry) for entry in self._pending_manual_narrations]
            self._pending_manual_narrations.clear()
            return entries

    def register_event_subscriber(
        self, subscriber: Callable[[list[dict[str, object]]], None]
    ) -> None:
        """Register a callback to receive each tick's event batch."""
        self._event_subscribers.append(subscriber)

    def latest_job_snapshot(self) -> dict[str, dict[str, object]]:
        return getattr(self, "_latest_job_snapshot", {})

    def latest_economy_snapshot(self) -> dict[str, dict[str, object]]:
        return getattr(self, "_latest_economy_snapshot", {})

    def latest_economy_settings(self) -> dict[str, float]:
        return dict(self._latest_economy_settings)

    def latest_price_spikes(self) -> dict[str, dict[str, object]]:
        return {
            event_id: {
                "magnitude": float(data.get("magnitude", 0.0)),
                "targets": list(data.get("targets", [])),
            }
            for event_id, data in self._latest_price_spikes.items()
        }

    def latest_utilities(self) -> dict[str, bool]:
        return {key: bool(value) for key, value in self._latest_utilities.items()}

    def latest_employment_metrics(self) -> dict[str, object]:
        return dict(getattr(self, "_latest_employment_metrics", {}))

    def schema(self) -> str:
        return self.schema_version

    @property
    def event_dispatcher(self) -> TelemetryEventDispatcher:
        """Expose the event dispatcher used for streaming telemetry."""

        return self._event_dispatcher

    def emit_event(self, name: str, payload: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        """Forward an event through the internal dispatcher."""

        return self._event_dispatcher.emit_event(name, payload)

    def _handle_event(self, name: str, payload: Mapping[str, Any]) -> None:
        """Internal subscriber that bridges events back into publisher behaviour."""

        if name == "loop.tick":
            self._ingest_loop_tick(**payload)
            return
        if name == "loop.health":
            self._ingest_health_metrics(payload)
            return
        if name == "loop.failure":
            self._ingest_loop_failure(payload)
            return
        if name == "policy.metadata":
            self._ingest_policy_metadata(payload)
            return
        if name == "policy.possession":
            agents = payload.get("agents", payload.get("possessed_agents", ()))
            if isinstance(agents, Iterable):
                self._ingest_possessed_agents(agents)
            return
        if name == "policy.anneal.update":
            self._ingest_policy_anneal(payload)
            return
        if name == "console.result":
            result_payload = dict(payload)
            result_kwargs = {
                "name": str(result_payload.get("name", "")),
                "status": str(result_payload.get("status", "ok")),
                "result": dict(result_payload.get("result", {})) if isinstance(result_payload.get("result"), Mapping) else None,
                "error": dict(result_payload.get("error", {})) if isinstance(result_payload.get("error"), Mapping) else None,
                "cmd_id": result_payload.get("cmd_id"),
                "issuer": result_payload.get("issuer"),
                "tick": result_payload.get("tick"),
                "latency_ms": result_payload.get("latency_ms"),
            }
            console_result = ConsoleCommandResult(**result_kwargs)
            self._ingest_console_results([console_result])
            self._latest_events.append({"type": "console.result", "payload": result_payload})
            if len(self._latest_events) > 128:
                self._latest_events = self._latest_events[-128:]
            return
        if name == "stability.metrics":
            self._ingest_stability_metrics(payload)
            return
        if name == "telemetry.snapshot.migrations":
            applied = payload.get("applied")
            if isinstance(applied, Iterable):
                self._ingest_snapshot_migrations(applied)
            return
        # Default: append to event cache for observers.
        self._latest_events.append({"type": name, "payload": dict(payload)})
        if len(self._latest_events) > 128:
            self._latest_events = self._latest_events[-128:]

    def _capture_relationship_snapshot(
        self,
        world: WorldState | WorldRuntimeAdapterProtocol,
    ) -> dict[str, dict[str, dict[str, float]]]:
        adapter = ensure_world_adapter(world)
        raw = adapter.relationships_snapshot() or {}
        if not isinstance(raw, dict):
            return {}
        normalised: dict[str, dict[str, dict[str, float]]] = {}
        for owner, ties in raw.items():
            if not isinstance(ties, dict):
                continue
            normalised[owner] = {
                other: {
                    "trust": float(values.get("trust", 0.0)),
                    "familiarity": float(values.get("familiarity", 0.0)),
                    "rivalry": float(values.get("rivalry", 0.0)),
                }
                for other, values in ties.items()
                if isinstance(values, dict)
            }
        return normalised

    def _compute_relationship_updates(
        self,
        previous: dict[str, dict[str, dict[str, float]]],
        current: dict[str, dict[str, dict[str, float]]],
    ) -> list[dict[str, object]]:
        updates: list[dict[str, object]] = []
        for owner, ties in current.items():
            prev_ties = previous.get(owner, {})
            for other, metrics in ties.items():
                prev_metrics = prev_ties.get(other)
                if prev_metrics is None:
                    updates.append(
                        {
                            "owner": owner,
                            "other": other,
                            "trust": metrics["trust"],
                            "familiarity": metrics["familiarity"],
                            "rivalry": metrics["rivalry"],
                            "status": "added",
                            "delta": dict(metrics),
                        }
                    )
                else:
                    delta_trust = metrics["trust"] - prev_metrics.get("trust", 0.0)
                    delta_fam = metrics["familiarity"] - prev_metrics.get("familiarity", 0.0)
                    delta_riv = metrics["rivalry"] - prev_metrics.get("rivalry", 0.0)
                    if any(abs(delta) > 1e-6 for delta in (delta_trust, delta_fam, delta_riv)):
                        updates.append(
                            {
                                "owner": owner,
                                "other": other,
                                "trust": metrics["trust"],
                                "familiarity": metrics["familiarity"],
                                "rivalry": metrics["rivalry"],
                                "status": "updated",
                                "delta": {
                                    "trust": delta_trust,
                                    "familiarity": delta_fam,
                                    "rivalry": delta_riv,
                                },
                            }
                        )
            for other, prev_metrics in prev_ties.items():
                if other not in ties:
                    updates.append(
                        {
                            "owner": owner,
                            "other": other,
                            "trust": 0.0,
                            "familiarity": 0.0,
                            "rivalry": 0.0,
                            "status": "removed",
                            "delta": {
                                "trust": -prev_metrics.get("trust", 0.0),
                                "familiarity": -prev_metrics.get("familiarity", 0.0),
                                "rivalry": -prev_metrics.get("rivalry", 0.0),
                            },
                        }
                    )
        for owner, ties in previous.items():
            if owner not in current:
                for other, prev_metrics in ties.items():
                    updates.append(
                        {
                            "owner": owner,
                            "other": other,
                            "trust": 0.0,
                            "familiarity": 0.0,
                            "rivalry": 0.0,
                            "status": "removed",
                            "delta": {
                                "trust": -prev_metrics.get("trust", 0.0),
                                "familiarity": -prev_metrics.get("familiarity", 0.0),
                                "rivalry": -prev_metrics.get("rivalry", 0.0),
                            },
                        }
                    )
        return updates

    def _build_relationship_overlay(self) -> dict[str, list[dict[str, object]]]:
        overlay: dict[str, list[dict[str, object]]] = {}
        delta_map: dict[tuple[str, str], dict[str, float]] = {}
        for entry in self._latest_relationship_updates:
            owner = str(entry.get("owner", ""))
            other = str(entry.get("other", ""))
            if not owner or not other:
                continue
            delta = entry.get("delta")
            if isinstance(delta, Mapping):
                delta_map[(owner, other)] = {
                    "trust": float(delta.get("trust", 0.0)),
                    "familiarity": float(delta.get("familiarity", 0.0)),
                    "rivalry": float(delta.get("rivalry", 0.0)),
                }
        for owner, ties in self._latest_relationship_snapshot.items():
            ranked = sorted(
                ties.items(),
                key=lambda item: item[1].get("trust", 0.0),
                reverse=True,
            )
            summaries: list[dict[str, object]] = []
            for other, metrics in ranked[:3]:
                delta = delta_map.get((owner, other), {})
                summaries.append(
                    {
                        "owner": owner,
                        "other": other,
                        "trust": float(metrics.get("trust", 0.0)),
                        "familiarity": float(metrics.get("familiarity", 0.0)),
                        "rivalry": float(metrics.get("rivalry", 0.0)),
                        "delta_trust": float(delta.get("trust", 0.0)),
                        "delta_familiarity": float(delta.get("familiarity", 0.0)),
                        "delta_rivalry": float(delta.get("rivalry", 0.0)),
                    }
                )
            if summaries:
                overlay[owner] = summaries
        return overlay

    def _build_relationship_summary(
        self,
        snapshot: Mapping[str, Mapping[str, Mapping[str, float]]],
        world: WorldState | WorldRuntimeAdapterProtocol,
    ) -> dict[str, object]:
        adapter = ensure_world_adapter(world)
        summary: dict[str, object] = {}
        max_entries = 3
        for owner, ties in snapshot.items():
            ranked_friends = sorted(
                ties.items(),
                key=lambda item: item[1].get("trust", 0.0)
                + item[1].get("familiarity", 0.0),
                reverse=True,
            )
            friend_payload = [
                {
                    "agent": other,
                    "trust": float(metrics.get("trust", 0.0)),
                    "familiarity": float(metrics.get("familiarity", 0.0)),
                    "rivalry": float(metrics.get("rivalry", 0.0)),
                }
                for other, metrics in ranked_friends[:max_entries]
            ]
            rivals: list[dict[str, object]] = []
            try:
                top_rivals = adapter.rivalry_top(owner, max_entries)
            except Exception:  # pragma: no cover - defensive
                top_rivals = []
            for other, value in top_rivals:
                rivals.append({"agent": other, "rivalry": float(value)})
            summary[owner] = {
                "top_friends": friend_payload,
                "top_rivals": rivals,
            }
        summary["churn"] = dict(self._latest_relationship_metrics or {})
        return summary

    def _build_personality_snapshot(
        self,
        world: WorldState | WorldRuntimeAdapterProtocol,
    ) -> dict[str, object]:
        adapter = ensure_world_adapter(world)
        snapshot = {
            agent_id: copy.deepcopy(agent)
            for agent_id, agent in adapter.agent_snapshots_view().items()
        }
        payload: dict[str, object] = {}
        for agent_id, agent in snapshot.items():
            profile_name = str(getattr(agent, "personality_profile", "") or "balanced")
            personality = getattr(agent, "personality", None)
            traits = {
                "extroversion": float(getattr(personality, "extroversion", 0.0)),
                "forgiveness": float(getattr(personality, "forgiveness", 0.0)),
                "ambition": float(getattr(personality, "ambition", 0.0)),
            }
            entry: dict[str, object] = {
                "profile": profile_name,
                "traits": traits,
            }
            try:
                profile = PersonalityProfiles.get(profile_name)
            except KeyError:
                profile = None
            if profile is not None:
                entry["multipliers"] = {
                    "needs": dict(profile.need_multipliers),
                    "rewards": dict(profile.reward_bias),
                    "behaviour": dict(profile.behaviour_bias),
                }
            payload[str(agent_id)] = entry
        return payload

    def _emit_personality_event_narrations(
        self,
        events: Iterable[Mapping[str, object]],
        tick: int,
    ) -> None:
        if (
            not self._personality_narration_cfg.enabled
            or not self._latest_personality_snapshot
        ):
            return
        chat_threshold = float(self._personality_narration_cfg.chat_extroversion_threshold)
        chat_priority = float(self._personality_narration_cfg.chat_priority_threshold)
        quality_threshold = float(self._personality_narration_cfg.chat_quality_threshold)
        tolerance_threshold = float(
            self._personality_narration_cfg.conflict_tolerance_threshold
        )
        for event in events:
            etype = str(event.get("type", ""))
            if etype == "chat_success":
                speaker = str(event.get("speaker") or "")
                if not speaker:
                    continue
                listener = str(event.get("listener") or "")
                profile = self._latest_personality_snapshot.get(speaker)
                if not isinstance(profile, Mapping):
                    continue
                traits = profile.get("traits", {})
                try:
                    extroversion = float(traits.get("extroversion", 0.0))
                except (TypeError, ValueError):
                    extroversion = 0.0
                if extroversion < chat_threshold:
                    continue
                quality = float(event.get("quality", 0.0) or 0.0)
                if quality < quality_threshold:
                    continue
                message = (
                    f"{speaker}'s extroversion ({extroversion:+.2f}) sparked a high-energy chat"
                )
                if listener:
                    message += f" with {listener}"
                if quality:
                    message += f" (quality {quality:.2f})"
                message += "."
                dedupe_key = f"personality_chat:{speaker}:{listener}"
                priority = extroversion >= chat_priority
                if self._narration_limiter.allow(
                    "personality_event",
                    message=message,
                    priority=priority,
                    dedupe_key=dedupe_key,
                ):
                    self._latest_narrations.append(
                        {
                            "tick": int(tick),
                            "category": "personality_event",
                            "message": message,
                            "priority": priority,
                            "data": {
                                "agent": speaker,
                                "listener": listener,
                                "trait": "extroversion",
                                "value": extroversion,
                                "quality": quality,
                            },
                            "dedupe_key": dedupe_key,
                        }
                    )
            elif etype == "rivalry_avoidance":
                agent = str(event.get("agent") or "")
                if not agent:
                    continue
                profile = self._latest_personality_snapshot.get(agent)
                if not isinstance(profile, Mapping):
                    continue
                multipliers = profile.get("multipliers", {})
                behaviour = {}
                if isinstance(multipliers, Mapping):
                    behaviour = multipliers.get("behaviour", {})
                try:
                    tolerance = float(behaviour.get("conflict_tolerance", 1.0))
                except (TypeError, ValueError):
                    tolerance = 1.0
                if tolerance >= tolerance_threshold:
                    continue
                location = str(event.get("object") or "the area")
                reason = str(event.get("reason") or "conflict avoidance")
                message = (
                    f"{agent} stayed composed (conflict tolerance {tolerance:.2f}) "
                    "and avoided trouble"
                )
                if location:
                    message += f" near {location}"
                if reason:
                    message += f" ({reason})"
                message += "."
                dedupe_key = f"personality_avoid:{agent}:{location}"
                if self._narration_limiter.allow(
                    "personality_event",
                    message=message,
                    priority=False,
                    dedupe_key=dedupe_key,
                ):
                    self._latest_narrations.append(
                        {
                            "tick": int(tick),
                            "category": "personality_event",
                            "message": message,
                            "priority": False,
                            "data": {
                                "agent": agent,
                                "trait": "conflict_tolerance",
                                "value": tolerance,
                                "location": location,
                                "reason": reason,
                            },
                            "dedupe_key": dedupe_key,
                        }
                    )

    def _process_narrations(
        self,
        events: Iterable[dict[str, object]],
        social_events: Iterable[Mapping[str, object]] | None,
        relationship_updates: Iterable[Mapping[str, object]],
        tick: int,
    ) -> None:
        social_events_snapshot = list(social_events or [])
        relationship_updates_snapshot = list(relationship_updates)
        for event in events:
            event_name = event.get("event")
            if event_name == "queue_conflict":
                self._handle_queue_conflict_narration(event, tick)
            elif event_name == "shower_power_outage":
                self._handle_shower_power_outage_narration(event, tick)
            elif event_name == "shower_complete":
                self._handle_shower_complete_narration(event, tick)
            elif event_name == "sleep_complete":
                self._handle_sleep_complete_narration(event, tick)
        self._emit_relationship_friendship_narrations(
            relationship_updates_snapshot, tick
        )
        self._emit_relationship_rivalry_narrations(tick)
        self._emit_social_alert_narrations(social_events_snapshot, tick)
        self._emit_personality_event_narrations(social_events_snapshot, tick)

    def _emit_relationship_friendship_narrations(
        self,
        updates: Iterable[Mapping[str, object]],
        tick: int,
    ) -> None:
        trust_threshold = float(self._relationship_narration_cfg.friendship_trust_threshold)
        delta_threshold = float(self._relationship_narration_cfg.friendship_delta_threshold)
        priority_threshold = float(
            self._relationship_narration_cfg.friendship_priority_threshold
        )
        for update in updates:
            owner = str(update.get("owner", ""))
            other = str(update.get("other", ""))
            if not owner or not other:
                continue
            status = str(update.get("status", ""))
            trust = float(update.get("trust", 0.0) or 0.0)
            familiarity = float(update.get("familiarity", 0.0) or 0.0)
            delta = update.get("delta")
            delta_trust = float(delta.get("trust", 0.0)) if isinstance(delta, Mapping) else 0.0
            delta_fam = float(delta.get("familiarity", 0.0)) if isinstance(delta, Mapping) else 0.0
            new_tie = status == "added"
            if not new_tie and trust < trust_threshold and delta_trust < delta_threshold:
                continue
            message = (
                f"{owner} bonded with {other}: trust {trust:.2f}, familiarity {familiarity:.2f}."
            )
            dedupe_key = f"relationship_friendship:{owner}:{other}"
            priority = new_tie or trust >= priority_threshold
            if self._narration_limiter.allow(
                RELATIONSHIP_FRIENDSHIP_EVENT,
                message=message,
                priority=priority,
                dedupe_key=dedupe_key,
            ):
                self._latest_narrations.append(
                    {
                        "tick": int(tick),
                        "category": RELATIONSHIP_FRIENDSHIP_EVENT,
                        "message": message,
                        "priority": priority,
                        "data": {
                            "owner": owner,
                            "other": other,
                            "status": status,
                            "trust": trust,
                            "familiarity": familiarity,
                            "delta_trust": delta_trust,
                            "delta_familiarity": delta_fam,
                        },
                    }
                )

    def _emit_relationship_rivalry_narrations(self, tick: int) -> None:
        summary = self._latest_relationship_summary
        if not isinstance(summary, Mapping):
            return
        avoid_threshold = float(self._relationship_narration_cfg.rivalry_avoid_threshold)
        escalation_threshold = float(
            self._relationship_narration_cfg.rivalry_escalation_threshold
        )
        for owner, payload in summary.items():
            if owner == "churn" or not isinstance(payload, Mapping):
                continue
            rivals = payload.get("top_rivals", [])
            if not isinstance(rivals, Iterable):
                continue
            for rival_entry in rivals:
                if not isinstance(rival_entry, Mapping):
                    continue
                rival = str(rival_entry.get("agent", ""))
                if not rival:
                    continue
                rivalry_value = float(rival_entry.get("rivalry", 0.0) or 0.0)
                if rivalry_value < avoid_threshold:
                    continue
                reason = "avoid_threshold" if rivalry_value < escalation_threshold else "escalation"
                priority = rivalry_value >= escalation_threshold
                message = (
                    f"Rivalry between {owner} and {rival} is at {rivalry_value:.2f} ({reason})."
                )
                dedupe_key = f"relationship_rivalry:{owner}:{rival}"
                if self._narration_limiter.allow(
                    RELATIONSHIP_RIVALRY_EVENT,
                    message=message,
                    priority=priority,
                    dedupe_key=dedupe_key,
                ):
                    self._latest_narrations.append(
                        {
                            "tick": int(tick),
                            "category": RELATIONSHIP_RIVALRY_EVENT,
                            "message": message,
                            "priority": priority,
                            "data": {
                                "owner": owner,
                                "rival": rival,
                                "rivalry": rivalry_value,
                                "threshold": reason,
                            },
                        }
                    )

    def _emit_social_alert_narrations(
        self,
        events: Iterable[Mapping[str, object]],
        tick: int,
    ) -> None:
        for event in events:
            event_type = str(event.get("type", ""))
            if event_type not in {"chat_failure", "rivalry_avoidance"}:
                continue
            if event_type == "chat_failure":
                speaker = str(event.get("speaker", ""))
                listener = str(event.get("listener", ""))
                if not speaker or not listener:
                    continue
                message = f"Chat between {speaker} and {listener} failed."
                dedupe_key = f"social_chat_failure:{speaker}:{listener}"
                priority = False
                data = {
                    "speaker": speaker,
                    "listener": listener,
                    "quality": event.get("quality"),
                }
            else:
                agent = str(event.get("agent", ""))
                target = str(event.get("object", ""))
                if not agent:
                    continue
                message = f"{agent} avoided a rivalry interaction at {target or 'unknown'}"
                dedupe_key = f"social_rivalry_avoidance:{agent}:{target}"
                priority = True
                data = {
                    "agent": agent,
                    "object": target,
                    "reason": event.get("reason"),
                }
            if self._narration_limiter.allow(
                RELATIONSHIP_SOCIAL_ALERT_EVENT,
                message=message,
                priority=priority,
                dedupe_key=dedupe_key,
            ):
                self._latest_narrations.append(
                    {
                        "tick": int(tick),
                        "category": RELATIONSHIP_SOCIAL_ALERT_EVENT,
                        "message": message,
                        "priority": priority,
                        "data": data,
                    }
                )

    def _handle_queue_conflict_narration(
        self,
        event: dict[str, object],
        tick: int,
    ) -> None:
        actor = str(event.get("actor", ""))
        rival = str(event.get("rival", ""))
        if not actor or not rival:
            return
        object_id = str(event.get("object_id", "")) or "queue"
        reason = str(event.get("reason", "unknown"))
        intensity = float(event.get("intensity", 0.0) or 0.0)
        queue_length = int(event.get("queue_length", 0))
        priority = reason == "ghost_step"
        dedupe_key = ":".join(
            [
                "queue_conflict",
                object_id,
                "::".join(sorted([actor, rival])),
            ]
        )
        message = (
            f"{actor} clashed with {rival} at {object_id}"
            f" (intensity {intensity:.2f}, queue {queue_length})."
        )
        if self._narration_limiter.allow(
            "queue_conflict",
            message=message,
            priority=priority,
            dedupe_key=dedupe_key,
        ):
            self._latest_narrations.append(
                {
                    "tick": int(tick),
                    "category": "queue_conflict",
                    "message": message,
                    "priority": priority,
                    "data": {
                        "actor": actor,
                        "rival": rival,
                        "object_id": object_id,
                        "reason": reason,
                        "intensity": intensity,
                        "queue_length": queue_length,
                    },
                }
            )

    def _handle_shower_power_outage_narration(
        self,
        event: dict[str, object],
        tick: int,
    ) -> None:
        object_id = str(event.get("object_id", "shower")) or "shower"
        message = f"{object_id} lost power; showers paused."
        dedupe_key = f"shower_outage:{object_id}"
        if self._narration_limiter.allow(
            "utility_outage",
            message=message,
            priority=True,
            dedupe_key=dedupe_key,
        ):
            self._latest_narrations.append(
                {
                    "tick": int(tick),
                    "category": "utility_outage",
                    "message": message,
                    "priority": True,
                    "data": {
                        "object_id": object_id,
                        "reason": "power_off",
                    },
                }
            )

    def _handle_shower_complete_narration(
        self,
        event: dict[str, object],
        tick: int,
    ) -> None:
        agent_id = str(event.get("agent_id", ""))
        object_id = str(event.get("object_id", "shower")) or "shower"
        if not agent_id:
            return
        message = f"{agent_id} finished showering at {object_id}."
        dedupe_key = f"shower_complete:{agent_id}:{object_id}"
        if self._narration_limiter.allow(
            "shower_complete",
            message=message,
            priority=False,
            dedupe_key=dedupe_key,
        ):
            self._latest_narrations.append(
                {
                    "tick": int(tick),
                    "category": "shower_complete",
                    "message": message,
                    "priority": False,
                    "data": {
                        "agent_id": agent_id,
                        "object_id": object_id,
                    },
                }
            )

    def _handle_sleep_complete_narration(
        self,
        event: dict[str, object],
        tick: int,
    ) -> None:
        agent_id = str(event.get("agent_id", ""))
        object_id = str(event.get("object_id", "bed")) or "bed"
        if not agent_id:
            return
        message = f"{agent_id} woke rested after sleeping at {object_id}."
        dedupe_key = f"sleep_complete:{agent_id}:{object_id}"
        if self._narration_limiter.allow(
            "sleep_complete",
            message=message,
            priority=False,
            dedupe_key=dedupe_key,
        ):
            self._latest_narrations.append(
                {
                    "tick": int(tick),
                    "category": "sleep_complete",
                    "message": message,
                    "priority": False,
                    "data": {
                        "agent_id": agent_id,
                        "object_id": object_id,
                    },
                }
            )

    def _update_kpi_history(
        self,
        world: WorldState | WorldRuntimeAdapterProtocol,
    ) -> None:
        adapter = ensure_world_adapter(world)
        queue_sum = float(
            self._latest_conflict_snapshot.get("queues", {}).get("intensity_sum", 0.0)
        )
        lateness_avg = 0.0
        agents = list(adapter.agent_snapshots_view().values())
        if agents:
            lateness_avg = sum(agent.lateness_counter for agent in agents) / len(agents)
        social_metric = float(
            (self._latest_relationship_metrics or {}).get("late_help_events", 0.0)
        )

        def _push(name: str, value: float) -> None:
            history = self._kpi_history.setdefault(name, [])
            history.append(value)
            if len(history) > 50:
                del history[0]

        _push("queue_conflict_intensity", queue_sum)
        _push("employment_lateness", lateness_avg)
        _push("late_help_events", social_metric)

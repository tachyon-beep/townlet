"""Telemetry pipelines and console bridge."""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Callable, Iterable, Mapping
from typing import TYPE_CHECKING, Any

from townlet.config import SimulationConfig
from townlet.telemetry.narration import NarrationRateLimiter
from townlet.telemetry.transport import (
    TelemetryTransportError,
    TransportBuffer,
    create_transport,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from townlet.world.grid import WorldState


class TelemetryPublisher:
    """Publishes observer snapshots and consumes console commands."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.schema_version = "0.8.0"
        self._console_buffer: list[object] = []
        self._latest_queue_metrics: dict[str, int] | None = None
        self._latest_embedding_metrics: dict[str, float] | None = None
        self._latest_events: list[dict[str, object]] = []
        self._event_subscribers: list[Callable[[list[dict[str, object]]], None]] = []
        self._latest_employment_metrics: dict[str, object] = {}
        self._latest_conflict_snapshot: dict[str, object] = {
            "queues": {"cooldown_events": 0, "ghost_step_events": 0},
            "rivalry": {},
        }
        self._latest_relationship_metrics: dict[str, object] | None = None
        self._latest_job_snapshot: dict[str, object] = {}
        self._latest_economy_snapshot: dict[str, object] = {}
        self._latest_relationship_snapshot: dict[str, dict[str, dict[str, float]]] = {}
        self._latest_relationship_updates: list[dict[str, object]] = []
        self._previous_relationship_snapshot: dict[str, dict[str, dict[str, float]]] = (
            {}
        )
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
        self._latest_reward_breakdown: dict[str, dict[str, float]] = {}
        self._latest_stability_inputs: dict[str, object] = {}
        self._latest_stability_metrics: dict[str, object] = {}
        self._latest_perturbations: dict[str, object] = {}
        self._latest_policy_identity: dict[str, object] | None = None
        self._latest_snapshot_migrations: list[str] = []
        transport_cfg = self.config.telemetry.transport
        self._transport_config = transport_cfg
        self._transport_retry = transport_cfg.retry
        self._transport_buffer = TransportBuffer(
            max_batch_size=int(transport_cfg.buffer.max_batch_size),
            max_buffer_bytes=int(transport_cfg.buffer.max_buffer_bytes),
        )
        self._transport_flush_interval = max(
            1, int(transport_cfg.buffer.flush_interval_ticks)
        )
        self._last_flush_tick = 0
        self._transport_status: dict[str, Any] = {
            "connected": False,
            "dropped_messages": 0,
            "last_error": None,
            "last_failure_tick": None,
            "last_success_tick": None,
        }
        self._transport_client = self._build_transport_client()

    def queue_console_command(self, command: object) -> None:
        self._console_buffer.append(command)

    def drain_console_buffer(self) -> Iterable[object]:
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
            "employment_metrics": dict(self._latest_employment_metrics or {}),
            "events": list(self._latest_events),
            "relationship_snapshot": self._copy_relationship_snapshot(
                self._latest_relationship_snapshot
            ),
            "relationship_updates": [
                dict(update) for update in self._latest_relationship_updates
            ],
            "narrations": [dict(entry) for entry in self._latest_narrations],
            "narration_state": self._narration_limiter.export_state(),
            "reward_breakdown": self.latest_reward_breakdown(),
            "perturbations": self.latest_perturbations(),
        }
        if self._latest_affordance_manifest:
            state["affordance_manifest"] = dict(self._latest_affordance_manifest)
        if self._latest_anneal_status is not None:
            state["anneal_status"] = dict(self._latest_anneal_status)
        if self._latest_policy_snapshot:
            state["policy_snapshot"] = {
                agent: dict(entry)
                for agent, entry in self._latest_policy_snapshot.items()
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
        state["transport_buffer_pending"] = len(self._transport_buffer)
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

        self._latest_job_snapshot = dict(payload.get("job_snapshot", {}))
        self._latest_economy_snapshot = dict(payload.get("economy_snapshot", {}))
        self._latest_employment_metrics = dict(payload.get("employment_metrics", {}))
        self._latest_events = list(payload.get("events", []))
        snapshot_payload = payload.get("relationship_snapshot") or {}
        if isinstance(snapshot_payload, dict):
            snapshot_copy = self._copy_relationship_snapshot(snapshot_payload)
            self._latest_relationship_snapshot = snapshot_copy
            self._previous_relationship_snapshot = self._copy_relationship_snapshot(
                snapshot_copy
            )
        updates_payload = payload.get("relationship_updates", [])
        if isinstance(updates_payload, list):
            self._latest_relationship_updates = [
                dict(update) for update in updates_payload
            ]
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
            self._latest_perturbations = self._normalize_perturbations_payload(
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
            self._latest_snapshot_migrations = [
                str(item) for item in migrations_payload
            ]
        else:
            self._latest_snapshot_migrations = []

        kpi_payload = payload.get("kpi_history")
        if isinstance(kpi_payload, Mapping):
            history: dict[str, list[float]] = {}
            for name, values in kpi_payload.items():
                if isinstance(values, list):
                    coerced = [
                        float(value)
                        for value in values
                        if isinstance(value, (int, float))
                    ]
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
        self._transport_buffer.clear()

    def export_console_buffer(self) -> list[object]:
        return list(self._console_buffer)

    def import_console_buffer(self, buffer: Iterable[object]) -> None:
        self._console_buffer = list(buffer)

    def latest_transport_status(self) -> dict[str, object]:
        """Return transport health and backlog counters for observability."""

        return dict(self._transport_status)

    def _build_transport_client(self):
        cfg = self._transport_config
        try:
            return create_transport(
                transport_type=str(cfg.type),
                file_path=cfg.file_path,
                endpoint=getattr(cfg, "endpoint", None),
                connect_timeout=float(cfg.connect_timeout_seconds),
                send_timeout=float(cfg.send_timeout_seconds),
            )
        except TelemetryTransportError as exc:  # pragma: no cover - init failure
            message = (
                f"Failed to initialise telemetry transport '{cfg.type}': {exc}"
            )
            logger.error(message)
            raise RuntimeError(message) from exc

    def _reset_transport_client(self) -> None:
        client = getattr(self, "_transport_client", None)
        if client is not None:
            try:
                client.close()
            except Exception:  # pragma: no cover - logging only
                logger.debug("Closing telemetry transport failed", exc_info=True)
        self._transport_client = self._build_transport_client()

    def _send_with_retry(self, payload: bytes, tick: int) -> bool:
        attempts = 0
        max_attempts = max(0, int(self._transport_retry.max_attempts))
        while True:
            try:
                self._transport_client.send(payload)
                self._transport_status["connected"] = True
                self._transport_status["last_success_tick"] = int(tick)
                return True
            except Exception as exc:  # pragma: no cover - depends on transport failure
                error_message = str(exc)
                self._transport_status["connected"] = False
                self._transport_status["last_error"] = error_message
                self._transport_status["last_failure_tick"] = int(tick)
                logger.warning(
                    "Telemetry transport send failed (attempt %s/%s): %s",
                    attempts + 1,
                    max_attempts + 1,
                    error_message,
                )
                if attempts >= max_attempts:
                    return False
                attempts += 1
                try:
                    self._reset_transport_client()
                except RuntimeError as reconnect_exc:
                    reconnect_msg = str(reconnect_exc)
                    self._transport_status["last_error"] = reconnect_msg
                    logger.error(
                        "Telemetry transport reconnect failed: %s", reconnect_msg
                    )
                    return False
                backoff = float(self._transport_retry.backoff_seconds)
                if backoff > 0:
                    time.sleep(backoff)

    def _flush_transport_buffer(self, tick: int) -> None:
        if not len(self._transport_buffer):
            return
        while len(self._transport_buffer):
            payload = self._transport_buffer.popleft()
            if not self._send_with_retry(payload, tick):
                self._transport_status["dropped_messages"] += 1
                logger.error(
                    "Dropping telemetry payload after repeated send failures"
                )
                if len(self._transport_buffer):
                    dropped = len(self._transport_buffer)
                    self._transport_status["dropped_messages"] += dropped
                    self._transport_buffer.clear()
                break
        else:
            self._last_flush_tick = int(tick)

    def _enqueue_stream_payload(self, payload: Mapping[str, Any], *, tick: int) -> None:
        encoded = json.dumps(
            payload,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        if not encoded.endswith(b"\n"):
            encoded += b"\n"
        self._transport_buffer.append(encoded)
        if self._transport_buffer.is_over_capacity():
            dropped = self._transport_buffer.drop_until_within_capacity()
            if dropped:
                self._transport_status["dropped_messages"] += dropped
                logger.warning(
                    "Telemetry buffer exceeded %s bytes; dropped %s payloads",
                    self._transport_buffer.max_buffer_bytes,
                    dropped,
                )
        should_flush = (
            len(self._transport_buffer) >= self._transport_buffer.max_batch_size
            or tick - self._last_flush_tick >= self._transport_flush_interval
        )
        if should_flush:
            self._flush_transport_buffer(tick)

    def _build_stream_payload(self, tick: int) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_version": self.schema_version,
            "tick": int(tick),
            "queue_metrics": dict(self._latest_queue_metrics or {}),
            "embedding_metrics": dict(self._latest_embedding_metrics or {}),
            "employment": dict(self._latest_employment_metrics or {}),
            "conflict": self.latest_conflict_snapshot(),
            "relationships": self._latest_relationship_metrics or {},
            "relationship_snapshot": self._copy_relationship_snapshot(
                self._latest_relationship_snapshot
            ),
            "relationship_updates": [
                dict(entry) for entry in self._latest_relationship_updates
            ],
            "relationship_overlay": {
                owner: [dict(item) for item in entries]
                for owner, entries in self._latest_relationship_overlay.items()
            },
            "events": list(self._latest_events),
            "narrations": [dict(entry) for entry in self._latest_narrations],
            "jobs": {
                agent_id: dict(snapshot)
                for agent_id, snapshot in self._latest_job_snapshot.items()
            },
            "economy": {
                object_id: dict(obj)
                for object_id, obj in self._latest_economy_snapshot.items()
            },
            "affordance_manifest": dict(self._latest_affordance_manifest),
            "reward_breakdown": self.latest_reward_breakdown(),
            "stability": {
                "metrics": self.latest_stability_metrics(),
                "alerts": self.latest_stability_alerts(),
                "inputs": self.latest_stability_inputs(),
            },
            "perturbations": self.latest_perturbations(),
            "policy_identity": self.latest_policy_identity() or {},
            "policy_snapshot": {
                agent: dict(data)
                for agent, data in self._latest_policy_snapshot.items()
            },
            "anneal_status": self.latest_anneal_status(),
            "kpi_history": self.kpi_history(),
        }
        return payload

    def close(self) -> None:
        if len(self._transport_buffer):
            self._flush_transport_buffer(self._last_flush_tick)
        try:
            self._transport_client.close()
        except Exception:  # pragma: no cover - shutdown cleanup
            logger.debug("Closing telemetry transport failed", exc_info=True)

    def publish_tick(
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
    ) -> None:
        # Observations and rewards are consumed for downstream side effects.
        _ = observations, rewards
        self._narration_limiter.begin_tick(int(tick))
        self._latest_narrations = []
        queue_metrics = world.queue_manager.metrics()
        self._latest_queue_metrics = queue_metrics
        rivalry_snapshot: dict[str, object] = {}
        rivalry_getter = getattr(world, "rivalry_snapshot", None)
        if callable(rivalry_getter):
            rivalry_snapshot = dict(rivalry_getter())
        self._latest_conflict_snapshot = {
            "queues": dict(queue_metrics),
            "rivalry": rivalry_snapshot,
        }
        relationship_metrics_getter = getattr(
            world, "relationship_metrics_snapshot", None
        )
        if callable(relationship_metrics_getter):
            metrics_snapshot = relationship_metrics_getter()
            if metrics_snapshot is not None:
                self._latest_relationship_metrics = dict(metrics_snapshot)
        relationship_snapshot = self._capture_relationship_snapshot(world)
        self._latest_relationship_updates = self._compute_relationship_updates(
            self._previous_relationship_snapshot,
            relationship_snapshot,
        )
        self._latest_relationship_snapshot = relationship_snapshot
        self._previous_relationship_snapshot = self._copy_relationship_snapshot(
            relationship_snapshot
        )
        self._latest_relationship_overlay = self._build_relationship_overlay()
        raw_embedding_metrics = world.embedding_allocator.metrics()
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
        self._process_narrations(self._latest_events, int(tick))
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
            }
            for agent_id, snapshot in world.agents.items()
        }
        self._latest_economy_snapshot = {
            object_id: {
                "type": obj.object_type,
                "stock": dict(obj.stock),
            }
            for object_id, obj in world.objects.items()
        }
        self._latest_employment_metrics = world.employment_queue_snapshot()
        if reward_breakdown is not None:
            self._latest_reward_breakdown = {
                agent: dict(components)
                for agent, components in reward_breakdown.items()
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
            self._update_kpi_history(world)

        if stability_inputs is not None:
            self._latest_stability_inputs = {
                "hunger_levels": dict(stability_inputs.get("hunger_levels", {}) or {}),
                "option_switch_counts": dict(
                    stability_inputs.get("option_switch_counts", {}) or {}
                ),
                "reward_samples": {
                    agent: float(value)
                    for agent, value in (
                        (stability_inputs.get("reward_samples") or {}).items()
                    )
                },
            }

        if isinstance(perturbations, Mapping):
            self._latest_perturbations = self._normalize_perturbations_payload(
                perturbations
            )

        if policy_identity is not None:
            self.update_policy_identity(policy_identity)

        stream_payload = self._build_stream_payload(tick)
        self._enqueue_stream_payload(stream_payload, tick=int(tick))

    def latest_queue_metrics(self) -> dict[str, int] | None:
        """Expose the most recent queue-related telemetry counters."""
        if self._latest_queue_metrics is None:
            return None
        return dict(self._latest_queue_metrics)

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
        return snapshot

    def latest_affordance_manifest(self) -> dict[str, object]:
        """Expose the most recent affordance manifest metadata."""

        return dict(self._latest_affordance_manifest)

    def latest_reward_breakdown(self) -> dict[str, dict[str, float]]:
        return {
            agent: dict(components)
            for agent, components in self._latest_reward_breakdown.items()
        }

    def latest_stability_inputs(self) -> dict[str, object]:
        if not self._latest_stability_inputs:
            return {}
        result: dict[str, object] = {}
        hunger = self._latest_stability_inputs.get("hunger_levels")
        if isinstance(hunger, dict):
            result["hunger_levels"] = {
                str(agent): float(value) for agent, value in hunger.items()
            }
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

    def record_stability_metrics(self, metrics: Mapping[str, object]) -> None:
        self._latest_stability_metrics = dict(metrics)

    def latest_stability_metrics(self) -> dict[str, object]:
        return dict(self._latest_stability_metrics)

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
                for event_id, data in self._latest_perturbations.get(
                    "active", {}
                ).items()
            },
            "pending": [
                dict(entry) for entry in self._latest_perturbations.get("pending", [])
            ],
            "cooldowns": {
                "spec": dict(
                    self._latest_perturbations.get("cooldowns", {}).get("spec", {})
                ),
                "agents": dict(
                    self._latest_perturbations.get("cooldowns", {}).get("agents", {})
                ),
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

    def record_snapshot_migrations(self, applied: Iterable[str]) -> None:
        self._latest_snapshot_migrations = [str(item) for item in applied]

    def latest_snapshot_migrations(self) -> list[str]:
        return list(self._latest_snapshot_migrations)

    def _normalize_perturbations_payload(
        self, payload: Mapping[str, object]
    ) -> dict[str, object]:
        active = payload.get("active", {})
        pending = payload.get("pending", [])
        cooldowns = payload.get("cooldowns", {})
        active_map: dict[str, dict[str, object]] = {}
        if isinstance(active, Mapping):
            active_map = {
                str(event_id): dict(entry)
                for event_id, entry in active.items()
                if isinstance(entry, Mapping)
            }
        pending_list: list[dict[str, object]] = []
        if isinstance(pending, list):
            pending_list = [
                dict(entry) for entry in pending if isinstance(entry, Mapping)
            ]
        spec_cd: dict[str, int] = {}
        agent_cd: dict[str, int] = {}
        if isinstance(cooldowns, Mapping):
            spec_payload = cooldowns.get("spec", {})
            if isinstance(spec_payload, Mapping):
                spec_cd = {
                    str(name): int(expiry)
                    for name, expiry in spec_payload.items()
                    if isinstance(expiry, int)
                }
            agent_payload = cooldowns.get("agents", {})
            if isinstance(agent_payload, Mapping):
                agent_cd = {
                    str(agent): int(expiry)
                    for agent, expiry in agent_payload.items()
                    if isinstance(expiry, int)
                }
        return {
            "active": active_map,
            "pending": pending_list,
            "cooldowns": {"spec": spec_cd, "agents": agent_cd},
        }

    def latest_policy_snapshot(self) -> dict[str, dict[str, object]]:
        return {
            agent: dict(data) for agent, data in self._latest_policy_snapshot.items()
        }

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
        return self._copy_relationship_snapshot(self._latest_relationship_snapshot)

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

    def register_event_subscriber(
        self, subscriber: Callable[[list[dict[str, object]]], None]
    ) -> None:
        """Register a callback to receive each tick's event batch."""
        self._event_subscribers.append(subscriber)

    def latest_job_snapshot(self) -> dict[str, dict[str, object]]:
        return getattr(self, "_latest_job_snapshot", {})

    def latest_economy_snapshot(self) -> dict[str, dict[str, object]]:
        return getattr(self, "_latest_economy_snapshot", {})

    def latest_employment_metrics(self) -> dict[str, object]:
        return dict(getattr(self, "_latest_employment_metrics", {}))

    def schema(self) -> str:
        return self.schema_version

    def _capture_relationship_snapshot(
        self,
        world: WorldState,
    ) -> dict[str, dict[str, dict[str, float]]]:
        snapshot_getter = getattr(world, "relationships_snapshot", None)
        if not callable(snapshot_getter):
            return {}
        raw = snapshot_getter() or {}
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
                    delta_fam = metrics["familiarity"] - prev_metrics.get(
                        "familiarity", 0.0
                    )
                    delta_riv = metrics["rivalry"] - prev_metrics.get("rivalry", 0.0)
                    if any(
                        abs(delta) > 1e-6
                        for delta in (delta_trust, delta_fam, delta_riv)
                    ):
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

    def _process_narrations(
        self,
        events: Iterable[dict[str, object]],
        tick: int,
    ) -> None:
        for event in events:
            event_name = event.get("event")
            if event_name == "queue_conflict":
                self._handle_queue_conflict_narration(event, tick)

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

    @staticmethod
    def _copy_relationship_snapshot(
        snapshot: dict[str, dict[str, dict[str, float]]],
    ) -> dict[str, dict[str, dict[str, float]]]:
        return {
            owner: {
                other: {
                    "trust": float(values.get("trust", 0.0)),
                    "familiarity": float(values.get("familiarity", 0.0)),
                    "rivalry": float(values.get("rivalry", 0.0)),
                }
                for other, values in ties.items()
            }
            for owner, ties in snapshot.items()
        }

    def _update_kpi_history(self, world: WorldState) -> None:
        queue_sum = float(
            self._latest_conflict_snapshot.get("queues", {}).get("intensity_sum", 0.0)
        )
        lateness_avg = 0.0
        agents = list(world.agents.values())
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

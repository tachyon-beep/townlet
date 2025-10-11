"""Console validation scaffolding."""

from __future__ import annotations

import copy
import json
import logging
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, TypeVar

if TYPE_CHECKING:
    from townlet.config import SimulationConfig
    from townlet.lifecycle.manager import LifecycleManager
    from townlet.scheduler.perturbations import PerturbationScheduler
    from townlet.world.grid import WorldState

from townlet.core.interfaces import PolicyBackendProtocol, TelemetrySinkProtocol
from townlet.core.utils import is_stub_policy, is_stub_telemetry
from townlet.snapshots import SnapshotManager
from townlet.stability.promotion import PromotionManager

SUPPORTED_SCHEMA_PREFIX = "0.9"
SUPPORTED_SCHEMA_LABEL = f"{SUPPORTED_SCHEMA_PREFIX}.x"

logger = logging.getLogger(__name__)


@dataclass
class ConsoleCommand:
    """Represents a parsed console command ready for execution."""

    name: str
    args: tuple[object, ...]
    kwargs: dict[str, object]


class ConsoleHandler(Protocol):
    def __call__(self, command: ConsoleCommand) -> object: ...


class ConsoleRouter:
    """Routes validated commands to subsystem handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, ConsoleHandler] = {}

    def register(self, name: str, handler: ConsoleHandler) -> None:
        """Register ``handler`` under ``name`` for later dispatch."""

        self._handlers[name] = handler

    def dispatch(self, command: ConsoleCommand) -> object:
        """Route the command to its registered handler and return the result."""

        handler = self._handlers.get(command.name)
        if handler is None:
            raise KeyError(f"Unknown console command: {command.name}")
        return handler(command)


class EventStream:
    """Simple subscriber that records the latest simulation events."""

    def __init__(self) -> None:
        self._latest: list[dict[str, object]] = []

    def connect(self, publisher: TelemetrySinkProtocol) -> None:
        """Subscribe to telemetry events produced by ``publisher``."""

        publisher.register_event_subscriber(self._record)

    def _record(self, events: list[dict[str, object]]) -> None:
        self._latest = events

    def latest(self) -> list[dict[str, object]]:
        """Return a copy of the latest recorded events."""

        return list(self._latest)


T = TypeVar("T")


class TelemetryBridge:
    """Provides access to the latest telemetry snapshots for console consumers."""

    def __init__(
        self,
        publisher: TelemetrySinkProtocol,
        *,
        provider_name: str | None = None,
    ) -> None:
        self._publisher = publisher
        self._provider_name = provider_name or ("stub" if is_stub_telemetry(publisher) else "unknown")
        self._dispatcher = getattr(publisher, "event_dispatcher", None)

    def _call_or_default(self, name: str, default: T) -> T:
        """Call a telemetry method if present; otherwise return default.

        This shields console consumers from transport/provider differences by
        avoiding direct reliance on publisher-specific attributes.
        """
        fn = getattr(self._publisher, name, None)
        if callable(fn):
            try:
                return fn()
            except Exception:  # pragma: no cover - defensive fallback
                return default
        return default

    def _global_context(self) -> dict[str, object]:
        """Return the latest DTO-backed global context emitted by the loop."""

        dispatcher = self._dispatcher
        if dispatcher is None:
            return {}
        latest_tick = dispatcher.latest_tick
        if not isinstance(latest_tick, Mapping):
            return {}
        payload = latest_tick.get("global_context")
        if not isinstance(payload, Mapping):
            return {}
        return {str(key): copy.deepcopy(value) for key, value in payload.items()}

    def snapshot(self) -> dict[str, dict[str, object]]:
        version, warning = _schema_metadata(self._publisher)
        global_context = self._global_context()
        command_metadata = {
            "relationship_summary": {
                "mode": "viewer",
                "usage": "relationship_summary",
                "description": "Return per-agent friends/rivals plus churn aggregates",
            },
            "relationship_detail": {
                "mode": "admin",
                "usage": "relationship_detail <agent_id>",
                "description": "Inspect detailed ledger ties and recent updates for an agent",
            },
            "social_events": {
                "mode": "viewer",
                "usage": "social_events [--limit N]",
                "description": "List recent chat and rivalry avoidance events (newest first)",
            },
            "announce_story": {
                "mode": "viewer",
                "usage": "announce_story <message> [--category tag] [--priority true|false]",
                "description": "Push an operator narration entry to observers",
            },
        }
        jobs_payload = copy.deepcopy(global_context.get("job_snapshot", {}))
        economy_payload = copy.deepcopy(global_context.get("economy_snapshot", {}))
        economy_settings_payload = copy.deepcopy(global_context.get("economy_settings", {}))
        price_spikes_payload = copy.deepcopy(global_context.get("price_spikes", {}))
        utilities_payload = copy.deepcopy(global_context.get("utilities", {}))
        employment_payload = copy.deepcopy(global_context.get("employment_snapshot", {}))
        relationship_metrics_payload = copy.deepcopy(global_context.get("relationship_metrics", {}))
        relationship_snapshot_payload = copy.deepcopy(global_context.get("relationship_snapshot", {}))
        promotion_payload = copy.deepcopy(global_context.get("promotion_state", {}))
        anneal_payload = copy.deepcopy(global_context.get("anneal_context", {}))
        queue_metrics_payload = copy.deepcopy(global_context.get("queue_metrics", {}))
        stability_metrics_payload = copy.deepcopy(global_context.get("stability_metrics", {}))
        perturbations_payload = copy.deepcopy(global_context.get("perturbations", {}))
        payload = {
            "schema_version": version,
            "schema_warning": warning,
            "console_commands": command_metadata,
            "jobs": jobs_payload or self._call_or_default("latest_job_snapshot", {}),
            "economy": economy_payload or self._call_or_default("latest_economy_snapshot", {}),
            "economy_settings": economy_settings_payload or self._call_or_default("latest_economy_settings", {}),
            "price_spikes": price_spikes_payload or self._call_or_default("latest_price_spikes", {}),
            "utilities": utilities_payload or self._call_or_default("latest_utilities", {}),
            "employment": employment_payload or self._call_or_default("latest_employment_metrics", {}),
            "queue_metrics": queue_metrics_payload or self._call_or_default("latest_queue_metrics", {}),
            "conflict": self._call_or_default("latest_conflict_snapshot", {}),
            "relationships": relationship_metrics_payload or self._call_or_default("latest_relationship_metrics", {}) or {},
            "relationship_snapshot": relationship_snapshot_payload or self._call_or_default("latest_relationship_snapshot", {}),
            "relationship_updates": self._call_or_default("latest_relationship_updates", []),
            "relationship_summary": self._call_or_default("latest_relationship_summary", {}),
            "social_events": self._call_or_default("latest_social_events", []),
            "events": list(self._call_or_default("latest_events", [])),
            "narrations": self._call_or_default("latest_narrations", []),
            "narration_state": self._call_or_default("latest_narration_state", {}),
            "anneal_status": anneal_payload or self._call_or_default("latest_anneal_status", None),
            "policy_snapshot": self._call_or_default("latest_policy_snapshot", {}),
            "policy_identity": self._call_or_default("latest_policy_identity", {}) or {},
            "snapshot_migrations": self._call_or_default("latest_snapshot_migrations", []),
            "affordance_manifest": self._call_or_default("latest_affordance_manifest", {}),
            "affordance_runtime": self._call_or_default("latest_affordance_runtime", {}),
            "reward_breakdown": self._call_or_default("latest_reward_breakdown", {}),
            "personalities": self._call_or_default("latest_personality_snapshot", {}),
            "stability": {
                "alerts": self._call_or_default("latest_stability_alerts", []),
                "metrics": stability_metrics_payload or self._call_or_default("latest_stability_metrics", {}),
                "promotion_state": promotion_payload or getattr(self._publisher, "latest_promotion_state", lambda: None)(),
            },
            "perturbations": perturbations_payload or self._call_or_default("latest_perturbations", {}),
            "transport": self._call_or_default("latest_transport_status", {}),
            "health": self._call_or_default("latest_health_status", {}),
            "console_results": self._call_or_default("latest_console_results", []),
            "possessed_agents": self._call_or_default("latest_possessed_agents", []),
            "precondition_failures": self._call_or_default("latest_precondition_failures", []),
        }
        provider = self._provider_name
        # Defensive: treat as stub if either provider says 'stub' or instance is StubTelemetrySink.
        if provider == "stub" or is_stub_telemetry(self._publisher):
            payload["telemetry_warning"] = {
                "provider": provider,
                "message": "Telemetry running in stub mode; real-time streaming disabled.",
            }
        return payload

    def relationship_summary_payload(self) -> dict[str, object]:
        """Return normalised relationship summary data for console consumers."""

        raw_summary = self._publisher.latest_relationship_summary()
        per_agent: dict[str, dict[str, object]] = {}
        churn_payload: dict[str, object] = {}
        for agent, entry in raw_summary.items():
            if agent == "churn":
                if isinstance(entry, Mapping):
                    churn_payload = dict(entry)
                continue
            if not isinstance(entry, Mapping):
                continue
            friends = entry.get("top_friends", [])
            rivals = entry.get("top_rivals", [])
            per_agent[agent] = {
                "top_friends": [dict(item) for item in friends if isinstance(item, Mapping)],
                "top_rivals": [dict(item) for item in rivals if isinstance(item, Mapping)],
            }
        return {"per_agent": per_agent, "churn": churn_payload}

    def relationship_detail_payload(self, agent_id: str) -> dict[str, object]:
        """Expose ledger metrics and recent updates for the requested agent."""

        agent_key = str(agent_id)
        snapshot = self._publisher.latest_relationship_snapshot()
        agent_ties = snapshot.get(agent_key)
        if not agent_ties:
            raise KeyError(agent_key)

        tie_entries: list[dict[str, object]] = []
        for other, metrics in (agent_ties or {}).items():
            if not isinstance(metrics, Mapping):
                continue
            tie_entries.append(
                {
                    "other": str(other),
                    "trust": float(metrics.get("trust", 0.0)),
                    "familiarity": float(metrics.get("familiarity", 0.0)),
                    "rivalry": float(metrics.get("rivalry", 0.0)),
                }
            )
        tie_entries.sort(key=lambda item: item["trust"] + item["familiarity"], reverse=True)

        overlay_entries: list[dict[str, object]] = []
        overlay = self._publisher.latest_relationship_overlay().get(agent_key, [])
        for entry in overlay:
            if not isinstance(entry, Mapping):
                continue
            overlay_entries.append(
                {
                    "other": str(entry.get("other", "")),
                    "trust": float(entry.get("trust", 0.0)),
                    "familiarity": float(entry.get("familiarity", 0.0)),
                    "rivalry": float(entry.get("rivalry", 0.0)),
                    "delta_trust": float(entry.get("delta_trust", 0.0)),
                    "delta_familiarity": float(entry.get("delta_familiarity", 0.0)),
                    "delta_rivalry": float(entry.get("delta_rivalry", 0.0)),
                }
            )

        updates_payload: list[dict[str, object]] = []
        incoming_payload: list[dict[str, object]] = []
        for update in self._publisher.latest_relationship_updates():
            if not isinstance(update, Mapping):
                continue
            owner = str(update.get("owner", ""))
            other = str(update.get("other", ""))
            delta_mapping = update.get("delta")
            if isinstance(delta_mapping, Mapping):
                delta_trust = float(delta_mapping.get("trust", 0.0))
                delta_familiarity = float(delta_mapping.get("familiarity", 0.0))
                delta_rivalry = float(delta_mapping.get("rivalry", 0.0))
            else:
                delta_trust = delta_familiarity = delta_rivalry = 0.0
            payload = {
                "owner": owner,
                "other": other,
                "status": str(update.get("status", "")),
                "trust": float(update.get("trust", 0.0)),
                "familiarity": float(update.get("familiarity", 0.0)),
                "rivalry": float(update.get("rivalry", 0.0)),
                "delta": {
                    "trust": delta_trust,
                    "familiarity": delta_familiarity,
                    "rivalry": delta_rivalry,
                },
            }
            if owner == agent_key:
                updates_payload.append(payload)
            elif other == agent_key:
                incoming_payload.append(payload)

        return {
            "agent_id": agent_key,
            "ties": tie_entries,
            "overlay": overlay_entries,
            "recent_updates": updates_payload,
            "incoming_updates": incoming_payload,
        }

    def social_events_payload(self, limit: int | None = None) -> list[dict[str, object]]:
        """Return a bounded list of the most recent social events."""

        events = self._publisher.latest_social_events()
        if limit is not None and limit >= 0:
            return list(reversed(events))[:limit]
        return list(reversed(events))


def create_console_router(
    publisher: TelemetrySinkProtocol,
    world: WorldState | None = None,
    scheduler: PerturbationScheduler | None = None,
    promotion: PromotionManager | None = None,
    *,
    policy: PolicyBackendProtocol | None = None,
    policy_provider: str | None = None,
    telemetry_provider: str | None = None,
    mode: str = "viewer",
    config: SimulationConfig | None = None,
    lifecycle: LifecycleManager | None = None,
) -> ConsoleRouter:
    router = ConsoleRouter()
    allowed_snapshot_roots: tuple[Path, ...] = ()
    if config is not None:
        config.register_snapshot_migrations()
        allowed_snapshot_roots = config.snapshot_allowed_roots()
    inferred_policy_provider = policy_provider
    if inferred_policy_provider is None and policy is not None:
        inferred_policy_provider = "stub" if is_stub_policy(policy) else "unknown"
    if policy is not None and is_stub_policy(policy, inferred_policy_provider):
        logger.warning(
            "console_router_stub_policy provider=%s message='Console operating with stub policy backend'",
            inferred_policy_provider,
        )

    inferred_telemetry_provider = telemetry_provider
    if inferred_telemetry_provider is None:
        inferred_telemetry_provider = "stub" if is_stub_telemetry(publisher) else "unknown"
    if is_stub_telemetry(publisher, inferred_telemetry_provider):
        logger.warning(
            "console_router_stub_telemetry provider=%s message='Console telemetry limited to in-memory data'",
            inferred_telemetry_provider,
        )

    bridge = TelemetryBridge(publisher, provider_name=inferred_telemetry_provider)

    def _forbidden(_: ConsoleCommand) -> object:
        return {
            "error": "forbidden",
            "message": "command requires admin mode",
        }

    def _attach_metadata(result: dict[str, object], command: ConsoleCommand) -> dict[str, object]:
        cmd_id = command.kwargs.get("cmd_id")
        if cmd_id is not None:
            result["cmd_id"] = cmd_id
        issuer = command.kwargs.get("issuer")
        if issuer is not None:
            result["issuer"] = issuer
        return result

    def _refresh_promotion_metrics() -> None:
        if promotion is None:
            return
        metrics = publisher.latest_stability_metrics()
        base = dict(metrics) if isinstance(metrics, dict) else {}
        base["promotion_state"] = promotion.snapshot()
        emit = getattr(publisher, "emit_event", None)
        if callable(emit):
            emit("stability.metrics", base)

    def _apply_release_metadata(metadata: object) -> None:
        if policy is None and config is None:
            return
        metadata_dict: dict[str, object] = {}
        if isinstance(metadata, dict):
            metadata_dict = metadata
        policy_hash_value = metadata_dict.get("policy_hash")
        active_hash: str | None = None
        anneal_ratio: float | None = None
        if policy is not None:
            if policy_hash_value is not None:
                policy.set_policy_hash(str(policy_hash_value))
            else:
                policy.set_policy_hash(None)
            active_hash = policy.active_policy_hash()
            try:
                anneal_ratio = policy.current_anneal_ratio()
            except Exception:  # pragma: no cover - defensive
                anneal_ratio = None
        elif policy_hash_value is not None:
            active_hash = str(policy_hash_value)
        if config is not None:
            identity = config.build_snapshot_identity(
                policy_hash=active_hash,
                runtime_observation_variant=config.observation_variant,
                runtime_anneal_ratio=anneal_ratio,
            )
            publisher.update_policy_identity(identity)

    def _is_path_allowed(resolved: Path) -> bool:
        return any(resolved == root or resolved.is_relative_to(root) for root in allowed_snapshot_roots)

    def _resolve_snapshot_input(
        value: object,
        *,
        require_exists: bool,
        require_file: bool,
    ) -> tuple[Path | None, dict[str, object] | None]:
        if not allowed_snapshot_roots:
            return None, {
                "error": "unsupported",
                "message": "snapshot commands require configured snapshot roots",
            }
        try:
            candidate = Path(str(value)).expanduser()
            resolved = candidate.resolve()
        except Exception as exc:  # pragma: no cover - defensive
            return None, {
                "error": "invalid_path",
                "message": str(exc),
            }
        if require_exists and not resolved.exists():
            return None, {"error": "not_found", "path": str(resolved)}
        if require_file:
            if resolved.is_dir():
                return None, {
                    "error": "invalid_path",
                    "message": "snapshot path must reference a file",
                }
        if not _is_path_allowed(resolved):
            return None, {
                "error": "forbidden",
                "message": "path is outside permitted snapshot roots",
            }
        return resolved, None

    def _parse_snapshot_path(command: ConsoleCommand, usage: str) -> tuple[Path | None, dict[str, object] | None]:
        path_arg = command.kwargs.get("path")
        if path_arg is None and command.args:
            path_arg = command.args[0]
        if path_arg is None:
            return None, {"error": "usage", "message": usage}
        return _resolve_snapshot_input(
            path_arg,
            require_exists=True,
            require_file=True,
        )

    def _require_config() -> tuple[SimulationConfig | None, dict[str, object] | None]:
        if config is None:
            return None, {
                "error": "unsupported",
                "message": "snapshot command requires simulation config",
            }
        return config, None

    def telemetry_handler(command: ConsoleCommand) -> object:
        return bridge.snapshot()

    def health_status_handler(command: ConsoleCommand) -> object:
        return {
            "health": publisher.latest_health_status(),
            "transport": publisher.latest_transport_status(),
        }

    def employment_status_handler(command: ConsoleCommand) -> object:
        version, warning = _schema_metadata(publisher)
        metrics = publisher.latest_employment_metrics()
        return {
            "schema_version": version,
            "schema_warning": warning,
            "metrics": metrics,
            "pending_agents": metrics.get("pending", []),
        }

    def relationship_summary_handler(command: ConsoleCommand) -> object:
        version, warning = _schema_metadata(publisher)
        payload = bridge.relationship_summary_payload()
        return {
            "schema_version": version,
            "schema_warning": warning,
            "summary": payload["per_agent"],
            "churn": payload["churn"],
        }

    def relationship_detail_handler(command: ConsoleCommand) -> object:
        agent_arg = command.kwargs.get("agent_id")
        if agent_arg is None and command.args:
            agent_arg = command.args[0]
        if agent_arg is None:
            return {
                "error": "usage",
                "message": "relationship_detail <agent_id>",
            }
        agent_id = str(agent_arg)
        try:
            payload = bridge.relationship_detail_payload(agent_id)
        except KeyError:
            return {
                "error": "not_found",
                "agent_id": agent_id,
            }
        version, warning = _schema_metadata(publisher)
        return {
            "schema_version": version,
            "schema_warning": warning,
            **payload,
        }

    def social_events_handler(command: ConsoleCommand) -> object:
        limit_arg = command.kwargs.get("limit")
        if limit_arg is None and command.args:
            limit_arg = command.args[0]
        limit_value: int | None
        if limit_arg is None:
            limit_value = None
        else:
            try:
                limit_value = int(limit_arg)
            except (TypeError, ValueError):
                return {
                    "error": "invalid_args",
                    "message": "limit must be an integer",
                }
            if limit_value < 0:
                return {
                    "error": "invalid_args",
                    "message": "limit must be non-negative",
                }
        version, warning = _schema_metadata(publisher)
        events = bridge.social_events_payload(limit_value)
        return {
            "schema_version": version,
            "schema_warning": warning,
            "events": events,
        }

    def _coerce_priority(value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            candidate = value.strip().lower()
            return candidate in {"1", "true", "yes", "on"}
        return False

    def announce_story_handler(command: ConsoleCommand) -> object:
        message_arg = command.kwargs.get("message")
        if message_arg is None and command.args:
            message_arg = command.args[0]
        if not isinstance(message_arg, str) or not message_arg.strip():
            return {
                "error": "usage",
                "message": ("announce_story <message> [--category tag] [--priority true|false]"),
            }
        message = message_arg.strip()
        category = str(command.kwargs.get("category", "operator_story")).strip() or "operator_story"
        priority = _coerce_priority(command.kwargs.get("priority", False))
        dedupe_key_arg = command.kwargs.get("dedupe_key")
        dedupe_key = str(dedupe_key_arg) if dedupe_key_arg is not None else None

        data_payload = command.kwargs.get("data")
        if data_payload is None:
            data: dict[str, object] | None = None
        elif isinstance(data_payload, Mapping):
            data = dict(data_payload)
        elif isinstance(data_payload, str):
            try:
                parsed = json.loads(data_payload)
            except json.JSONDecodeError as exc:  # pragma: no cover - defensive
                return {
                    "error": "invalid_args",
                    "message": f"data parse error: {exc.msg}",
                }
            if not isinstance(parsed, Mapping):
                return {
                    "error": "invalid_args",
                    "message": "data must decode to an object mapping",
                }
            data = dict(parsed)
        else:
            return {
                "error": "invalid_args",
                "message": "data must be a mapping or JSON object",
            }

        tick_arg = command.kwargs.get("tick")
        if tick_arg is None:
            tick_value = publisher.current_tick()
        else:
            try:
                tick_value = int(tick_arg)
            except (TypeError, ValueError):
                return {
                    "error": "invalid_args",
                    "message": "tick must be an integer",
                }

        try:
            entry = publisher.emit_manual_narration(
                message=message,
                category=category,
                tick=tick_value,
                priority=priority,
                data=data,
                dedupe_key=dedupe_key,
            )
        except ValueError as exc:
            return {"error": "invalid_args", "message": str(exc)}

        if entry is None:
            return {
                "queued": False,
                "throttled": True,
                "message": "narration suppressed by rate limiter",
            }
        return {
            "queued": True,
            "entry": entry,
        }

    def affordance_status_handler(command: ConsoleCommand) -> object:
        version, warning = _schema_metadata(publisher)
        runtime = publisher.latest_affordance_runtime()
        if world is not None:
            snapshot = world.running_affordances_snapshot()
            runtime = {
                "running_count": len(snapshot),
                "running": {object_id: asdict(state) for object_id, state in snapshot.items()},
                "active_reservations": world.active_reservations,
                "event_counts": dict(runtime.get("event_counts", {})),
            }
        event_counts = runtime.get("event_counts", {})
        for key in ("start", "finish", "fail", "precondition_fail"):
            event_counts.setdefault(key, 0)
        runtime["event_counts"] = event_counts
        return {
            "schema_version": version,
            "schema_warning": warning,
            "runtime": runtime,
        }

    def employment_exit_handler(command: ConsoleCommand) -> object:
        if world is None:
            raise RuntimeError("employment_exit requires world access")
        if not command.args:
            return {
                "error": "usage",
                "message": "employment_exit <approve|defer|review> [agent_id]",
            }
        action = str(command.args[0])
        if action == "review":
            return world.employment_queue_snapshot()
        if len(command.args) < 2:
            return {"error": "missing_agent_id"}
        agent_id = str(command.args[1])
        if action == "approve":
            success = world.employment_request_manual_exit(agent_id, tick=world.tick)
            return {"approved": success, "agent_id": agent_id}
        if action == "defer":
            success = world.employment_defer_exit(agent_id)
            return {"deferred": success, "agent_id": agent_id}
        return {"error": "unknown_action", "action": action}

    def possess_handler(command: ConsoleCommand) -> object:
        if policy is None:
            return {"error": "unsupported"}
        payload = command.kwargs.get("payload")
        agent_id: str | None = None
        action = command.kwargs.get("action") if isinstance(command.kwargs.get("action"), str) else None
        if isinstance(payload, Mapping):
            candidate = payload.get("agent_id")
            if isinstance(candidate, str):
                agent_id = candidate
            if isinstance(payload.get("action"), str):
                action = payload["action"]
        if agent_id is None and command.args:
            first = command.args[0]
            if isinstance(first, str):
                agent_id = first
        if agent_id is None or not agent_id:
            return {
                "error": "usage",
                "message": "possess requires agent_id",
            }
        if world is not None and agent_id not in world.agents:
            return {"error": "not_found", "agent_id": agent_id}
        verb = str(action or "acquire").lower()
        if verb not in {"acquire", "release"}:
            return {
                "error": "invalid_args",
                "message": "action must be 'acquire' or 'release'",
            }
        if verb == "acquire":
            if not policy.acquire_possession(agent_id):
                return {
                    "error": "conflict",
                    "message": "agent already possessed",
                    "agent_id": agent_id,
                }
            if world is not None:
                world.request_ctx_reset(agent_id)
            possessed = True
        else:
            if not policy.release_possession(agent_id):
                return {
                    "error": "invalid_args",
                    "message": "agent not currently possessed",
                    "agent_id": agent_id,
                }
            possessed = False
        return {
            "agent_id": agent_id,
            "possessed": possessed,
            "possessed_agents": policy.possessed_agents(),
        }

    def kill_handler(command: ConsoleCommand) -> object:
        if world is None:
            return {"error": "unsupported"}
        payload = command.kwargs.get("payload")
        agent_id: str | None = None
        reason: str | None = None
        if isinstance(payload, Mapping):
            candidate = payload.get("agent_id")
            if isinstance(candidate, str):
                agent_id = candidate
            if isinstance(payload.get("reason"), str):
                reason = payload["reason"]
        if agent_id is None and command.args:
            first = command.args[0]
            if isinstance(first, str):
                agent_id = first
        if agent_id is None or not agent_id:
            return {
                "error": "usage",
                "message": "kill requires agent_id",
            }
        if not world.kill_agent(agent_id, reason=reason):
            return {"error": "not_found", "agent_id": agent_id}
        return {
            "agent_id": agent_id,
            "killed": True,
            "reason": reason,
        }

    def toggle_mortality_handler(command: ConsoleCommand) -> object:
        if lifecycle is None:
            return {"error": "unsupported"}
        payload = command.kwargs.get("payload")
        value = command.kwargs.get("enabled") if isinstance(command.kwargs.get("enabled"), bool) else None
        if isinstance(payload, Mapping) and "enabled" in payload:
            candidate = payload.get("enabled")
            if isinstance(candidate, bool):
                value = candidate
        if value is None:
            return {
                "error": "usage",
                "message": "toggle_mortality requires enabled bool",
            }
        lifecycle.set_mortality_enabled(bool(value))
        return {"enabled": lifecycle.mortality_enabled}

    def set_exit_cap_handler(command: ConsoleCommand) -> object:
        if world is None:
            return {"error": "unsupported"}
        payload = command.kwargs.get("payload")
        cap_value = command.kwargs.get("daily_exit_cap") if isinstance(command.kwargs.get("daily_exit_cap"), int) else None
        if isinstance(payload, Mapping) and "daily_exit_cap" in payload:
            candidate = payload.get("daily_exit_cap")
            if isinstance(candidate, int):
                cap_value = candidate
        if cap_value is None:
            return {
                "error": "usage",
                "message": "set_exit_cap requires daily_exit_cap integer",
            }
        if cap_value < 0:
            return {
                "error": "invalid_args",
                "message": "daily_exit_cap must be >= 0",
            }
        world.config.employment.daily_exit_cap = cap_value
        metrics = world.employment_queue_snapshot()
        return {
            "daily_exit_cap": cap_value,
            "metrics": metrics,
        }

    def set_spawn_delay_handler(command: ConsoleCommand) -> object:
        if lifecycle is None:
            return {"error": "unsupported"}
        payload = command.kwargs.get("payload")
        delay_value = command.kwargs.get("delay")
        if isinstance(payload, Mapping) and "delay" in payload:
            delay_value = payload.get("delay")
        if delay_value is None and command.args:
            delay_value = command.args[0]
        try:
            delay_int = int(delay_value)
        except (TypeError, ValueError):
            return {
                "error": "usage",
                "message": "set_spawn_delay <ticks>",
            }
        if delay_int < 0:
            return {
                "error": "invalid_args",
                "message": "delay must be >= 0",
            }
        lifecycle.set_respawn_delay(delay_int)
        return {"respawn_delay_ticks": lifecycle.respawn_delay_ticks}

    def conflict_status_handler(command: ConsoleCommand) -> object:
        version, warning = _schema_metadata(publisher)
        try:
            history_limit = int(command.kwargs.get("history", 10))
        except (TypeError, ValueError):
            history_limit = 10
        try:
            rivalry_limit = int(command.kwargs.get("rivalries", 10))
        except (TypeError, ValueError):
            rivalry_limit = 10
        queue_history = publisher.latest_queue_history()
        if history_limit > 0:
            queue_history = queue_history[-history_limit:]
        rivalry_events = publisher.latest_rivalry_events()
        if rivalry_limit > 0:
            rivalry_events = rivalry_events[-rivalry_limit:]
        return {
            "schema_version": version,
            "schema_warning": warning,
            "queue_metrics": publisher.latest_queue_metrics() or {},
            "conflict": publisher.latest_conflict_snapshot(),
            "history": queue_history,
            "rivalry_events": rivalry_events,
            "stability_alerts": publisher.latest_stability_alerts(),
            "stability_metrics": publisher.latest_stability_metrics(),
        }

    def queue_inspect_handler(command: ConsoleCommand) -> object:
        if world is None:
            return {"error": "unsupported"}
        if not command.args:
            return {
                "error": "usage",
                "message": "queue_inspect <object_id>",
            }
        object_id = str(command.args[0])
        state = world.queue_manager.export_state()
        queues = state.get("queues", {})
        entries = [
            {
                "agent_id": str(entry.get("agent_id", "")),
                "joined_tick": int(entry.get("joined_tick", 0)),
            }
            for entry in queues.get(object_id, [])
        ]
        cooldowns = []
        for item in state.get("cooldowns", []):
            if str(item.get("object_id")) != object_id:
                continue
            expiry = int(item.get("expiry", 0))
            cooldowns.append(
                {
                    "agent_id": str(item.get("agent_id", "")),
                    "expiry_tick": expiry,
                    "ticks_remaining": max(0, expiry - world.tick),
                }
            )
        stall_counts = state.get("stall_counts", {})
        return {
            "object_id": object_id,
            "tick": world.tick,
            "active": world.queue_manager.active_agent(object_id),
            "queue": entries,
            "cooldowns": cooldowns,
            "stall_count": int(stall_counts.get(object_id, 0)),
            "metrics": publisher.latest_queue_metrics() or {},
        }

    def rivalry_dump_handler(command: ConsoleCommand) -> object:
        if world is None:
            return {"error": "unsupported"}
        snapshot_getter = getattr(world, "rivalry_snapshot", None)
        if not callable(snapshot_getter):
            return {"error": "unsupported"}
        ledger = snapshot_getter() or {}
        try:
            limit = int(command.kwargs.get("limit", 5))
        except (TypeError, ValueError):
            limit = 5
        if command.args:
            agent_id = str(command.args[0])
            rivals = ledger.get(agent_id, {}) or {}
            sorted_rivals = sorted(
                ((other, float(value)) for other, value in rivals.items()),
                key=lambda item: item[1],
                reverse=True,
            )
            if limit > 0:
                sorted_rivals = sorted_rivals[:limit]
            return {
                "agent_id": agent_id,
                "rivals": [{"agent_id": other, "intensity": intensity} for other, intensity in sorted_rivals],
            }
        edges: list[tuple[str, str, float]] = []
        for owner, rivals in ledger.items():
            for other, value in (rivals or {}).items():
                if owner >= other:
                    continue
                edges.append((owner, other, float(value)))
        edges.sort(key=lambda item: item[2], reverse=True)
        if limit > 0:
            edges = edges[:limit]
        return {
            "pairs": [{"agent_a": a, "agent_b": b, "intensity": intensity} for a, b, intensity in edges],
            "agent_count": len(ledger),
        }

    def promotion_status_handler(command: ConsoleCommand) -> object:
        if promotion is None:
            return _attach_metadata({"error": "unsupported"}, command)
        result = {"promotion": promotion.snapshot()}
        return _attach_metadata(result, command)

    def promote_policy_handler(command: ConsoleCommand) -> object:
        if promotion is None:
            return _attach_metadata({"error": "unsupported"}, command)
        if not promotion.candidate_ready:
            return _attach_metadata(
                {"error": "promotion_not_ready", "promotion": promotion.snapshot()},
                command,
            )
        checkpoint_arg = command.kwargs.get("checkpoint")
        if checkpoint_arg is None and command.args:
            checkpoint_arg = command.args[0]
        if checkpoint_arg is None:
            return _attach_metadata(
                {
                    "error": "usage",
                    "message": "promote_policy <checkpoint> [--policy-hash HASH]",
                },
                command,
            )
        try:
            checkpoint_path = Path(str(checkpoint_arg)).expanduser().resolve()
        except Exception as exc:  # pragma: no cover - defensive
            return _attach_metadata({"error": "invalid_path", "message": str(exc)}, command)
        metadata: dict[str, object] = {"checkpoint": str(checkpoint_path)}
        policy_hash = command.kwargs.get("policy_hash")
        if policy_hash is not None:
            metadata["policy_hash"] = str(policy_hash)
        promotion.set_candidate_metadata(metadata)
        promotion.mark_promoted(tick=getattr(world, "tick", 0), metadata=metadata)
        snapshot = promotion.snapshot()
        _refresh_promotion_metrics()
        _apply_release_metadata(snapshot.get("current_release"))
        return _attach_metadata({"promoted": True, "promotion": snapshot}, command)

    def rollback_policy_handler(command: ConsoleCommand) -> object:
        if promotion is None:
            return _attach_metadata({"error": "unsupported"}, command)
        metadata: dict[str, object] = {}
        checkpoint_arg = command.kwargs.get("checkpoint")
        if checkpoint_arg is not None:
            try:
                checkpoint_path = Path(str(checkpoint_arg)).expanduser().resolve()
                metadata["checkpoint"] = str(checkpoint_path)
            except Exception as exc:  # pragma: no cover - defensive
                return _attach_metadata({"error": "invalid_path", "message": str(exc)}, command)
        reason = command.kwargs.get("reason")
        if reason is not None:
            metadata["reason"] = str(reason)
        promotion.register_rollback(tick=getattr(world, "tick", 0), metadata=metadata)
        promotion.set_candidate_metadata(None)
        snapshot = promotion.snapshot()
        _refresh_promotion_metrics()
        _apply_release_metadata(snapshot.get("current_release"))
        return _attach_metadata({"rolled_back": True, "promotion": snapshot}, command)

    def policy_swap_handler(command: ConsoleCommand) -> object:
        if policy is None and promotion is None:
            return _attach_metadata({"error": "unsupported"}, command)
        if command.kwargs.get("cmd_id") is None:
            return {"error": "usage", "message": "policy_swap requires cmd_id"}
        checkpoint_arg = command.kwargs.get("checkpoint")
        if checkpoint_arg is None and command.args:
            checkpoint_arg = command.args[0]
        if checkpoint_arg is None:
            return _attach_metadata(
                {
                    "error": "usage",
                    "message": "policy_swap <checkpoint> [--policy-hash HASH]",
                },
                command,
            )
        try:
            checkpoint_path = Path(str(checkpoint_arg)).expanduser().resolve()
        except Exception as exc:  # pragma: no cover - defensive
            return _attach_metadata({"error": "invalid_path", "message": str(exc)}, command)
        if not checkpoint_path.exists():
            return _attach_metadata(
                {
                    "error": "not_found",
                    "message": f"checkpoint '{checkpoint_path}' not found",
                },
                command,
            )
        metadata: dict[str, object] = {"checkpoint": str(checkpoint_path)}
        policy_hash = command.kwargs.get("policy_hash")
        if policy_hash is not None:
            metadata["policy_hash"] = str(policy_hash)
        snapshot: dict[str, object] | None = None
        if promotion is not None:
            snapshot = promotion.record_manual_swap(
                tick=getattr(world, "tick", 0),
                metadata=metadata,
            )
            _refresh_promotion_metrics()
        _apply_release_metadata(metadata)
        result: dict[str, object] = {"swapped": True, "release": metadata}
        if snapshot is not None:
            result["promotion"] = snapshot
        return _attach_metadata(result, command)

    def arrange_meet_handler(command: ConsoleCommand) -> object:
        if scheduler is None or world is None:
            return {"error": "unsupported"}
        payload = command.kwargs.get("payload")
        if payload is None and command.args:
            payload = command.args[0]
        if not isinstance(payload, Mapping):
            return {"error": "invalid_args", "message": "payload must be a mapping"}
        spec = payload.get("spec")
        if not isinstance(spec, str) or not spec:
            return {"error": "invalid_args", "message": "spec is required"}
        agents = payload.get("agents")
        if not isinstance(agents, list) or not agents:
            return {"error": "invalid_args", "message": "agents list required"}
        agent_ids = [str(agent) for agent in agents]
        missing = [agent for agent in agent_ids if agent not in world.agents]
        if missing:
            return {
                "error": "not_found",
                "message": "agents missing",
                "agents": missing,
            }
        starts_in = int(payload.get("starts_in", 0) or 0)
        duration = payload.get("duration")
        duration_int = int(duration) if duration is not None else None
        overrides = dict(payload.get("payload", {})) if isinstance(payload.get("payload"), Mapping) else None
        try:
            event = scheduler.schedule_manual(
                world,
                spec_name=spec,
                current_tick=world.tick,
                starts_in=starts_in,
                duration=duration_int,
                targets=agent_ids,
                payload_overrides=overrides,
            )
        except KeyError:
            return {"error": "unknown_spec", "spec": spec}
        except ValueError as exc:
            return {"error": "invalid_args", "message": str(exc)}
        return {
            "event_id": event.event_id,
            "spec": spec,
            "starts_at": event.started_at,
            "ends_at": event.ends_at,
            "targets": agent_ids,
        }

    def perturbation_queue_handler(command: ConsoleCommand) -> object:
        if scheduler is None:
            return {"error": "unsupported"}
        return scheduler.latest_state()

    def perturbation_trigger_handler(command: ConsoleCommand) -> object:
        if scheduler is None or world is None:
            return {"error": "unsupported"}
        if not command.args:
            return {
                "error": "usage",
                "message": (
                    "perturbation_trigger <spec> [--starts_in ticks] [--duration ticks] "
                    "[--targets a,b] [--magnitude value] [--location place]"
                ),
            }
        spec_name = str(command.args[0])
        starts_in = int(command.kwargs.get("starts_in", 0))
        duration_arg = command.kwargs.get("duration")
        duration = int(duration_arg) if duration_arg is not None else None
        targets_arg = command.kwargs.get("targets")
        targets = None
        if isinstance(targets_arg, str):
            targets = [item.strip() for item in targets_arg.split(",") if item.strip()]
        elif isinstance(targets_arg, (list, tuple)):
            targets = [str(item) for item in targets_arg]
        payload: dict[str, object] = {}
        if "magnitude" in command.kwargs:
            try:
                payload["magnitude"] = float(command.kwargs["magnitude"])
            except (TypeError, ValueError):
                return {"error": "invalid_args", "message": "magnitude must be numeric"}
        if "location" in command.kwargs:
            payload["location"] = str(command.kwargs["location"])
        try:
            event = scheduler.schedule_manual(
                world,
                spec_name=spec_name,
                current_tick=world.tick,
                starts_in=starts_in,
                duration=duration,
                targets=targets,
                payload_overrides=payload or None,
            )
        except KeyError:
            return {"error": "unknown_spec", "spec": spec_name}
        except ValueError as exc:
            return {"error": "invalid_args", "message": str(exc)}
        return {"enqueued": True, "event": scheduler.serialize_event(event)}

    def perturbation_cancel_handler(command: ConsoleCommand) -> object:
        if scheduler is None or world is None:
            return {"error": "unsupported"}
        if not command.args:
            return {
                "error": "usage",
                "message": "perturbation_cancel <event_id>",
            }
        event_id = str(command.args[0])
        cancelled = scheduler.cancel_event(world, event_id)
        return {"cancelled": cancelled, "event_id": event_id}

    def snapshot_inspect_handler(command: ConsoleCommand) -> object:
        path, error = _parse_snapshot_path(command, "snapshot_inspect <path>")
        if error:
            return error
        try:
            document = json.loads(path.read_text())
        except Exception as exc:
            return {"error": "read_failed", "message": str(exc), "path": str(path)}
        state_payload = document.get("state")
        if not isinstance(state_payload, dict):
            state_payload = {}
        return {
            "path": str(path),
            "schema_version": document.get("schema_version"),
            "config_id": state_payload.get("config_id"),
            "tick": state_payload.get("tick"),
            "identity": state_payload.get("identity", {}),
            "migrations": state_payload.get("migrations", {}),
        }

    def snapshot_validate_handler(command: ConsoleCommand) -> object:
        path, error = _parse_snapshot_path(command, "snapshot_validate <path> [--strict]")
        if error:
            return error
        cfg, cfg_error = _require_config()
        if cfg_error:
            return cfg_error
        manager = SnapshotManager(path.parent)
        strict = bool(command.kwargs.get("strict", False))
        allow_migration = (not strict) and cfg.snapshot.migrations.auto_apply
        try:
            state = manager.load(
                path,
                cfg,
                allow_migration=allow_migration,
                allow_downgrade=cfg.snapshot.guardrails.allow_downgrade,
                require_exact_config=cfg.snapshot.guardrails.require_exact_config,
            )
        except ValueError as exc:
            return {"valid": False, "error": str(exc), "path": str(path)}
        return {
            "valid": True,
            "config_id": state.config_id,
            "tick": state.tick,
            "migrations_applied": list(state.migrations.get("applied", [])),
        }

    def snapshot_migrate_handler(command: ConsoleCommand) -> object:
        path, error = _parse_snapshot_path(command, "snapshot_migrate <path> [--output dir]")
        if error:
            return error
        cfg, cfg_error = _require_config()
        if cfg_error:
            return cfg_error
        manager = SnapshotManager(path.parent)
        try:
            state = manager.load(
                path,
                cfg,
                allow_migration=True,
                allow_downgrade=cfg.snapshot.guardrails.allow_downgrade,
                require_exact_config=cfg.snapshot.guardrails.require_exact_config,
            )
        except ValueError as exc:
            return {
                "error": "migration_failed",
                "message": str(exc),
                "path": str(path),
            }
        applied = list(state.migrations.get("applied", []))
        publisher.record_snapshot_migrations(applied)
        output_arg = command.kwargs.get("output")
        saved_path: Path | None = None
        if output_arg is not None:
            output_dir, error = _resolve_snapshot_input(
                output_arg,
                require_exists=False,
                require_file=False,
            )
            if error:
                return error
            assert output_dir is not None
            if output_dir.suffix:
                return {
                    "error": "invalid_args",
                    "message": "output must be a directory path",
                }
            output_dir.mkdir(parents=True, exist_ok=True)
            out_manager = SnapshotManager(output_dir)
            saved_path = out_manager.save(state)
        result = {
            "migrated": True,
            "config_id": state.config_id,
            "tick": state.tick,
            "migrations_applied": applied,
        }
        if saved_path is not None:
            result["output_path"] = str(saved_path)
        return result

    router.register("conflict_status", conflict_status_handler)
    router.register("queue_inspect", queue_inspect_handler)
    router.register("rivalry_dump", rivalry_dump_handler)
    router.register("telemetry_snapshot", telemetry_handler)
    router.register("health_status", health_status_handler)
    router.register("employment_status", employment_status_handler)
    router.register("relationship_summary", relationship_summary_handler)
    router.register("social_events", social_events_handler)
    router.register("announce_story", announce_story_handler)
    router.register("affordance_status", affordance_status_handler)
    router.register("employment_exit", employment_exit_handler)
    router.register("promotion_status", promotion_status_handler)
    router.register("arrange_meet", arrange_meet_handler)
    router.register("perturbation_queue", perturbation_queue_handler)
    router.register("snapshot_inspect", snapshot_inspect_handler)
    router.register("snapshot_validate", snapshot_validate_handler)
    if mode == "admin":
        router.register("relationship_detail", relationship_detail_handler)
        router.register("possess", possess_handler)
        router.register("kill", kill_handler)
        router.register("toggle_mortality", toggle_mortality_handler)
        router.register("set_exit_cap", set_exit_cap_handler)
        router.register("set_spawn_delay", set_spawn_delay_handler)
        router.register("perturbation_trigger", perturbation_trigger_handler)
        router.register("perturbation_cancel", perturbation_cancel_handler)
        router.register("snapshot_migrate", snapshot_migrate_handler)
        router.register("promote_policy", promote_policy_handler)
        router.register("rollback_policy", rollback_policy_handler)
        router.register("policy_swap", policy_swap_handler)
    else:
        router.register("relationship_detail", _forbidden)
        router.register("possess", _forbidden)
        router.register("kill", _forbidden)
        router.register("toggle_mortality", _forbidden)
        router.register("set_exit_cap", _forbidden)
        router.register("set_spawn_delay", _forbidden)
        router.register("perturbation_trigger", _forbidden)
        router.register("perturbation_cancel", _forbidden)
        router.register("snapshot_migrate", _forbidden)
        router.register("promote_policy", _forbidden)
        router.register("rollback_policy", _forbidden)
        router.register("policy_swap", _forbidden)
    return router


def _schema_metadata(publisher: TelemetrySinkProtocol) -> tuple[str, str | None]:
    schema_fn = getattr(publisher, "schema", None)
    version = str(schema_fn()) if callable(schema_fn) else SUPPORTED_SCHEMA_PREFIX
    warning = None
    if not version.startswith(SUPPORTED_SCHEMA_PREFIX):
        warning = f"Console supports telemetry schema {SUPPORTED_SCHEMA_PREFIX}.x; shard reported {version}. Upgrade required."
    return version, warning

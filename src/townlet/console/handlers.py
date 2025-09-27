"""Console validation scaffolding."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from townlet.telemetry.publisher import TelemetryPublisher
    from townlet.world.grid import WorldState
    from townlet.scheduler.perturbations import PerturbationScheduler

SUPPORTED_SCHEMA_PREFIX = "0.8"
SUPPORTED_SCHEMA_LABEL = f"{SUPPORTED_SCHEMA_PREFIX}.x"


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
        self._handlers[name] = handler

    def dispatch(self, command: ConsoleCommand) -> object:
        handler = self._handlers.get(command.name)
        if handler is None:
            raise KeyError(f"Unknown console command: {command.name}")
        return handler(command)


class EventStream:
    """Simple subscriber that records the latest simulation events."""

    def __init__(self) -> None:
        self._latest: List[dict[str, object]] = []

    def connect(self, publisher: "TelemetryPublisher") -> None:
        publisher.register_event_subscriber(self._record)

    def _record(self, events: List[dict[str, object]]) -> None:
        self._latest = events

    def latest(self) -> List[dict[str, object]]:
        return list(self._latest)


class TelemetryBridge:
    """Provides access to the latest telemetry snapshots for console consumers."""

    def __init__(self, publisher: "TelemetryPublisher") -> None:
        self._publisher = publisher

    def snapshot(self) -> Dict[str, Dict[str, object]]:
        version, warning = _schema_metadata(self._publisher)
        return {
            "schema_version": version,
            "schema_warning": warning,
            "jobs": self._publisher.latest_job_snapshot(),
            "economy": self._publisher.latest_economy_snapshot(),
            "employment": self._publisher.latest_employment_metrics(),
            "conflict": self._publisher.latest_conflict_snapshot(),
            "relationships": self._publisher.latest_relationship_metrics() or {},
            "relationship_snapshot": self._publisher.latest_relationship_snapshot(),
            "relationship_updates": self._publisher.latest_relationship_updates(),
            "events": list(self._publisher.latest_events()),
            "anneal_status": self._publisher.latest_anneal_status(),
            "policy_snapshot": self._publisher.latest_policy_snapshot(),
            "affordance_manifest": self._publisher.latest_affordance_manifest(),
            "reward_breakdown": self._publisher.latest_reward_breakdown(),
            "stability": {
                "alerts": self._publisher.latest_stability_alerts(),
                "metrics": self._publisher.latest_stability_metrics(),
            },
            "perturbations": self._publisher.latest_perturbations(),
        }


def create_console_router(
    publisher: "TelemetryPublisher",
    world: "WorldState" | None = None,
    scheduler: "PerturbationScheduler" | None = None,
    *,
    mode: str = "viewer",
) -> ConsoleRouter:
    router = ConsoleRouter()
    bridge = TelemetryBridge(publisher)

    def telemetry_handler(command: ConsoleCommand) -> object:
        return bridge.snapshot()

    def employment_status_handler(command: ConsoleCommand) -> object:
        version, warning = _schema_metadata(publisher)
        metrics = publisher.latest_employment_metrics()
        return {
            "schema_version": version,
            "schema_warning": warning,
            "metrics": metrics,
            "pending_agents": metrics.get("pending", []),
        }

    def employment_exit_handler(command: ConsoleCommand) -> object:
        if world is None:
            raise RuntimeError("employment_exit requires world access")
        if not command.args:
            return {"error": "usage", "message": "employment_exit <approve|defer|review> [agent_id]"}
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
                "message": "perturbation_trigger <spec> [--starts_in ticks] [--duration ticks] [--targets a,b] [--magnitude value] [--location place]",
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
        payload: Dict[str, object] = {}
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

    router.register("telemetry_snapshot", telemetry_handler)
    router.register("employment_status", employment_status_handler)
    router.register("employment_exit", employment_exit_handler)
    router.register("perturbation_queue", perturbation_queue_handler)
    if mode == "admin":
        router.register("perturbation_trigger", perturbation_trigger_handler)
        router.register("perturbation_cancel", perturbation_cancel_handler)
    else:
        def _forbidden(_: ConsoleCommand) -> object:
            return {
                "error": "forbidden",
                "message": "command requires admin mode",
            }

        router.register("perturbation_trigger", _forbidden)
        router.register("perturbation_cancel", _forbidden)
    return router


def _schema_metadata(publisher: "TelemetryPublisher") -> tuple[str, str | None]:
    version = publisher.schema()
    warning = None
    if not version.startswith(SUPPORTED_SCHEMA_PREFIX):
        warning = (
            "Console supports telemetry schema "
            f"{SUPPORTED_SCHEMA_PREFIX}.x; shard reported {version}. Upgrade required."
        )
    return version, warning

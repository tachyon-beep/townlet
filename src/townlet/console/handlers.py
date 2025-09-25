"""Console validation scaffolding."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from townlet.telemetry.publisher import TelemetryPublisher
    from townlet.world.grid import WorldState

SUPPORTED_SCHEMA_PREFIX = "0.3"
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
            "events": list(self._publisher.latest_events()),
        }


def create_console_router(
    publisher: "TelemetryPublisher", world: "WorldState" | None = None
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

    router.register("telemetry_snapshot", telemetry_handler)
    router.register("employment_status", employment_status_handler)
    router.register("employment_exit", employment_exit_handler)
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

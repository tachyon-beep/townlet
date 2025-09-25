"""Console validation scaffolding."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from townlet.telemetry.publisher import TelemetryPublisher


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
        return {
            "jobs": self._publisher.latest_job_snapshot(),
            "economy": self._publisher.latest_economy_snapshot(),
            "events": list(self._publisher.latest_events()),
        }


def create_console_router(publisher: "TelemetryPublisher") -> ConsoleRouter:
    router = ConsoleRouter()
    bridge = TelemetryBridge(publisher)

    def telemetry_handler(command: ConsoleCommand) -> object:
        return bridge.snapshot()

    router.register("telemetry_snapshot", telemetry_handler)
    return router

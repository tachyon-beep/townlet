"""Console validation scaffolding."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol, TYPE_CHECKING

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

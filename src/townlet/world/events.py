"""Domain event definitions (skeleton)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List


@dataclass(frozen=True)
class Event:
    """Simple event record capturing type and payload."""

    type: str
    payload: dict[str, Any]


class EventDispatcher:
    """Placeholder dispatcher that will fan out events to listeners."""

    def __init__(self) -> None:
        self._buffer: List[Event] = []

    def emit(self, event: Event) -> None:
        raise NotImplementedError("EventDispatcher.emit pending WP2 implementation")

    def drain(self) -> Iterable[Event]:
        raise NotImplementedError("EventDispatcher.drain pending WP2 implementation")


__all__ = ["Event", "EventDispatcher"]

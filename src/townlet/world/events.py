"""Domain event primitives shared by world systems and orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from time import time
from typing import Any, Callable, Iterable, Mapping, MutableSequence, Protocol

EventPayload = Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class Event:
    """Structured world event following the ADR-002 schema."""

    type: str
    payload: EventPayload
    tick: int | None = None
    ts: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialise the event into the canonical mapping form."""

        result: dict[str, Any] = {"type": self.type, "payload": dict(self.payload)}
        if self.tick is not None:
            result["tick"] = self.tick
        if self.ts is not None:
            result["ts"] = self.ts
        return result


class EventListener(Protocol):
    """Callable signature for event subscribers."""

    def __call__(self, event: Event) -> None:  # pragma: no cover - protocol stub
        ...


class EventDispatcher:
    """Collects events and optionally fans them out to listeners."""

    def __init__(self) -> None:
        self._buffer: MutableSequence[Event] = []
        self._listeners: list[EventListener] = []

    def register(self, listener: EventListener) -> None:
        """Attach a listener invoked for every emitted event."""

        if listener not in self._listeners:
            self._listeners.append(listener)

    def emit(
        self,
        *,
        type: str,
        payload: EventPayload | None = None,
        tick: int | None = None,
        ts: float | None = None,
    ) -> Event:
        """Create an event and enqueue it for later draining."""

        event = Event(
            type=type,
            payload=payload or {},
            tick=tick,
            ts=ts if ts is not None else time(),
        )
        self._buffer.append(event)
        for listener in tuple(self._listeners):
            listener(event)
        return event

    def drain(self) -> list[Event]:
        """Return buffered events in emission order and clear the queue."""

        events = list(self._buffer)
        self._buffer.clear()
        return events

    def clear(self) -> None:
        """Discard any buffered events without returning them."""

        self._buffer.clear()

    def __len__(self) -> int:
        return len(self._buffer)


__all__ = ["Event", "EventDispatcher", "EventListener", "EventPayload"]

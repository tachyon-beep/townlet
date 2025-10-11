from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Dict, List


class DummyTelemetrySink:
    """In-memory telemetry sink useful for tests and dummies."""

    def __init__(self) -> None:
        self.started = False
        self.stopped = False
        self.events: List[tuple[str, dict[str, Any]]] = []
        self.metrics: List[tuple[str, float, dict[str, Any]]] = []
        self._transport_status: dict[str, Any] = {
            "provider": "dummy",
            "queue_length": 0,
            "dropped_messages": 0,
            "last_flush_duration_ms": None,
        }

    def start(self) -> None:
        self.started = True
        self.stopped = False

    def stop(self) -> None:
        self.stopped = True

    def emit_event(self, name: str, payload: Mapping[str, Any] | None = None) -> None:
        event_payload = dict(payload) if isinstance(payload, Mapping) else {}
        self.events.append((name, event_payload))

    def emit_metric(self, name: str, value: float, **tags: Any) -> None:
        self.metrics.append((name, float(value), dict(tags)))

    def transport_status(self) -> Mapping[str, Any]:
        return dict(self._transport_status)

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from townlet.dto.telemetry import TelemetryEventDTO


class DummyTelemetrySink:
    """In-memory telemetry sink useful for tests and dummies."""

    def __init__(self) -> None:
        self.started = False
        self.stopped = False
        self.events: list[tuple[str, dict[str, Any]]] = []
        self.metrics: list[tuple[str, float, dict[str, Any]]] = []
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

    def emit_event(self, event: TelemetryEventDTO) -> None:
        """Accept a typed telemetry event and store it for inspection.

        Args:
            event: TelemetryEventDTO containing event_type, tick, and payload.
        """
        self.events.append((event.event_type, dict(event.payload)))

    def emit_metric(self, name: str, value: float, **tags: Any) -> None:
        self.metrics.append((name, float(value), dict(tags)))

    def transport_status(self) -> Mapping[str, Any]:
        return dict(self._transport_status)

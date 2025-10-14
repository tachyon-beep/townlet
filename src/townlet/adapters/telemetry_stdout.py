"""Adapter exposing telemetry publisher via the minimal telemetry port."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from townlet.dto.telemetry import TelemetryEventDTO
from townlet.ports.telemetry import TelemetrySink
from townlet.telemetry.publisher import TelemetryPublisher


class StdoutTelemetryAdapter(TelemetrySink):
    """Wrap `TelemetryPublisher` and expose start/stop + generic emits."""

    def __init__(self, publisher: TelemetryPublisher) -> None:
        self._publisher = publisher
        self._started = False

    def start(self) -> None:
        if hasattr(self._publisher, "start_worker"):
            self._publisher.start_worker()
        self._started = True

    def stop(self) -> None:
        if hasattr(self._publisher, "stop_worker"):
            self._publisher.stop_worker()
        if hasattr(self._publisher, "close"):
            self._publisher.close()
        self._started = False

    def emit_event(self, event: TelemetryEventDTO) -> None:
        """Forward typed event to the publisher's internal event dispatcher.

        Args:
            event: TelemetryEventDTO containing event_type, tick, and payload.
        """
        self._publisher.event_dispatcher.emit_event(event.event_type, event.payload)

    def emit_metric(self, name: str, value: float, **tags: Any) -> None:
        metrics = self._publisher._latest_health_status
        metrics[name] = {
            "value": float(value),
            "tags": dict(tags),
        }

    def transport_status(self) -> Mapping[str, Any]:
        """Expose the publisher transport status snapshot."""

        getter = getattr(self._publisher, "latest_transport_status", None)
        if callable(getter):
            try:
                return dict(getter())
            except Exception:  # pragma: no cover - defensive
                return {}
        return {}

    @property
    def publisher(self) -> TelemetryPublisher:
        """Expose the wrapped telemetry publisher for transitional call sites."""

        return self._publisher


__all__ = ["StdoutTelemetryAdapter"]

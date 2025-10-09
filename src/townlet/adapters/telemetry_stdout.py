"""Adapter exposing telemetry publisher via the minimal telemetry port."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

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

    def emit_event(self, name: str, payload: Mapping[str, Any] | None = None) -> None:
        self._publisher.event_dispatcher.emit_event(name, payload)

    def emit_metric(self, name: str, value: float, **tags: Any) -> None:
        metrics = self._publisher._latest_health_status  # type: ignore[attr-defined]
        metrics[name] = {
            "value": float(value),
            "tags": dict(tags),
        }

    @property
    def publisher(self) -> TelemetryPublisher:
        """Expose the wrapped telemetry publisher for transitional call sites."""

        return self._publisher


__all__ = ["StdoutTelemetryAdapter"]

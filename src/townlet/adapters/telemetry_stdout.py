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
        if name == "loop.tick":
            if not isinstance(payload, Mapping):
                raise TypeError("loop.tick payload must be a mapping")
            self._publisher.publish_tick(**payload)
            return
        self._publisher._latest_events.append(  # type: ignore[attr-defined]
            {
                "type": name,
                "payload": dict(payload or {}),
            }
        )

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

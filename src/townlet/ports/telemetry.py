"""Protocol defining the telemetry sink surface."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol


class TelemetrySink(Protocol):
    """Emit telemetry events and metrics from the simulation loop."""

    def start(self) -> None:
        """Initialise telemetry resources prior to the first tick."""

    def stop(self) -> None:
        """Tear down telemetry resources during shutdown."""

    def emit_event(self, name: str, payload: Mapping[str, Any] | None = None) -> None:
        """Publish a telemetry event with the provided payload."""

    def emit_metric(self, name: str, value: float, **tags: Any) -> None:
        """Record a telemetry metric with optional tag values."""

    def transport_status(self) -> Mapping[str, Any]:
        """Return the latest transport health/backlog measurements."""


__all__ = ["TelemetrySink"]

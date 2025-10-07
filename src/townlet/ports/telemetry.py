"""Protocol describing the telemetry sink consumed by the simulation loop."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol


class TelemetrySink(Protocol):
    """Lifecycle-aware telemetry output used by the simulation loop."""

    def start(self) -> None:
        """Initialise the telemetry sink before ticks begin."""

    def stop(self) -> None:
        """Tear down the telemetry sink once the run completes."""

    def emit_event(self, name: str, payload: Mapping[str, Any] | None = None) -> None:
        """Emit an event with ``name`` and optional ``payload`` mapping."""

    def emit_metric(self, name: str, value: float, **tags: Any) -> None:
        """Emit a numeric metric identified by ``name`` and ``value``."""

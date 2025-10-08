"""Telemetry sink port."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol


class TelemetrySink(Protocol):
    """Port describing the telemetry lifecycle and emission surface."""

    def start(self) -> None:
        """Initialise the telemetry sink."""

    def stop(self) -> None:
        """Tear down the telemetry sink."""

    def emit_event(self, name: str, payload: Mapping[str, Any] | None = None) -> None:
        """Emit an event with the provided payload."""

    def emit_metric(self, name: str, value: float, **tags: Any) -> None:
        """Emit a numeric metric with optional tags."""

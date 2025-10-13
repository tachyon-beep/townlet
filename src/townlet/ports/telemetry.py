"""Protocol defining the telemetry sink surface.

This module defines the TelemetrySink port protocol for emitting telemetry events and
metrics from the simulation loop. The protocol enforces typed DTO boundaries for all
telemetry data, ensuring type safety and validation.

Implementations:
    - TelemetryPublisher (main implementation with buffering/transport)
    - DummyTelemetrySink (testing stub)
    - StdoutTelemetrySink (simple console output)

See Also:
    - ADR-001: Port and Factory Registry
    - ADR-003: DTO Boundary specification
    - townlet.dto.telemetry for DTO definitions
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:  # pragma: no cover
    from townlet.dto.telemetry import TelemetryEventDTO


class TelemetrySink(Protocol):
    """Emit telemetry events and metrics from the simulation loop.

    This protocol defines the interface for telemetry sinks that receive events and metrics
    from the simulation. All telemetry implementations must satisfy this protocol.

    DTO Enforcement:
        - emit_event() accepts TelemetryEventDTO (townlet.dto.telemetry)
        - All telemetry events use typed DTOs rather than raw dicts
    """

    def start(self) -> None:
        """Initialise telemetry resources prior to the first tick.

        This method is called once before the simulation begins. Implementations should
        set up any required resources (network connections, file handles, buffers, etc.).
        """

    def stop(self) -> None:
        """Tear down telemetry resources during shutdown.

        This method is called once after the simulation ends. Implementations should clean
        up resources and flush any buffered data.
        """

    def emit_event(self, event: TelemetryEventDTO) -> None:
        """Publish a typed telemetry event.

        Args:
            event: TelemetryEventDTO containing event_type, tick, payload, and metadata.

        Example:
            ```python
            from townlet.dto.telemetry import TelemetryEventDTO, TelemetryMetadata

            event = TelemetryEventDTO(
                event_type="loop.tick",
                tick=42,
                payload={"duration_ms": 15.3},
                metadata=TelemetryMetadata(),
            )
            sink.emit_event(event)
            ```
        """

    def emit_metric(self, name: str, value: float, **tags: Any) -> None:
        """Record a telemetry metric with optional tag values.

        Args:
            name: Metric identifier (e.g., "reward.mean", "queue.length").
            value: Numeric metric value.
            **tags: Optional tags for metric dimensions (agent_id, object_id, etc.).
        """

    def transport_status(self) -> Mapping[str, Any]:
        """Return the latest transport health/backlog measurements.

        Returns:
            Dict containing transport status keys:
                - queue_length: Number of buffered events
                - dropped_messages: Count of dropped events due to backpressure
                - provider: Transport implementation name
        """


__all__ = ["TelemetrySink"]

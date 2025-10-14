"""Protocols and shared types for the refactored telemetry pipeline (WP-D).

This module defines the contracts between the telemetry aggregation, transform,
and transport layers. The `SimulationLoop` will interact with these protocols via
`TelemetrySinkProtocol` once WP-D lands, enabling different pipeline
implementations without touching the core loop.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Protocol, TypeAlias, runtime_checkable

from townlet.core.interfaces import RewardMapping

if TYPE_CHECKING:  # pragma: no cover
    from townlet.console.command import ConsoleCommandResult
    from townlet.world.grid import WorldState

TelemetryPayload: TypeAlias = Mapping[str, object]
TelemetryMetadata: TypeAlias = Mapping[str, object]
TelemetryEventKind: TypeAlias = Literal[
    "snapshot",
    "diff",
    "event",
    "health",
    "console",
    "narration",
]
TelemetryEventBatch: TypeAlias = Sequence["TelemetryEvent"]


@dataclass(slots=True)
class TelemetryEvent:
    """Canonical telemetry event emitted by the aggregation layer."""

    tick: int
    kind: TelemetryEventKind
    payload: TelemetryPayload
    metadata: TelemetryMetadata = field(default_factory=dict)


@runtime_checkable
class TelemetryAggregationProtocol(Protocol):
    """Produce telemetry events for a simulation tick."""

    def collect_tick(
        self,
        *,
        tick: int,
        world: WorldState,
        rewards: RewardMapping,
        events: Iterable[Mapping[str, object]] | None = None,
        policy_snapshot: Mapping[str, Mapping[str, object]] | None = None,
        kpi_history: bool = False,
        reward_breakdown: Mapping[str, Mapping[str, float]] | None = None,
        stability_inputs: Mapping[str, object] | None = None,
        perturbations: Mapping[str, object] | None = None,
        policy_identity: Mapping[str, object] | None = None,
        possessed_agents: Iterable[str] | None = None,
        social_events: Iterable[Mapping[str, object]] | None = None,
        runtime_variant: str | None = None,
    ) -> Iterable[TelemetryEvent]:
        """Aggregate world artefacts into telemetry events for the tick."""

    def record_console_results(self, results: Iterable[ConsoleCommandResult]) -> None:
        """Capture console outputs so they can be emitted as telemetry events."""

    def record_loop_failure(self, payload: Mapping[str, object]) -> Iterable[TelemetryEvent]:
        """Emit events describing a simulation loop failure."""


@runtime_checkable
class TelemetryTransformProtocol(Protocol):
    """Transform or filter telemetry events prior to transport."""

    def process(self, event: TelemetryEvent) -> TelemetryEvent | None:
        """Return the transformed event or ``None`` to drop it."""

    def flush(self) -> Iterable[TelemetryEvent]:
        """Flush any buffered events (e.g., batched diffs)."""


@runtime_checkable
class TelemetryTransportProtocol(Protocol):
    """Ship telemetry events to an external sink."""

    def start(self) -> None:
        """Initialise transport resources (threads, sockets, file handles)."""

    def send(self, events: Iterable[TelemetryEvent]) -> None:
        """Send the provided events. Implementations may batch internally."""

    def flush(self) -> None:
        """Force any buffered payloads to be transmitted."""

    def close(self) -> None:
        """Tear down transport resources and ensure graceful shutdown."""

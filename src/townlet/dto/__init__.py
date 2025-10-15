"""Data Transfer Objects for typed boundaries across Townlet subsystems.

This package contains Pydantic v2 models defining typed interfaces between:
- World state and simulation loop (WorldSnapshot, AgentSummary)
- Observations and policy (ObservationEnvelope, AgentObservationDTO)
- Rewards and training (RewardBreakdown, RewardComponent)
- Telemetry and monitoring (TelemetryEventDTO, ConsoleEventDTO)

All DTOs support serialization via `.model_dump()` for transport/persistence.
"""

from __future__ import annotations

from .observations import AgentObservationDTO, ObservationEnvelope, ObservationMetadata
from .rewards import RewardBreakdown, RewardComponent
from .telemetry import ConsoleEventDTO, TelemetryEventDTO, TelemetryMetadata
from .world import (
    AffordanceSnapshot,
    AgentSummary,
    EmbeddingSnapshot,
    EmploymentSnapshot,
    IdentitySnapshot,
    LifecycleSnapshot,
    MigrationSnapshot,
    PerturbationSnapshot,
    PromotionSnapshot,
    QueueSnapshot,
    SimulationSnapshot,
    StabilitySnapshot,
    TelemetrySnapshot,
    WorldSnapshot,  # Legacy alias
)

__all__ = [
    # Observations
    "ObservationEnvelope",
    "AgentObservationDTO",
    "ObservationMetadata",
    # Simulation Snapshot (primary)
    "SimulationSnapshot",
    # World components
    "AgentSummary",
    "QueueSnapshot",
    "EmploymentSnapshot",
    # Subsystem snapshots
    "LifecycleSnapshot",
    "PerturbationSnapshot",
    "AffordanceSnapshot",
    "EmbeddingSnapshot",
    "StabilitySnapshot",
    "PromotionSnapshot",
    "TelemetrySnapshot",
    # Metadata
    "IdentitySnapshot",
    "MigrationSnapshot",
    # Rewards
    "RewardBreakdown",
    "RewardComponent",
    # Telemetry
    "TelemetryEventDTO",
    "TelemetryMetadata",
    "ConsoleEventDTO",
    # Legacy (deprecated)
    "WorldSnapshot",
]

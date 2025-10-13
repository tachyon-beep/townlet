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
from .world import AgentSummary, EmploymentSnapshot, QueueSnapshot, WorldSnapshot

__all__ = [
    # Observations
    "ObservationEnvelope",
    "AgentObservationDTO",
    "ObservationMetadata",
    # World
    "WorldSnapshot",
    "AgentSummary",
    "QueueSnapshot",
    "EmploymentSnapshot",
    # Rewards
    "RewardBreakdown",
    "RewardComponent",
    # Telemetry
    "TelemetryEventDTO",
    "TelemetryMetadata",
    "ConsoleEventDTO",
]

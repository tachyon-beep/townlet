"""World and simulation snapshot DTOs.

This module provides Pydantic models for complete simulation state snapshots.
SimulationSnapshot replaces the legacy SnapshotState dataclass with proper
validation, nested DTOs, and type safety.

Design Pattern:
    - Nested DTOs for each subsystem (lifecycle, perturbations, etc.)
    - Full Pydantic validation on save/load
    - Serialization via model_dump() for JSON persistence
    - Type-safe restoration via model_validate()

This pattern serves as a reference implementation for other DTO boundaries.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AgentSummary(BaseModel):
    """Summary of agent state for snapshots."""

    agent_id: str
    position: tuple[int, int]
    needs: dict[str, float]
    wallet: float
    job_id: str | None = None
    on_shift: bool = False
    inventory: dict[str, int] = Field(default_factory=dict)
    personality: dict[str, float] = Field(default_factory=dict)
    personality_profile: str = "balanced"
    lateness_counter: int = 0
    last_late_tick: int = -1
    shift_state: str = "pre_shift"
    late_ticks_today: int = 0
    attendance_ratio: float = 1.0
    absent_shifts_7d: int = 0
    wages_withheld: float = 0.0
    exit_pending: bool = False


class QueueSnapshot(BaseModel):
    """State of resource queue system."""

    active: dict[str, str] = Field(default_factory=dict)  # object_id → agent_id
    queues: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)
    cooldowns: list[dict[str, Any]] = Field(default_factory=list)
    stall_counts: dict[str, int] = Field(default_factory=dict)


class EmploymentSnapshot(BaseModel):
    """State of employment subsystem."""

    exit_queue: list[str] = Field(default_factory=list)
    queue_timestamps: dict[str, int] = Field(default_factory=dict)
    manual_exits: list[str] = Field(default_factory=list)
    exits_today: int = 0


class LifecycleSnapshot(BaseModel):
    """State of lifecycle manager (spawns, exits, mortality)."""

    exits_today: int = 0
    employment_day: int = -1


class PerturbationSnapshot(BaseModel):
    """State of perturbation scheduler (events, active disruptions)."""

    pending: list[dict[str, Any]] = Field(default_factory=list)
    active: dict[str, dict[str, Any]] = Field(default_factory=dict)


class AffordanceSnapshot(BaseModel):
    """State of affordance runtime (running actions per object)."""

    running: dict[str, dict[str, Any]] = Field(default_factory=dict)


class EmbeddingSnapshot(BaseModel):
    """State of embedding allocator (agent slot assignments)."""

    assignments: dict[str, int] = Field(default_factory=dict)
    available: list[int] = Field(default_factory=list)


class StabilitySnapshot(BaseModel):
    """State of stability monitor (starvation tracking, metrics)."""

    starvation_streaks: dict[str, int] = Field(default_factory=dict)
    starvation_active: list[str] = Field(default_factory=list)
    starvation_incidents: list[tuple[int, str]] = Field(default_factory=list)
    latest_metrics: dict[str, Any] = Field(default_factory=dict)


class PromotionSnapshot(BaseModel):
    """State of promotion manager (A/B gate, pass streaks)."""

    state: str = "monitoring"
    pass_streak: int = 0
    required_passes: int = 2
    candidate_ready: bool = False


class TelemetrySnapshot(BaseModel):
    """State of telemetry publisher (cached metrics, snapshots)."""

    queue_metrics: dict[str, int] = Field(default_factory=dict)
    embedding_metrics: dict[str, float] = Field(default_factory=dict)
    conflict_snapshot: dict[str, Any] = Field(default_factory=dict)
    relationship_metrics: dict[str, Any] = Field(default_factory=dict)
    job_snapshot: dict[str, dict[str, Any]] = Field(default_factory=dict)
    economy_snapshot: dict[str, Any] = Field(default_factory=dict)
    relationship_snapshot: dict[str, dict[str, dict[str, float]]] = Field(default_factory=dict)


class IdentitySnapshot(BaseModel):
    """Identity metadata for snapshot compatibility checks."""

    config_id: str
    policy_hash: str | None = None
    observation_variant: str | None = None
    anneal_ratio: float | None = None
    policy_artifact: str | None = None


class MigrationSnapshot(BaseModel):
    """Migration tracking for snapshot version upgrades."""

    applied: list[str] = Field(default_factory=list)
    required: list[str] = Field(default_factory=list)


class SimulationSnapshot(BaseModel):
    """Complete simulation state snapshot for serialization/restore.

    This DTO replaces the legacy SnapshotState dataclass with proper
    Pydantic validation and nested DTOs for type safety.

    Design Pattern:
        - Nested DTOs for each subsystem (lifecycle, perturbations, etc.)
        - Full validation on save/load via Pydantic
        - Serialization: snapshot.model_dump() → dict
        - Deserialization: SimulationSnapshot.model_validate(dict) → snapshot
        - Allow mutation for restoration (frozen=False)

    Example:
        ```python
        # Save
        snapshot = SimulationSnapshot(config_id="abc123", tick=42, ...)
        data = snapshot.model_dump()
        Path("snapshot.json").write_text(json.dumps(data))

        # Load
        data = json.loads(Path("snapshot.json").read_text())
        snapshot = SimulationSnapshot.model_validate(data)
        ```
    """

    model_config = ConfigDict(frozen=False, validate_assignment=True)

    # Core identity
    config_id: str
    tick: int
    ticks_per_day: int = 1440

    # World state
    agents: dict[str, AgentSummary]
    objects: dict[str, dict[str, Any]]
    queues: QueueSnapshot
    employment: EmploymentSnapshot
    relationships: dict[str, dict[str, dict[str, float]]] = Field(default_factory=dict)
    relationship_metrics: dict[str, Any] = Field(default_factory=dict)

    # Subsystem state
    lifecycle: LifecycleSnapshot = Field(default_factory=LifecycleSnapshot)
    perturbations: PerturbationSnapshot = Field(default_factory=PerturbationSnapshot)
    affordances: AffordanceSnapshot = Field(default_factory=AffordanceSnapshot)
    embeddings: EmbeddingSnapshot = Field(default_factory=EmbeddingSnapshot)
    stability: StabilitySnapshot = Field(default_factory=StabilitySnapshot)
    promotion: PromotionSnapshot = Field(default_factory=PromotionSnapshot)
    telemetry: TelemetrySnapshot = Field(default_factory=TelemetrySnapshot)

    # RNG streams
    rng_state: str | None = None  # Legacy field (use rng_streams["world"])
    rng_streams: dict[str, str] = Field(default_factory=dict)

    # Console buffer (pending commands)
    console_buffer: list[Any] = Field(default_factory=list)

    # Metadata
    identity: IdentitySnapshot
    migrations: MigrationSnapshot = Field(default_factory=MigrationSnapshot)


__all__ = [
    # Agent/World components
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
    # Top-level snapshot
    "SimulationSnapshot",
    # Legacy alias (deprecated, will be removed)
    "WorldSnapshot",
]

# Backward compatibility alias (will be removed in future)
WorldSnapshot = SimulationSnapshot

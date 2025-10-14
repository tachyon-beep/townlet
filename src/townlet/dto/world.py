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

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AgentSummary(BaseModel):
    """Summary of agent state for snapshots.

    Validates agent state consistency at snapshot boundaries.
    """

    agent_id: str = Field(..., min_length=1, description="Unique agent identifier")
    position: tuple[int, int] = Field(..., description="Agent position (x, y) on grid")
    needs: dict[str, float] = Field(..., description="Agent needs (hunger, hygiene, energy)")
    wallet: float = Field(..., ge=0.0, description="Agent wallet balance (must be >= 0)")
    job_id: str | None = Field(None, description="Current job assignment")
    on_shift: bool = Field(False, description="Whether agent is currently on shift")
    inventory: dict[str, int] = Field(default_factory=dict, description="Agent inventory items")
    personality: dict[str, float] = Field(default_factory=dict, description="Personality traits")
    personality_profile: str = Field("balanced", min_length=1, description="Personality profile name")
    lateness_counter: int = Field(0, ge=0, description="Cumulative lateness counter")
    last_late_tick: int = Field(-1, ge=-1, description="Last tick agent was late")
    shift_state: str = Field("pre_shift", min_length=1, description="Current shift state")
    late_ticks_today: int = Field(0, ge=0, description="Ticks late today")
    attendance_ratio: float = Field(1.0, ge=0.0, le=1.0, description="Attendance ratio (0-1)")
    absent_shifts_7d: int = Field(0, ge=0, description="Absent shifts in last 7 days")
    wages_withheld: float = Field(0.0, ge=0.0, description="Withheld wages for lateness")
    exit_pending: bool = Field(False, description="Whether agent exit is pending")

    @field_validator("position")
    @classmethod
    def validate_position(cls, v: tuple[int, int]) -> tuple[int, int]:
        """Ensure position is valid (x >= 0, y >= 0)."""
        if len(v) != 2:
            raise ValueError(f"Position must be 2-tuple, got {len(v)} elements")
        x, y = v
        if x < 0 or y < 0:
            raise ValueError(f"Position must be non-negative, got ({x}, {y})")
        return v

    @field_validator("needs")
    @classmethod
    def validate_needs(cls, v: dict[str, float]) -> dict[str, float]:
        """Ensure need values are in [0, 1] range."""
        for need_name, need_value in v.items():
            if not (0.0 <= need_value <= 1.0):
                raise ValueError(
                    f"Need '{need_name}' must be in [0, 1], got {need_value}"
                )
        return v


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
        - Strict validation for critical fields (tick >= 0, valid config_id)

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

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        str_strip_whitespace=True,
        validate_default=True,
    )

    # Core identity
    config_id: str = Field(..., min_length=1, description="Configuration hash identifier")
    tick: int = Field(..., ge=0, description="Current simulation tick (must be >= 0)")
    ticks_per_day: int = Field(1440, ge=1, le=86400, description="Ticks per day (1-86400)")

    # World state
    agents: dict[str, AgentSummary] = Field(..., description="Agent state indexed by agent_id")
    objects: dict[str, dict[str, Any]] = Field(..., description="Interactive objects (stores, beds, etc)")
    queues: QueueSnapshot = Field(..., description="Resource queue state")
    employment: EmploymentSnapshot = Field(..., description="Employment subsystem state")
    relationships: dict[str, dict[str, dict[str, float]]] = Field(
        default_factory=dict,
        description="Agent relationship values (owner → target → values)"
    )
    relationship_metrics: dict[str, Any] = Field(
        default_factory=dict,
        description="Cached relationship metrics"
    )

    # Subsystem state
    lifecycle: LifecycleSnapshot = Field(
        default_factory=LifecycleSnapshot,
        description="Lifecycle manager state (spawns, exits)"
    )
    perturbations: PerturbationSnapshot = Field(
        default_factory=PerturbationSnapshot,
        description="Perturbation scheduler state (active events)"
    )
    affordances: AffordanceSnapshot = Field(
        default_factory=AffordanceSnapshot,
        description="Affordance runtime state (running actions)"
    )
    embeddings: EmbeddingSnapshot = Field(
        default_factory=EmbeddingSnapshot,
        description="Embedding allocator state (agent slots)"
    )
    stability: StabilitySnapshot = Field(
        default_factory=StabilitySnapshot,
        description="Stability monitor state (starvation tracking)"
    )
    promotion: PromotionSnapshot = Field(
        default_factory=PromotionSnapshot,
        description="Promotion manager state (A/B gate)"
    )
    telemetry: TelemetrySnapshot = Field(
        default_factory=TelemetrySnapshot,
        description="Telemetry publisher state (cached metrics)"
    )

    # RNG streams
    rng_state: str | None = Field(
        None,
        description="Legacy RNG state (deprecated, use rng_streams['world'])"
    )
    rng_streams: dict[str, str] = Field(
        default_factory=dict,
        description="Named RNG streams (world, events, policy, context_seed)"
    )

    # Console buffer (pending commands)
    console_buffer: list[Any] = Field(
        default_factory=list,
        description="Buffered console commands pending execution"
    )

    # Metadata
    identity: IdentitySnapshot = Field(..., description="Identity metadata for compatibility checks")
    migrations: MigrationSnapshot = Field(
        default_factory=MigrationSnapshot,
        description="Migration tracking metadata"
    )

    @field_validator("config_id")
    @classmethod
    def validate_config_id(cls, v: str) -> str:
        """Ensure config_id is non-empty after stripping."""
        if not v or not v.strip():
            raise ValueError("config_id must be non-empty")
        return v.strip()

    @field_validator("agents")
    @classmethod
    def validate_agents(cls, v: dict[str, AgentSummary]) -> dict[str, AgentSummary]:
        """Ensure all agent_ids match their keys."""
        for agent_id, agent_summary in v.items():
            if agent_summary.agent_id != agent_id:
                raise ValueError(
                    f"Agent key mismatch: key='{agent_id}' but agent_id='{agent_summary.agent_id}'"
                )
        return v

    @field_validator("rng_streams")
    @classmethod
    def validate_rng_streams(cls, v: dict[str, str]) -> dict[str, str]:
        """Ensure RNG streams contain valid JSON payloads."""
        import json
        for stream_name, payload in v.items():
            if not isinstance(payload, str):
                raise ValueError(f"RNG stream '{stream_name}' must be JSON string")
            try:
                # Validate it's parseable JSON
                json.loads(payload)
            except json.JSONDecodeError as exc:
                raise ValueError(f"RNG stream '{stream_name}' contains invalid JSON: {exc}") from exc
        return v

    @model_validator(mode="after")
    def validate_rng_consistency(self) -> SimulationSnapshot:
        """Ensure at least one RNG stream is present."""
        if not self.rng_state and not self.rng_streams:
            raise ValueError("Snapshot must contain either rng_state or rng_streams")
        return self


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

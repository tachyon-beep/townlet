"""World state snapshot DTOs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


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
    lateness_counter: int = 0
    last_late_tick: int | None = None
    shift_state: str | None = None
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


class WorldSnapshot(BaseModel):
    """Complete world state snapshot for serialization/restore."""

    tick: int
    ticks_per_day: int
    agents: dict[str, AgentSummary]
    objects: dict[str, dict[str, Any]]  # object_id → object state
    queues: QueueSnapshot
    employment: EmploymentSnapshot
    relationships: dict[str, dict[str, dict[str, float]]] = Field(default_factory=dict)
    embeddings: dict[str, Any] = Field(default_factory=dict)
    events: list[dict[str, Any]] = Field(default_factory=list)
    rng_state: str | None = None  # Encoded RNG state
    rng_streams: dict[str, str] = Field(default_factory=dict)  # Stream name → encoded state

    class Config:
        frozen = False  # Allow mutation for restoration


__all__ = ["WorldSnapshot", "AgentSummary", "QueueSnapshot", "EmploymentSnapshot"]

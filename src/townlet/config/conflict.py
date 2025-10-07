"""Conflict and fairness configuration models."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class QueueFairnessConfig(BaseModel):
    """Queue fairness tuning parameters (see REQUIREMENTS#5)."""

    cooldown_ticks: int = Field(60, ge=0, le=600)
    ghost_step_after: int = Field(3, ge=0, le=100)
    age_priority_weight: float = Field(0.1, ge=0.0, le=1.0)


class RivalryConfig(BaseModel):
    """Conflict/rivalry tuning knobs (see REQUIREMENTS#5)."""

    increment_per_conflict: float = Field(0.15, ge=0.0, le=1.0)
    decay_per_tick: float = Field(0.005, ge=0.0, le=1.0)
    min_value: float = Field(0.0, ge=0.0, le=1.0)
    max_value: float = Field(1.0, ge=0.0, le=1.0)
    avoid_threshold: float = Field(0.7, ge=0.0, le=1.0)
    eviction_threshold: float = Field(0.05, ge=0.0, le=1.0)
    max_edges: int = Field(6, ge=1, le=32)
    ghost_step_boost: float = Field(1.5, ge=0.0, le=5.0)
    handover_boost: float = Field(0.4, ge=0.0, le=5.0)
    queue_length_boost: float = Field(0.25, ge=0.0, le=2.0)

    @model_validator(mode="after")
    def _validate_ranges(self) -> RivalryConfig:
        if self.min_value > self.max_value:
            raise ValueError("rivalry.min_value must be <= max_value")
        if self.avoid_threshold < self.min_value or self.avoid_threshold > self.max_value:
            raise ValueError("rivalry.avoid_threshold must lie within [min_value, max_value]")
        if self.eviction_threshold < self.min_value or self.eviction_threshold > self.max_value:
            raise ValueError("rivalry.eviction_threshold must lie within [min_value, max_value]")
        return self


class ConflictConfig(BaseModel):
    rivalry: RivalryConfig = RivalryConfig()


__all__ = [
    "ConflictConfig",
    "QueueFairnessConfig",
    "RivalryConfig",
]


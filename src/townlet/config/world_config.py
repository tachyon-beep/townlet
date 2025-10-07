"""World-related configuration models (affordances, employment, behaviour, lifecycle)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AffordanceRuntimeConfig(BaseModel):
    """Runtime affordance tuning flags."""

    factory: str | None = None
    instrumentation: Literal["off", "timings"] = "off"
    options: dict[str, object] = Field(default_factory=dict)
    hook_allowlist: tuple[str, ...] = Field(default_factory=tuple)
    allow_env_hooks: bool = True

    model_config = ConfigDict(extra="allow")


class AffordanceConfig(BaseModel):
    """Top-level affordance configuration (manifest + runtime)."""

    affordances_file: str = Field("configs/affordances/core.yaml")
    runtime: AffordanceRuntimeConfig = AffordanceRuntimeConfig()


class EmploymentConfig(BaseModel):
    """Employment system knobs for queues and wages."""

    grace_ticks: int = Field(5, ge=0, le=120)
    absent_cutoff: int = Field(30, ge=0, le=600)
    absence_slack: int = Field(20, ge=0, le=600)
    late_tick_penalty: float = Field(0.005, ge=0.0, le=1.0)
    absence_penalty: float = Field(0.2, ge=0.0, le=5.0)
    max_absent_shifts: int = Field(3, ge=0, le=20)
    attendance_window: int = Field(3, ge=1, le=14)
    daily_exit_cap: int = Field(2, ge=0, le=50)
    exit_queue_limit: int = Field(8, ge=0, le=100)
    exit_review_window: int = Field(1440, ge=1, le=100000)
    enforce_job_loop: bool = False


class BehaviorConfig(BaseModel):
    """Configuration namespace for scripted behaviours."""

    hunger_threshold: float = Field(0.4, ge=0.0, le=1.0)
    hygiene_threshold: float = Field(0.4, ge=0.0, le=1.0)
    energy_threshold: float = Field(0.4, ge=0.0, le=1.0)
    job_arrival_buffer: int = Field(20, ge=0)


class LifecycleConfig(BaseModel):
    """Lifecycle timing controls for respawn/reset flows."""

    respawn_delay_ticks: int = Field(0, ge=0, le=100_000)


__all__ = [
    "AffordanceConfig",
    "AffordanceRuntimeConfig",
    "BehaviorConfig",
    "EmploymentConfig",
    "LifecycleConfig",
]


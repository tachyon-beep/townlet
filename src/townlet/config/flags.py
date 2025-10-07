"""Feature flag and basic policy runtime configuration models.

This module hosts small, low-risk configuration models and type aliases used
across the system. It is intentionally free of heavy imports to keep the
`townlet.config` package acyclic.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# Type aliases (kept simple and local to avoid cycles)
ObservationVariant = Literal["full", "hybrid", "compact"]
RelationshipStage = Literal["OFF", "A", "B", "C1", "C2", "C3"]
SocialRewardStage = Literal["OFF", "C1", "C2", "C3"]
LifecycleToggle = Literal["on", "off"]
CuriosityToggle = Literal["phase_A", "off"]
ConsoleMode = Literal["viewer", "admin"]


class StageFlags(BaseModel):
    """Configure high-level feature stage toggles."""

    relationships: RelationshipStage = "OFF"
    social_rewards: SocialRewardStage = "OFF"


class SystemFlags(BaseModel):
    """Toggle major runtime subsystems such as lifecycle and observations."""

    lifecycle: LifecycleToggle = "on"
    observations: ObservationVariant = "hybrid"


class TrainingFlags(BaseModel):
    """Enable/disable training-time behaviours such as curiosity."""

    curiosity: CuriosityToggle = "phase_A"


class PolicyRuntimeConfig(BaseModel):
    """Configure runtime policy behaviour (e.g., option commit duration)."""

    option_commit_ticks: int = Field(15, ge=0, le=100_000)


class ConsoleFlags(BaseModel):
    """Default console mode advertised when auth is optional."""

    mode: ConsoleMode = "viewer"


class BehaviorFlags(BaseModel):
    """Feature toggles for behaviour modules injected into the policy."""

    personality_profiles: bool = False
    reward_multipliers: bool = False


class ObservationFeatureFlags(BaseModel):
    """Observation variant feature toggles (UI overlays, metadata)."""

    personality_channels: bool = False
    personality_ui: bool = False


class FeatureFlags(BaseModel):
    """Aggregate feature flag surface exposed in YAML configs."""

    stages: StageFlags
    systems: SystemFlags
    training: TrainingFlags
    console: ConsoleFlags
    relationship_modifiers: bool = False
    behavior: BehaviorFlags = BehaviorFlags()
    observations: ObservationFeatureFlags = ObservationFeatureFlags()


__all__ = [
    "BehaviorFlags",
    "ConsoleFlags",
    "ConsoleMode",
    "CuriosityToggle",
    "FeatureFlags",
    "LifecycleToggle",
    "ObservationFeatureFlags",
    "ObservationVariant",
    "PolicyRuntimeConfig",
    "RelationshipStage",
    "SocialRewardStage",
    "StageFlags",
    "SystemFlags",
    "TrainingFlags",
]


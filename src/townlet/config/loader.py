"""Configuration loader and validation layer.

This module reflects the expectations in docs/REQUIREMENTS.md#1 and related
sections. It centralises config parsing, feature flag handling, and sanity
checks such as observation variant validation and reward guardrails.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


ObservationVariant = Literal["full", "hybrid", "compact"]
RelationshipStage = Literal["OFF", "A", "B", "C1", "C2", "C3"]
SocialRewardStage = Literal["OFF", "C1", "C2", "C3"]
LifecycleToggle = Literal["on", "off"]
CuriosityToggle = Literal["phase_A", "off"]
ConsoleMode = Literal["viewer", "admin"]
TrainingSource = Literal["replay", "rollout", "mixed"]


class StageFlags(BaseModel):
    relationships: RelationshipStage = "OFF"
    social_rewards: SocialRewardStage = "OFF"


class SystemFlags(BaseModel):
    lifecycle: LifecycleToggle = "on"
    observations: ObservationVariant = "hybrid"


class TrainingFlags(BaseModel):
    curiosity: CuriosityToggle = "phase_A"


class ConsoleFlags(BaseModel):
    mode: ConsoleMode = "viewer"


class FeatureFlags(BaseModel):
    stages: StageFlags
    systems: SystemFlags
    training: TrainingFlags
    console: ConsoleFlags
    relationship_modifiers: bool = False


class NeedsWeights(BaseModel):
    hunger: float = Field(1.0, ge=0.5, le=2.0)
    hygiene: float = Field(0.6, ge=0.2, le=1.0)
    energy: float = Field(0.8, ge=0.4, le=1.5)


class SocialRewardWeights(BaseModel):
    C1_chat_base: float = Field(0.01, ge=0.0, le=0.05)
    C1_coeff_trust: float = Field(0.3, ge=0.0, le=1.0)
    C1_coeff_fam: float = Field(0.2, ge=0.0, le=1.0)
    C2_avoid_conflict: float = Field(0.005, ge=0.0, le=0.02)


class RewardClips(BaseModel):
    clip_per_tick: float = Field(0.2, ge=0.01, le=1.0)
    clip_per_episode: float = Field(50, ge=1, le=200)
    no_positive_within_death_ticks: int = Field(10, ge=0, le=200)


class RewardsConfig(BaseModel):
    needs_weights: NeedsWeights
    decay_rates: Dict[str, float] = Field(default_factory=lambda: {
        "hunger": 0.01,
        "hygiene": 0.005,
        "energy": 0.008,
    })
    punctuality_bonus: float = Field(0.05, ge=0.0, le=0.1)
    wage_rate: float = Field(0.01, ge=0.0, le=0.05)
    survival_tick: float = Field(0.002, ge=0.0, le=0.01)
    faint_penalty: float = Field(-1.0, ge=-5.0, le=0.0)
    eviction_penalty: float = Field(-2.0, ge=-5.0, le=0.0)
    social: SocialRewardWeights = SocialRewardWeights()
    clip: RewardClips = RewardClips()

    @model_validator(mode="after")
    def _sanity_check_punctuality(self) -> "RewardsConfig":
        if self.punctuality_bonus > self.needs_weights.hunger:
            raise ValueError(
                "Punctuality bonus must remain below hunger weight (see REQUIREMENTS#6)."
            )
        return self


class ShapingConfig(BaseModel):
    use_potential: bool = True


class CuriosityConfig(BaseModel):
    phase_A_weight: float = Field(0.02, ge=0.0, le=0.1)
    decay_by_milestone: Literal["M2", "never"] = "M2"


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
    def _validate_ranges(self) -> "RivalryConfig":
        if self.min_value > self.max_value:
            raise ValueError("rivalry.min_value must be <= max_value")
        if self.avoid_threshold < self.min_value or self.avoid_threshold > self.max_value:
            raise ValueError("rivalry.avoid_threshold must lie within [min_value, max_value]")
        if self.eviction_threshold < self.min_value or self.eviction_threshold > self.max_value:
            raise ValueError("rivalry.eviction_threshold must lie within [min_value, max_value]")
        return self


class ConflictConfig(BaseModel):
    rivalry: RivalryConfig = RivalryConfig()




class PPOConfig(BaseModel):
    """Config for PPO training hyperparameters."""

    learning_rate: float = Field(3e-4, gt=0.0)
    clip_param: float = Field(0.2, ge=0.0, le=1.0)
    value_loss_coef: float = Field(0.5, ge=0.0)
    entropy_coef: float = Field(0.01, ge=0.0)
    num_epochs: int = Field(4, ge=1, le=64)
    mini_batch_size: int = Field(32, ge=1)
    gae_lambda: float = Field(0.95, ge=0.0, le=1.0)
    gamma: float = Field(0.99, ge=0.0, le=1.0)
    max_grad_norm: float = Field(0.5, ge=0.0)
    value_clip: float = Field(0.2, ge=0.0, le=1.0)
    advantage_normalization: bool = True
    num_mini_batches: int = Field(4, ge=1, le=1024)

class EmbeddingAllocatorConfig(BaseModel):
    """Embedding slot reuse guardrails (see REQUIREMENTS#3)."""

    cooldown_ticks: int = Field(2000, ge=0, le=10000)
    reuse_warning_threshold: float = Field(0.05, ge=0.0, le=0.5)
    log_forced_reuse: bool = True
    max_slots: int = Field(64, ge=1, le=256)


class HybridObservationConfig(BaseModel):
    local_window: int = Field(11, ge=3)
    include_targets: bool = False
    time_ticks_per_day: int = Field(1440, ge=1)

    @model_validator(mode="after")
    def _validate_window(self) -> "HybridObservationConfig":
        if self.local_window % 2 == 0:
            raise ValueError("observations.hybrid.local_window must be odd to center on agent")
        return self


class SocialSnippetConfig(BaseModel):
    top_friends: int = Field(2, ge=0, le=8)
    top_rivals: int = Field(2, ge=0, le=8)
    embed_dim: int = Field(8, ge=1, le=32)
    include_aggregates: bool = True

    @model_validator(mode="after")
    def _validate_totals(self) -> "SocialSnippetConfig":
        if self.top_friends == 0 and self.top_rivals == 0:
            object.__setattr__(self, "include_aggregates", False)
        if self.top_friends + self.top_rivals > 8:
            raise ValueError("Sum of top_friends and top_rivals must be <= 8 for tensor budget")
        return self


class ObservationsConfig(BaseModel):
    hybrid: HybridObservationConfig = HybridObservationConfig()
    social_snippet: SocialSnippetConfig = SocialSnippetConfig()


class StabilityConfig(BaseModel):
    affordance_fail_threshold: int = Field(5, ge=0, le=100)
    lateness_threshold: int = Field(3, ge=0, le=100)


class AffordanceConfig(BaseModel):
    affordances_file: str = Field("configs/affordances/core.yaml")


class EmploymentConfig(BaseModel):
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
    hunger_threshold: float = Field(0.4, ge=0.0, le=1.0)
    hygiene_threshold: float = Field(0.4, ge=0.0, le=1.0)
    energy_threshold: float = Field(0.4, ge=0.0, le=1.0)
    job_arrival_buffer: int = Field(20, ge=0)


class SocialRewardScheduleEntry(BaseModel):
    cycle: int = Field(0, ge=0)
    stage: SocialRewardStage


class TrainingConfig(BaseModel):
    source: TrainingSource = "replay"
    rollout_ticks: int = Field(100, ge=0)
    rollout_auto_seed_agents: bool = False
    replay_manifest: Path | None = None
    social_reward_stage_override: SocialRewardStage | None = None
    social_reward_schedule: List["SocialRewardScheduleEntry"] = Field(default_factory=list)


class JobSpec(BaseModel):
    start_tick: int = 0
    end_tick: int = 0
    wage_rate: float = 0.0
    lateness_penalty: float = 0.0
    location: tuple[int, int] | None = None


class SimulationConfig(BaseModel):
    config_id: str
    features: FeatureFlags
    rewards: RewardsConfig
    economy: Dict[str, float] = Field(default_factory=lambda: {
        "meal_cost": 0.4,
        "cook_energy_cost": 0.05,
        "cook_hygiene_cost": 0.02,
        "wage_income": 0.02,
        "ingredients_cost": 0.15,
        "stove_stock_replenish": 2,
    })
    jobs: Dict[str, JobSpec] = Field(default_factory=lambda: {
        "grocer": JobSpec(
            start_tick=180,
            end_tick=360,
            wage_rate=0.02,
            lateness_penalty=0.1,
            location=(0, 0),
        ),
        "barista": JobSpec(
            start_tick=400,
            end_tick=560,
            wage_rate=0.025,
            lateness_penalty=0.12,
            location=(1, 0),
        ),
    })
    shaping: ShapingConfig | None = None
    curiosity: CuriosityConfig | None = None
    queue_fairness: QueueFairnessConfig = QueueFairnessConfig()
    conflict: ConflictConfig = ConflictConfig()
    ppo: PPOConfig | None = None
    training: TrainingConfig = TrainingConfig()
    embedding_allocator: EmbeddingAllocatorConfig = EmbeddingAllocatorConfig()
    observations_config: ObservationsConfig = ObservationsConfig()
    affordances: AffordanceConfig = AffordanceConfig()
    stability: StabilityConfig = StabilityConfig()
    behavior: BehaviorConfig = BehaviorConfig()
    employment: EmploymentConfig = EmploymentConfig()

    model_config = ConfigDict(extra="allow")

    @property
    def observation_variant(self) -> ObservationVariant:
        return self.features.systems.observations

    def require_observation_variant(self, expected: ObservationVariant) -> None:
        if self.observation_variant != expected:
            raise ValueError(
                "Observation variant mismatch: expected %s, got %s" % (
                    expected,
                    self.observation_variant,
                )
            )


def load_config(path: Path) -> SimulationConfig:
    """Load and validate a Townlet YAML configuration file."""
    if not path.exists():
        raise FileNotFoundError(path)

    data = yaml.safe_load(path.read_text())
    try:
        return SimulationConfig.model_validate(data)
    except ValidationError as exc:  # pragma: no cover - formatting helper
        header = f"Invalid config at {path}:\n"
        raise ValueError(header + str(exc)) from exc

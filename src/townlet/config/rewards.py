"""Reward configuration models and stability canaries."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class NeedsWeights(BaseModel):
    """Weighting applied to hunger/hygiene/energy reward terms."""

    hunger: float = Field(1.0, ge=0.5, le=2.0)
    hygiene: float = Field(0.6, ge=0.2, le=1.0)
    energy: float = Field(0.8, ge=0.4, le=1.5)


class SocialRewardWeights(BaseModel):
    """Reward shaping multipliers used by the social reward engine."""

    C1_chat_base: float = Field(0.01, ge=0.0, le=0.05)
    C1_coeff_trust: float = Field(0.3, ge=0.0, le=1.0)
    C1_coeff_fam: float = Field(0.2, ge=0.0, le=1.0)
    C2_avoid_conflict: float = Field(0.005, ge=0.0, le=0.02)


class RewardClips(BaseModel):
    """Reward clipping constraints for per-tick and per-episode rewards."""

    clip_per_tick: float = Field(0.2, ge=0.01, le=1.0)
    clip_per_episode: float = Field(50, ge=1, le=200)
    no_positive_within_death_ticks: int = Field(10, ge=0, le=200)


class RewardsConfig(BaseModel):
    """Top-level reward configuration consumed by RewardEngine."""

    needs_weights: NeedsWeights
    decay_rates: dict[str, float] = Field(
        default_factory=lambda: {
            "hunger": 0.01,
            "hygiene": 0.005,
            "energy": 0.008,
        }
    )
    punctuality_bonus: float = Field(0.05, ge=0.0, le=0.1)
    wage_rate: float = Field(0.01, ge=0.0, le=0.05)
    survival_tick: float = Field(0.002, ge=0.0, le=0.01)
    faint_penalty: float = Field(-1.0, ge=-5.0, le=0.0)
    eviction_penalty: float = Field(-2.0, ge=-5.0, le=0.0)
    social: SocialRewardWeights = SocialRewardWeights()
    clip: RewardClips = RewardClips()

    @model_validator(mode="after")
    def _sanity_check_punctuality(self) -> RewardsConfig:
        if self.punctuality_bonus > self.needs_weights.hunger:
            raise ValueError("Punctuality bonus must remain below hunger weight (see REQUIREMENTS#6).")
        return self


class ShapingConfig(BaseModel):
    """Reward shaping configuration (potential-based shaping toggles)."""

    use_potential: bool = True


class CuriosityConfig(BaseModel):
    """Configure curiosity-style intrinsic reward weighting."""

    phase_A_weight: float = Field(0.02, ge=0.0, le=0.1)  # noqa: N815
    decay_by_milestone: str = Field("M2")


class StarvationCanaryConfig(BaseModel):
    """Detect prolonged starvation incidents for stability monitoring."""

    window_ticks: int = Field(1000, ge=1, le=100_000)
    max_incidents: int = Field(0, ge=0, le=10_000)
    hunger_threshold: float = Field(0.05, ge=0.0, le=1.0)
    min_duration_ticks: int = Field(30, ge=1, le=10_000)


class RewardVarianceCanaryConfig(BaseModel):
    """Alert when episodic reward variance spikes beyond limits."""

    window_ticks: int = Field(1000, ge=1, le=100_000)
    max_variance: float = Field(0.25, ge=0.0)
    min_samples: int = Field(20, ge=1, le=100_000)


class OptionThrashCanaryConfig(BaseModel):
    """Track how frequently agents swap options to flag thrashing."""

    window_ticks: int = Field(600, ge=1, le=100_000)
    max_switch_rate: float = Field(0.25, ge=0.0, le=10.0)
    min_samples: int = Field(10, ge=1, le=100_000)


class PromotionGateConfig(BaseModel):
    """Thresholds applied when deciding whether to promote policies."""

    required_passes: int = Field(2, ge=1, le=10)
    window_ticks: int = Field(1000, ge=1, le=100_000)
    allowed_alerts: tuple[str, ...] = ()

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    def _coerce_allowed(cls, value: object) -> object:  # noqa: N805
        if isinstance(value, dict):
            allowed = value.get("allowed_alerts")
            if allowed is not None and not isinstance(allowed, (list, tuple)):
                value = dict(value)
                value["allowed_alerts"] = [allowed]
            return value
        return value

    @model_validator(mode="after")
    def _normalise(self) -> PromotionGateConfig:
        object.__setattr__(self, "allowed_alerts", tuple(self.allowed_alerts))
        return self


class StabilityConfig(BaseModel):
    """Aggregate stability thresholds surfaced to telemetry & promotion."""

    affordance_fail_threshold: int = Field(5, ge=0, le=100)
    lateness_threshold: int = Field(3, ge=0, le=100)
    starvation: StarvationCanaryConfig = StarvationCanaryConfig()
    reward_variance: RewardVarianceCanaryConfig = RewardVarianceCanaryConfig()
    option_thrash: OptionThrashCanaryConfig = OptionThrashCanaryConfig()
    promotion: PromotionGateConfig = PromotionGateConfig()

    def as_dict(self) -> dict[str, object]:
        return {
            "affordance_fail_threshold": self.affordance_fail_threshold,
            "lateness_threshold": self.lateness_threshold,
            "starvation": self.starvation.model_dump(),
            "reward_variance": self.reward_variance.model_dump(),
            "option_thrash": self.option_thrash.model_dump(),
            "promotion": self.promotion.model_dump(),
        }


__all__ = [
    "CuriosityConfig",
    "NeedsWeights",
    "OptionThrashCanaryConfig",
    "PromotionGateConfig",
    "RewardClips",
    "RewardVarianceCanaryConfig",
    "RewardsConfig",
    "ShapingConfig",
    "SocialRewardWeights",
    "StabilityConfig",
    "StarvationCanaryConfig",
]


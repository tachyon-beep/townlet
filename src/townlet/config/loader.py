"""Configuration loader and validation layer.

This module reflects the expectations in docs/REQUIREMENTS.md#1 and related
sections. It centralises config parsing, feature flag handling, and sanity
checks such as observation variant validation and reward guardrails.
"""

from __future__ import annotations

import importlib
import re
from collections.abc import Mapping
from enum import Enum
from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

ObservationVariant = Literal["full", "hybrid", "compact"]
RelationshipStage = Literal["OFF", "A", "B", "C1", "C2", "C3"]
SocialRewardStage = Literal["OFF", "C1", "C2", "C3"]
LifecycleToggle = Literal["on", "off"]
CuriosityToggle = Literal["phase_A", "off"]
ConsoleMode = Literal["viewer", "admin"]
TrainingSource = Literal["replay", "rollout", "mixed", "bc", "anneal"]
TelemetryTransportType = Literal["stdout", "file", "tcp"]


class StageFlags(BaseModel):
    relationships: RelationshipStage = "OFF"
    social_rewards: SocialRewardStage = "OFF"


class SystemFlags(BaseModel):
    lifecycle: LifecycleToggle = "on"
    observations: ObservationVariant = "hybrid"


class TrainingFlags(BaseModel):
    curiosity: CuriosityToggle = "phase_A"


class PolicyRuntimeConfig(BaseModel):
    option_commit_ticks: int = Field(15, ge=0, le=100_000)


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


class StarvationCanaryConfig(BaseModel):
    window_ticks: int = Field(1000, ge=1, le=100_000)
    max_incidents: int = Field(0, ge=0, le=10_000)
    hunger_threshold: float = Field(0.05, ge=0.0, le=1.0)
    min_duration_ticks: int = Field(30, ge=1, le=10_000)


class RewardVarianceCanaryConfig(BaseModel):
    window_ticks: int = Field(1000, ge=1, le=100_000)
    max_variance: float = Field(0.25, ge=0.0)
    min_samples: int = Field(20, ge=1, le=100_000)


class OptionThrashCanaryConfig(BaseModel):
    window_ticks: int = Field(600, ge=1, le=100_000)
    max_switch_rate: float = Field(0.25, ge=0.0, le=10.0)
    min_samples: int = Field(10, ge=1, le=100_000)


class PromotionGateConfig(BaseModel):
    required_passes: int = Field(2, ge=1, le=10)
    window_ticks: int = Field(1000, ge=1, le=100_000)
    allowed_alerts: tuple[str, ...] = ()

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    def _coerce_allowed(cls, value: object) -> object:
        if isinstance(value, Mapping):
            allowed = value.get("allowed_alerts")
            if allowed is not None and not isinstance(allowed, (list, tuple)):
                value = dict(value)
                value["allowed_alerts"] = [allowed]
            return value
        return value

    @model_validator(mode="after")
    def _normalise(self) -> "PromotionGateConfig":
        object.__setattr__(self, "allowed_alerts", tuple(self.allowed_alerts))
        return self


class LifecycleConfig(BaseModel):
    respawn_delay_ticks: int = Field(0, ge=0, le=100_000)


class StabilityConfig(BaseModel):
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


class IntRange(BaseModel):
    min: int = Field(ge=0)
    max: int = Field(ge=0)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    def _coerce(cls, value: object) -> dict[str, int]:
        if isinstance(value, Mapping):
            return {
                "min": int(value.get("min", 0)),
                "max": int(value.get("max", value.get("min", 0))),
            }
        if isinstance(value, (list, tuple)):
            items = list(value)
            if len(items) != 2:
                raise ValueError("Range list must contain exactly two values")
            return {"min": int(items[0]), "max": int(items[1])}
        if isinstance(value, int):
            return {"min": value, "max": value}
        raise TypeError(f"Unsupported range value: {value!r}")

    @model_validator(mode="after")
    def _validate_bounds(self) -> "IntRange":
        if self.max < self.min:
            raise ValueError("Range max must be >= min")
        return self


class FloatRange(BaseModel):
    min: float
    max: float

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    def _coerce(cls, value: object) -> dict[str, float]:
        if isinstance(value, Mapping):
            lo = float(value.get("min", 0.0))
            hi = float(value.get("max", value.get("min", 0.0)))
            return {"min": lo, "max": hi}
        if isinstance(value, (list, tuple)):
            items = list(value)
            if len(items) != 2:
                raise ValueError("Float range list must contain exactly two values")
            return {"min": float(items[0]), "max": float(items[1])}
        if isinstance(value, (int, float)):
            val = float(value)
            return {"min": val, "max": val}
        raise TypeError(f"Unsupported float range value: {value!r}")

    @model_validator(mode="after")
    def _validate_bounds(self) -> "FloatRange":
        if self.max < self.min:
            raise ValueError("Float range max must be >= min")
        return self


class PerturbationKind(str, Enum):
    PRICE_SPIKE = "price_spike"
    BLACKOUT = "blackout"
    OUTAGE = "outage"
    ARRANGED_MEET = "arranged_meet"


class BasePerturbationEventConfig(BaseModel):
    kind: PerturbationKind
    probability_per_day: float = Field(0.0, ge=0.0, alias="prob_per_day")
    cooldown_ticks: int = Field(0, ge=0)
    duration: IntRange = Field(default_factory=lambda: IntRange(min=0, max=0))

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @model_validator(mode="before")
    def _normalise_duration(cls, values: dict[str, object]) -> dict[str, object]:
        if "duration" not in values and "duration_min" in values:
            values["duration"] = values["duration_min"]
        return values


class PriceSpikeEventConfig(BasePerturbationEventConfig):
    kind: Literal[PerturbationKind.PRICE_SPIKE] = PerturbationKind.PRICE_SPIKE
    magnitude: FloatRange = Field(default_factory=lambda: FloatRange(min=1.0, max=1.0))
    targets: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    def _normalise_magnitude(cls, values: dict[str, object]) -> dict[str, object]:
        if "magnitude" not in values and "magnitude_range" in values:
            values["magnitude"] = values["magnitude_range"]
        return values


class BlackoutEventConfig(BasePerturbationEventConfig):
    kind: Literal[PerturbationKind.BLACKOUT] = PerturbationKind.BLACKOUT
    utility: Literal["power"] = "power"


class OutageEventConfig(BasePerturbationEventConfig):
    kind: Literal[PerturbationKind.OUTAGE] = PerturbationKind.OUTAGE
    utility: Literal["water"] = "water"


class ArrangedMeetEventConfig(BasePerturbationEventConfig):
    kind: Literal[PerturbationKind.ARRANGED_MEET] = PerturbationKind.ARRANGED_MEET
    target: str = Field(default="top_rivals")
    location: str = Field(default="cafe")
    max_participants: int = Field(2, ge=2)


PerturbationEventConfig = Annotated[
    PriceSpikeEventConfig | BlackoutEventConfig | OutageEventConfig | ArrangedMeetEventConfig,
    Field(discriminator="kind"),
]


class PerturbationSchedulerConfig(BaseModel):
    max_concurrent_events: int = Field(1, ge=1)
    global_cooldown_ticks: int = Field(0, ge=0)
    per_agent_cooldown_ticks: int = Field(0, ge=0)
    grace_window_ticks: int = Field(60, ge=0)
    window_ticks: int = Field(1440, ge=1)
    max_events_per_window: int = Field(1, ge=0)
    events: dict[str, PerturbationEventConfig] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @property
    def event_list(self) -> list[PerturbationEventConfig]:
        return list(self.events.values())


class AffordanceRuntimeConfig(BaseModel):
    factory: str | None = None
    instrumentation: Literal["off", "timings"] = "off"
    options: dict[str, object] = Field(default_factory=dict)
    hook_allowlist: tuple[str, ...] = Field(default_factory=tuple)
    allow_env_hooks: bool = True

    model_config = ConfigDict(extra="allow")


class AffordanceConfig(BaseModel):
    affordances_file: str = Field("configs/affordances/core.yaml")
    runtime: AffordanceRuntimeConfig = AffordanceRuntimeConfig()


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


class BCTrainingSettings(BaseModel):
    manifest: Path | None = None
    learning_rate: float = Field(1e-3, gt=0.0)
    batch_size: int = Field(64, ge=1)
    epochs: int = Field(10, ge=1)
    weight_decay: float = Field(0.0, ge=0.0)
    device: str = "cpu"


class AnnealStage(BaseModel):
    cycle: int = Field(0, ge=0)
    mode: Literal["bc", "ppo"] = "ppo"
    epochs: int = Field(1, ge=1)
    bc_weight: float = Field(1.0, ge=0.0, le=1.0)


class NarrationThrottleConfig(BaseModel):
    global_cooldown_ticks: int = Field(30, ge=0, le=10_000)
    category_cooldown_ticks: dict[str, int] = Field(default_factory=dict)
    dedupe_window_ticks: int = Field(20, ge=0, le=10_000)
    global_window_ticks: int = Field(600, ge=1, le=10_000)
    global_window_limit: int = Field(10, ge=1, le=1_000)
    priority_categories: list[str] = Field(default_factory=list)

    def get_category_cooldown(self, category: str) -> int:
        return int(self.category_cooldown_ticks.get(category, self.global_cooldown_ticks))


class RelationshipNarrationConfig(BaseModel):
    friendship_trust_threshold: float = Field(0.6, ge=-1.0, le=1.0)
    friendship_delta_threshold: float = Field(0.25, ge=0.0, le=2.0)
    friendship_priority_threshold: float = Field(0.85, ge=-1.0, le=1.0)
    rivalry_avoid_threshold: float = Field(0.7, ge=0.0, le=1.0)
    rivalry_escalation_threshold: float = Field(0.9, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _validate_thresholds(self) -> "RelationshipNarrationConfig":
        if self.friendship_priority_threshold < self.friendship_trust_threshold:
            raise ValueError(
                "telemetry.relationship_narration.friendship_priority_threshold must be "
                ">= friendship_trust_threshold"
            )
        if self.rivalry_escalation_threshold < self.rivalry_avoid_threshold:
            raise ValueError(
                "telemetry.relationship_narration.rivalry_escalation_threshold must be "
                ">= rivalry_avoid_threshold"
            )
        return self


class TelemetryRetryPolicy(BaseModel):
    max_attempts: int = Field(default=3, ge=0, le=10)
    backoff_seconds: float = Field(default=0.5, ge=0.0, le=30.0)


class TelemetryBufferConfig(BaseModel):
    max_batch_size: int = Field(default=32, ge=1, le=500)
    max_buffer_bytes: int = Field(default=256_000, ge=1_024, le=16_777_216)
    flush_interval_ticks: int = Field(default=1, ge=1, le=10_000)


class TelemetryTransportConfig(BaseModel):
    type: TelemetryTransportType = "stdout"
    endpoint: str | None = None
    file_path: Path | None = None
    connect_timeout_seconds: float = Field(default=5.0, ge=0.0, le=60.0)
    send_timeout_seconds: float = Field(default=1.0, ge=0.0, le=60.0)
    enable_tls: bool = False
    verify_hostname: bool = True
    ca_file: Path | None = None
    cert_file: Path | None = None
    key_file: Path | None = None
    allow_plaintext: bool = False
    retry: TelemetryRetryPolicy = TelemetryRetryPolicy()
    buffer: TelemetryBufferConfig = TelemetryBufferConfig()
    worker_poll_seconds: float = Field(default=0.5, ge=0.01, le=10.0)

    @model_validator(mode="after")
    def _validate_transport(self) -> "TelemetryTransportConfig":
        transport_type = self.type
        if transport_type == "stdout":
            if self.endpoint:
                raise ValueError(
                    "telemetry.transport.endpoint is not supported for stdout transport"
                )
            if self.file_path is not None:
                raise ValueError(
                    "telemetry.transport.file_path must be omitted for stdout transport"
                )
            if self.enable_tls:
                raise ValueError(
                    "telemetry.transport.enable_tls is only supported for tcp transport"
                )
            if any(value is not None for value in (self.ca_file, self.cert_file, self.key_file)):
                raise ValueError(
                    "telemetry.transport TLS options are only supported for tcp transport"
                )
            if self.allow_plaintext:
                raise ValueError(
                    "telemetry.transport.allow_plaintext is only supported for tcp transport"
                )
        elif transport_type == "file":
            if self.file_path is None:
                raise ValueError("telemetry.transport.file_path is required when type is 'file'")
            if str(self.file_path).strip() == "":
                raise ValueError("telemetry.transport.file_path must not be blank")
            if self.enable_tls:
                raise ValueError(
                    "telemetry.transport.enable_tls is only supported for tcp transport"
                )
            if any(value is not None for value in (self.ca_file, self.cert_file, self.key_file)):
                raise ValueError(
                    "telemetry.transport TLS options are only supported for tcp transport"
                )
            if self.allow_plaintext:
                raise ValueError(
                    "telemetry.transport.allow_plaintext is only supported for tcp transport"
                )
        elif transport_type == "tcp":
            endpoint = (self.endpoint or "").strip()
            if not endpoint:
                raise ValueError("telemetry.transport.endpoint is required when type is 'tcp'")
            self.endpoint = endpoint
            if self.file_path is not None:
                raise ValueError("telemetry.transport.file_path must be omitted for tcp transport")
            if self.enable_tls:
                if self.key_file and not self.cert_file:
                    raise ValueError(
                        "telemetry.transport.cert_file must be provided when key_file is set"
                    )
                if self.cert_file and not self.key_file:
                    raise ValueError(
                        "telemetry.transport.key_file must be provided when cert_file is set"
                    )
                if self.cert_file is not None and str(self.cert_file).strip() == "":
                    raise ValueError("telemetry.transport.cert_file must not be blank")
                if self.key_file is not None and str(self.key_file).strip() == "":
                    raise ValueError("telemetry.transport.key_file must not be blank")
                if self.ca_file is not None and str(self.ca_file).strip() == "":
                    raise ValueError("telemetry.transport.ca_file must not be blank")
            elif not self.allow_plaintext:
                raise ValueError(
                    "telemetry.transport.tcp requires enable_tls=true or allow_plaintext=true"
                )
        else:  # pragma: no cover - defensive branch for Literal changes
            raise ValueError(f"Unsupported telemetry transport type: {transport_type}")
        return self


class TelemetryConfig(BaseModel):
    narration: NarrationThrottleConfig = NarrationThrottleConfig()
    transport: TelemetryTransportConfig = TelemetryTransportConfig()
    relationship_narration: RelationshipNarrationConfig = RelationshipNarrationConfig()
    diff_enabled: bool = True


class ConsoleAuthTokenConfig(BaseModel):
    """Configuration entry for a single console authentication token."""

    label: str | None = None
    role: ConsoleMode = "viewer"
    token: str | None = None
    token_env: str | None = None

    @model_validator(mode="after")
    def _validate_token_source(self) -> "ConsoleAuthTokenConfig":
        provided = [value for value in (self.token, self.token_env) if value]
        if len(provided) != 1:
            raise ValueError(
                "console.auth.tokens entries must define exactly one of 'token' or 'token_env'"
            )
        if self.token is not None and not self.token.strip():
            raise ValueError("console.auth.tokens.token must not be blank")
        if self.token_env is not None and not self.token_env.strip():
            raise ValueError("console.auth.tokens.token_env must not be blank")
        return self


class ConsoleAuthConfig(BaseModel):
    """Authentication settings for console and telemetry command ingress."""

    enabled: bool = False
    require_auth_for_viewer: bool = True
    tokens: list[ConsoleAuthTokenConfig] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_tokens(self) -> "ConsoleAuthConfig":
        if self.enabled and not self.tokens:
            raise ValueError("console.auth.tokens must be provided when auth is enabled")
        return self


class SnapshotStorageConfig(BaseModel):
    root: Path = Field(default=Path("snapshots"))

    @model_validator(mode="after")
    def _validate_root(self) -> "SnapshotStorageConfig":
        if str(self.root).strip() == "":
            raise ValueError("snapshot.storage.root must not be empty")
        return self


class SnapshotAutosaveConfig(BaseModel):
    cadence_ticks: int | None = Field(default=None, ge=1)
    retain: int = Field(default=3, ge=1, le=1000)

    @model_validator(mode="after")
    def _validate_cadence(self) -> "SnapshotAutosaveConfig":
        if self.cadence_ticks is not None and self.cadence_ticks < 100:
            raise ValueError(
                "snapshot.autosave.cadence_ticks must be at least 100 ticks when enabled"
            )
        return self


class SnapshotIdentityConfig(BaseModel):
    policy_hash: str | None = None
    policy_artifact: Path | None = None
    observation_variant: ObservationVariant | Literal["infer"] = "infer"
    anneal_ratio: float | None = Field(default=None, ge=0.0, le=1.0)

    _HEX40 = re.compile(r"^[0-9a-fA-F]{40}$")
    _HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
    _BASE64 = re.compile(r"^[A-Za-z0-9+/=]{32,88}$")

    @model_validator(mode="after")
    def _validate_policy_hash(self) -> "SnapshotIdentityConfig":
        if self.policy_hash is None:
            return self
        candidate = self.policy_hash.strip()
        if not candidate:
            raise ValueError("snapshot.identity.policy_hash must not be blank if provided")
        if not (
            self._HEX40.match(candidate)
            or self._HEX64.match(candidate)
            or self._BASE64.match(candidate)
        ):
            raise ValueError(
                "snapshot.identity.policy_hash must be a 40/64-char hex or base64-encoded digest"
            )
        self.policy_hash = candidate
        return self

    @model_validator(mode="after")
    def _validate_variant(self) -> "SnapshotIdentityConfig":
        if self.observation_variant == "infer":
            return self
        supported: set[str] = {"hybrid", "full", "compact"}
        if self.observation_variant not in supported:
            raise ValueError(
                "snapshot.identity.observation_variant must be one of %s or 'infer'"
                % sorted(supported)
            )
        return self


class SnapshotMigrationsConfig(BaseModel):
    handlers: dict[str, str] = Field(default_factory=dict)
    auto_apply: bool = False
    allow_minor: bool = False

    @model_validator(mode="after")
    def _validate_handlers(self) -> "SnapshotMigrationsConfig":
        for legacy_id, target in self.handlers.items():
            if not str(legacy_id).strip():
                raise ValueError("snapshot.migrations.handlers keys must not be empty")
            if not str(target).strip():
                raise ValueError("snapshot.migrations.handlers values must not be empty")
        return self


class SnapshotGuardrailsConfig(BaseModel):
    require_exact_config: bool = True
    allow_downgrade: bool = False
    allowed_paths: list[Path] = Field(default_factory=list)


class SnapshotConfig(BaseModel):
    storage: SnapshotStorageConfig = SnapshotStorageConfig()
    autosave: SnapshotAutosaveConfig = SnapshotAutosaveConfig()
    identity: SnapshotIdentityConfig = SnapshotIdentityConfig()
    migrations: SnapshotMigrationsConfig = SnapshotMigrationsConfig()
    guardrails: SnapshotGuardrailsConfig = SnapshotGuardrailsConfig()

    @model_validator(mode="after")
    def _validate_observation_override(self) -> "SnapshotConfig":
        if (
            self.identity.observation_variant != "infer"
            and self.identity.observation_variant not in {"hybrid", "full", "compact"}
        ):
            raise ValueError(
                "snapshot.identity.observation_variant must be one of "
                "['hybrid', 'full', 'compact', 'infer']"
            )
        return self


class TrainingConfig(BaseModel):
    source: TrainingSource = "replay"
    rollout_ticks: int = Field(100, ge=0)
    rollout_auto_seed_agents: bool = False
    replay_manifest: Path | None = None
    social_reward_stage_override: SocialRewardStage | None = None
    social_reward_schedule: list["SocialRewardScheduleEntry"] = Field(default_factory=list)
    bc: BCTrainingSettings = BCTrainingSettings()
    anneal_schedule: list[AnnealStage] = Field(default_factory=list)
    anneal_accuracy_threshold: float = Field(0.9, ge=0.0, le=1.0)
    anneal_enable_policy_blend: bool = False


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
    economy: dict[str, float] = Field(
        default_factory=lambda: {
            "meal_cost": 0.4,
            "cook_energy_cost": 0.05,
            "cook_hygiene_cost": 0.02,
            "wage_income": 0.02,
            "ingredients_cost": 0.15,
            "stove_stock_replenish": 2,
        }
    )
    jobs: dict[str, JobSpec] = Field(
        default_factory=lambda: {
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
        }
    )
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
    policy_runtime: PolicyRuntimeConfig = PolicyRuntimeConfig()
    employment: EmploymentConfig = EmploymentConfig()
    telemetry: TelemetryConfig = TelemetryConfig()
    console_auth: ConsoleAuthConfig = ConsoleAuthConfig()
    snapshot: SnapshotConfig = SnapshotConfig()
    perturbations: PerturbationSchedulerConfig = PerturbationSchedulerConfig()
    lifecycle: LifecycleConfig = LifecycleConfig()

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def _validate_observation_variant(self) -> "SimulationConfig":
        variant = self.features.systems.observations
        supported = {"hybrid", "full", "compact"}
        if variant not in supported:
            raise ValueError(
                "Observation variant '%s' is not supported yet; supported variants: %s"
                % (variant, sorted(supported))
            )
        return self

    @property
    def observation_variant(self) -> ObservationVariant:
        return self.features.systems.observations

    def require_observation_variant(self, expected: ObservationVariant) -> None:
        if self.observation_variant != expected:
            raise ValueError(
                "Observation variant mismatch: expected %s, got %s"
                % (
                    expected,
                    self.observation_variant,
                )
            )

    def snapshot_root(self) -> Path:
        root = Path(self.snapshot.storage.root)
        return root.expanduser().resolve()

    def snapshot_allowed_roots(self) -> tuple[Path, ...]:
        roots: list[Path] = [self.snapshot_root()]
        extra = getattr(self.snapshot.guardrails, "allowed_paths", [])
        for candidate in extra:
            if candidate is None:
                continue
            path = Path(candidate)
            resolved = path.expanduser().resolve()
            if resolved not in roots:
                roots.append(resolved)
        return tuple(roots)

    def build_snapshot_identity(
        self,
        *,
        policy_hash: str | None,
        runtime_observation_variant: ObservationVariant | None,
        runtime_anneal_ratio: float | None,
    ) -> dict[str, object]:
        identity_cfg = self.snapshot.identity
        resolved_variant: str | None
        if identity_cfg.observation_variant != "infer":
            resolved_variant = identity_cfg.observation_variant
        else:
            resolved_variant = runtime_observation_variant or self.observation_variant

        resolved_hash = identity_cfg.policy_hash or policy_hash
        resolved_anneal: float | None
        if identity_cfg.anneal_ratio is not None:
            resolved_anneal = identity_cfg.anneal_ratio
        else:
            resolved_anneal = runtime_anneal_ratio

        payload: dict[str, object] = {"config_id": self.config_id}
        if resolved_hash is not None:
            payload["policy_hash"] = resolved_hash
        artifact = identity_cfg.policy_artifact
        if artifact is not None:
            payload["policy_artifact"] = str(artifact)
        if resolved_variant is not None:
            payload["observation_variant"] = resolved_variant
        if resolved_anneal is not None:
            payload["anneal_ratio"] = resolved_anneal
        return payload

    def register_snapshot_migrations(self) -> None:
        handlers = dict(self.snapshot.migrations.handlers)
        if not handlers:
            return
        from townlet.snapshots import register_migration

        for legacy_config, handler_path in handlers.items():
            module_name, separator, attribute = handler_path.partition(":")
            if not module_name or not attribute or separator != ":":
                raise ValueError(
                    "snapshot.migrations.handlers entries must use 'module:function' format"
                )
            try:
                module = importlib.import_module(module_name)
            except ImportError as exc:  # pragma: no cover - defensive path
                raise ImportError(
                    f"Failed to import snapshot migration module '{module_name}'"
                ) from exc
            try:
                handler = getattr(module, attribute)
            except AttributeError as exc:  # pragma: no cover - defensive path
                raise AttributeError(
                    f"Snapshot migration handler '{attribute}' not found in module '{module_name}'"
                ) from exc
            register_migration(legacy_config, self.config_id, handler)


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

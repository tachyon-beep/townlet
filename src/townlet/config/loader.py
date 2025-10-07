"""Configuration loader and validation layer.

This module reflects the expectations in docs/REQUIREMENTS.md#1 and related
sections. It centralises config parsing, feature flag handling, and sanity
checks such as observation variant validation and reward guardrails.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Final, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from townlet.config.conflict import ConflictConfig, QueueFairnessConfig
from townlet.config.console_auth import ConsoleAuthConfig
from townlet.config.flags import (
    FeatureFlags,
    ObservationVariant,
    PolicyRuntimeConfig,
    SocialRewardStage,
)
from townlet.config.observations import ObservationsConfig
from townlet.config.personalities import PersonalityAssignmentConfig
from townlet.config.policy import PPOConfig
from townlet.config.rewards import (
    CuriosityConfig,
    RewardsConfig,
    ShapingConfig,
    StabilityConfig,
)
from townlet.config.runtime import RuntimeProviders
from townlet.config.scheduler import (
    PerturbationSchedulerConfig,
)
from townlet.config.snapshots import (
    SnapshotConfig,
)
from townlet.config.telemetry import (
    NarrationThrottleConfig,
    PersonalityNarrationConfig,
    RelationshipNarrationConfig,
    TelemetryBufferConfig,
    TelemetryConfig,
    TelemetryRetryPolicy,
    TelemetryTransformEntry,
    TelemetryTransformsConfig,
    TelemetryTransportConfig,
    TelemetryWorkerConfig,
)
from townlet.config.world_config import (
    AffordanceConfig,
    BehaviorConfig,
    EmploymentConfig,
    LifecycleConfig,
)

TrainingSource = Literal["replay", "rollout", "mixed", "bc", "anneal"]
TelemetryTransportType = Literal["stdout", "file", "tcp", "websocket"]
TelemetryBackpressureStrategy = Literal["drop_oldest", "block", "fan_out"]

PERSONALITY_NEED_KEYS: Final[set[str]] = {"hunger", "hygiene", "energy"}
PERSONALITY_REWARD_KEYS: Final[set[str]] = {"social", "employment", "survival"}
PERSONALITY_BEHAVIOUR_KEYS: Final[set[str]] = {
    "chat_preference",
    "work_affinity",
    "conflict_tolerance",
}

# Prevent tooling from pruning imported telemetry types that are re-exported
_telemetry_exports: tuple[object, ...] = (
    NarrationThrottleConfig,
    PersonalityNarrationConfig,
    RelationshipNarrationConfig,
    TelemetryBufferConfig,
    TelemetryRetryPolicy,
    TelemetryTransformEntry,
    TelemetryTransformsConfig,
    TelemetryTransportConfig,
    TelemetryWorkerConfig,
)

 


## PersonalityAssignmentConfig moved to townlet.config.personalities


## Rewards models moved to townlet.config.rewards


## Conflict/fairness moved to townlet.config.conflict


## PPOConfig moved to townlet.config.policy


class EmbeddingAllocatorConfig(BaseModel):
    """Embedding slot reuse guardrails (see REQUIREMENTS#3)."""

    cooldown_ticks: int = Field(2000, ge=0, le=10000)
    reuse_warning_threshold: float = Field(0.05, ge=0.0, le=0.5)
    log_forced_reuse: bool = True
    max_slots: int = Field(64, ge=1, le=256)





## Canary/promotion/stability moved to townlet.config.rewards


 


## Stability moved to townlet.config.rewards





## Scheduler types moved to townlet.config.scheduler


 


 


 


 


class SocialRewardScheduleEntry(BaseModel):
    """Single entry in the social reward schedule."""

    cycle: int = Field(0, ge=0)
    stage: SocialRewardStage


class BCTrainingSettings(BaseModel):
    """Behaviour-cloning training parameters for anneal stages."""

    manifest: Path | None = None
    learning_rate: float = Field(1e-3, gt=0.0)
    batch_size: int = Field(64, ge=1)
    epochs: int = Field(10, ge=1)
    weight_decay: float = Field(0.0, ge=0.0)
    device: str = "cpu"


class AnnealStage(BaseModel):
    """Defines a single phase within the anneal schedule."""

    cycle: int = Field(0, ge=0)
    mode: Literal["bc", "ppo"] = "ppo"
    epochs: int = Field(1, ge=1)
    bc_weight: float = Field(1.0, ge=0.0, le=1.0)






## RuntimeProviderConfig and RuntimeProviders moved to townlet.config.runtime




class TrainingConfig(BaseModel):
    """Aggregate training configuration (BC, PPO, anneal)."""

    source: TrainingSource = "replay"
    rollout_ticks: int = Field(100, ge=0)
    rollout_auto_seed_agents: bool = False
    replay_manifest: Path | None = None
    social_reward_stage_override: SocialRewardStage | None = None
    social_reward_schedule: list[SocialRewardScheduleEntry] = Field(default_factory=list)
    bc: BCTrainingSettings = Field(default_factory=lambda: BCTrainingSettings(
        manifest=None,
        learning_rate=1e-3,
        batch_size=64,
        epochs=10,
        weight_decay=0.0,
        device="cpu",
    ))
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
    """Top-level simulation configuration assembled from YAML."""

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
    queue_fairness: QueueFairnessConfig = Field(default_factory=lambda: QueueFairnessConfig(
        cooldown_ticks=60,
        ghost_step_after=3,
        age_priority_weight=0.1,
    ))
    conflict: ConflictConfig = ConflictConfig()
    ppo: PPOConfig | None = None
    training: TrainingConfig = Field(default_factory=lambda: TrainingConfig(
        source="replay",
        rollout_ticks=100,
        rollout_auto_seed_agents=False,
        replay_manifest=None,
        social_reward_stage_override=None,
        social_reward_schedule=[],
        bc=BCTrainingSettings(
            manifest=None,
            learning_rate=1e-3,
            batch_size=64,
            epochs=10,
            weight_decay=0.0,
            device="cpu",
        ),
        anneal_schedule=[],
        anneal_accuracy_threshold=0.9,
        anneal_enable_policy_blend=False,
    ))
    embedding_allocator: EmbeddingAllocatorConfig = Field(default_factory=lambda: EmbeddingAllocatorConfig(
        cooldown_ticks=2000,
        reuse_warning_threshold=0.05,
        log_forced_reuse=True,
        max_slots=64,
    ))
    observations_config: ObservationsConfig = Field(default_factory=lambda: ObservationsConfig())
    affordances: AffordanceConfig = Field(default_factory=lambda: AffordanceConfig(affordances_file="configs/affordances/core.yaml"))
    stability: StabilityConfig = Field(default_factory=lambda: StabilityConfig(
        affordance_fail_threshold=5,
        lateness_threshold=3,
    ))
    behavior: BehaviorConfig = Field(default_factory=lambda: BehaviorConfig(
        hunger_threshold=0.4,
        hygiene_threshold=0.4,
        energy_threshold=0.4,
        job_arrival_buffer=20,
    ))
    policy_runtime: PolicyRuntimeConfig = Field(default_factory=lambda: PolicyRuntimeConfig(option_commit_ticks=15))
    employment: EmploymentConfig = EmploymentConfig()  # type: ignore[call-arg]
    personalities: PersonalityAssignmentConfig = Field(default_factory=lambda: PersonalityAssignmentConfig())
    telemetry: TelemetryConfig = Field(default_factory=lambda: TelemetryConfig())
    console_auth: ConsoleAuthConfig = Field(default_factory=lambda: ConsoleAuthConfig())
    snapshot: SnapshotConfig = Field(default_factory=lambda: SnapshotConfig())
    perturbations: PerturbationSchedulerConfig = PerturbationSchedulerConfig()  # type: ignore[call-arg]
    lifecycle: LifecycleConfig = Field(default_factory=lambda: LifecycleConfig(respawn_delay_ticks=0))
    runtime: RuntimeProviders = Field(default_factory=lambda: RuntimeProviders())

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def _validate_observation_variant(self) -> SimulationConfig:
        variant = self.features.systems.observations
        supported = {"hybrid", "full", "compact"}
        if variant not in supported:
            raise ValueError(f"Observation variant '{variant}' is not supported yet; supported variants: {sorted(supported)}")
        return self

    @property
    def observation_variant(self) -> ObservationVariant:
        """Return the configured observation variant (hybrid/compact/... )."""

        return self.features.systems.observations

    def require_observation_variant(self, expected: ObservationVariant) -> None:
        """Ensure the simulation is configured with the requested observation variant."""

        if self.observation_variant != expected:
            raise ValueError(f"Observation variant mismatch: expected {expected}, got {self.observation_variant}")

    def snapshot_root(self) -> Path:
        """Return the root directory used for snapshot storage."""

        root = Path(self.snapshot.storage.root)
        return root.expanduser().resolve()

    def resolve_personality_profile(self, agent_id: str, profile_name: str | None = None) -> str:
        """Resolve an agent to a personality profile key, honoring overrides."""

        if profile_name:
            return str(profile_name).lower()
        seed_value = getattr(self, "seed", None)
        return self.personalities.resolve(agent_id, seed=seed_value)

    def personality_profiles_enabled(self) -> bool:
        """Return whether personality profile features are enabled."""

        return bool(getattr(self.features.behavior, "personality_profiles", False))

    def reward_personality_scaling_enabled(self) -> bool:
        """Return whether reward scaling driven by personality is enabled."""

        return bool(getattr(self.features.behavior, "reward_multipliers", False))

    def personality_channels_enabled(self) -> bool:
        observations = getattr(self.features, "observations", None)
        return bool(getattr(observations, "personality_channels", False))

    def personality_ui_enabled(self) -> bool:
        observations = getattr(self.features, "observations", None)
        return bool(getattr(observations, "personality_ui", False))

    @model_validator(mode="after")
    def _validate_personality_bias_keys(self) -> SimulationConfig:
        if not (self.personality_profiles_enabled() or self.reward_personality_scaling_enabled()):
            return self
        from townlet.agents.models import PersonalityProfiles

        for profile_name in PersonalityProfiles.names():
            profile = PersonalityProfiles.get(profile_name)
            unknown_needs = set(profile.need_multipliers) - PERSONALITY_NEED_KEYS
            if unknown_needs:
                raise ValueError(f"Unknown need multipliers {sorted(unknown_needs)} in personality profile '{profile_name}'")
            unknown_reward = set(profile.reward_bias) - PERSONALITY_REWARD_KEYS
            if unknown_reward:
                raise ValueError(f"Unknown reward bias keys {sorted(unknown_reward)} in personality profile '{profile_name}'")
            unknown_behaviour = set(profile.behaviour_bias) - PERSONALITY_BEHAVIOUR_KEYS
            if unknown_behaviour:
                raise ValueError(f"Unknown behaviour bias keys {sorted(unknown_behaviour)} in personality profile '{profile_name}'")
        return self

    @model_validator(mode="after")
    def _validate_personality_profile_names(self) -> SimulationConfig:
        """Ensure personality distribution/overrides reference known profiles.

        Kept in loader to avoid domain-level imports from runtime modules.
        """
        try:
            from townlet.agents.models import PersonalityProfiles
        except Exception:  # pragma: no cover - defensive
            return self
        known = set(PersonalityProfiles.names())
        # Validate distribution keys
        dist_keys = set(getattr(self.personalities, "distribution", {}).keys())
        unknown = dist_keys - known
        if unknown:
            raise ValueError(f"Unknown personality profiles in distribution: {sorted(unknown)}")
        # Validate overrides values
        override_vals = set(getattr(self.personalities, "overrides", {}).values())
        unknown_overrides = override_vals - known
        if unknown_overrides:
            raise ValueError(f"Overrides reference unknown profiles: {sorted(unknown_overrides)}")
        return self

    def snapshot_allowed_roots(self) -> tuple[Path, ...]:
        """Return tuple of allowed snapshot root directories."""

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
        """Construct metadata describing the runtime snapshot identity."""

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
                raise ValueError("snapshot.migrations.handlers entries must use 'module:function' format")
            try:
                module = importlib.import_module(module_name)
            except ImportError as exc:  # pragma: no cover - defensive path
                raise ImportError(f"Failed to import snapshot migration module '{module_name}'") from exc
            try:
                handler = getattr(module, attribute)
            except AttributeError as exc:  # pragma: no cover - defensive path
                raise AttributeError(f"Snapshot migration handler '{attribute}' not found in module '{module_name}'") from exc
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

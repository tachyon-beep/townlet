"""Config utilities for Townlet."""

from __future__ import annotations

from .conflict import ConflictConfig, QueueFairnessConfig, RivalryConfig
from .console_auth import ConsoleAuthConfig, ConsoleAuthTokenConfig, ConsoleMode
from .core import FloatRange, IntRange
from .flags import (
    BehaviorFlags,
    ConsoleFlags,
    CuriosityToggle,
    LifecycleToggle,
    ObservationFeatureFlags,
    ObservationVariant,
    PolicyRuntimeConfig,
    SocialRewardStage,
    StageFlags,
    SystemFlags,
    TrainingFlags,
)
from .loader import (
    AnnealStage,
    BCTrainingSettings,
    # Console auth moved (re-exported below)
    # CuriosityToggle moved (re-exported below)
    EmbeddingAllocatorConfig,
    # LifecycleToggle moved (re-exported below)
    # ObservationFeatureFlags moved (re-exported below)
    # ObservationVariant moved (re-exported below)
    # OptionThrashCanaryConfig moved (re-exported below)
    # PersonalityAssignmentConfig moved to townlet.config.personalities; re-exported below
    # NOTE: PPOConfig moved to townlet.config.policy; re-exported below
    # PromotionGateConfig moved (re-exported below)
    # RewardVarianceCanaryConfig moved (re-exported below)
    # NOTE: Runtime providers moved to townlet.config.runtime; re-exported below
    SimulationConfig,
    # Snapshots moved (re-exported below)
    SocialRewardScheduleEntry,
    # SocialRewardStage moved (re-exported below)
    # StarvationCanaryConfig moved (re-exported below)
    # telemetry moved (re-exported below)
    TrainingConfig,
    TrainingSource,
    load_config,
)

# Re-exports from decomposed modules
from .policy import PPOConfig
from .rewards import (
    CuriosityConfig,
    NeedsWeights,
    OptionThrashCanaryConfig,
    PromotionGateConfig,
    RewardClips,
    RewardsConfig,
    RewardVarianceCanaryConfig,
    ShapingConfig,
    SocialRewardWeights,
    StabilityConfig,
    StarvationCanaryConfig,
)
from .runtime import RuntimeProviderConfig, RuntimeProviders
from .scheduler import (
    ArrangedMeetEventConfig,
    BlackoutEventConfig,
    OutageEventConfig,
    PerturbationEventConfig,
    PerturbationKind,
    PerturbationSchedulerConfig,
    PriceSpikeEventConfig,
)
from .snapshots import (
    SnapshotAutosaveConfig,
    SnapshotConfig,
    SnapshotGuardrailsConfig,
    SnapshotIdentityConfig,
    SnapshotMigrationsConfig,
    SnapshotStorageConfig,
)
from .telemetry import (
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
from .world_config import (
    AffordanceConfig,
    AffordanceRuntimeConfig,
    BehaviorConfig,
    EmploymentConfig,
    LifecycleConfig,
)
from .observations import ObservationsConfig
from .personalities import PersonalityAssignmentConfig

__all__ = [
    "AffordanceConfig",
    "AffordanceRuntimeConfig",
    "AnnealStage",
    "ArrangedMeetEventConfig",
    "BCTrainingSettings",
    "BehaviorConfig",
    "BehaviorFlags",
    "BlackoutEventConfig",
    "ConflictConfig",
    "ConsoleAuthConfig",
    "ConsoleAuthTokenConfig",
    "ConsoleFlags",
    "ConsoleMode",
    "CuriosityConfig",
    "CuriosityToggle",
    "EmbeddingAllocatorConfig",
    "EmploymentConfig",
    "FloatRange",
    "IntRange",
    "LifecycleConfig",
    "LifecycleToggle",
    "NarrationThrottleConfig",
    "NeedsWeights",
    "ObservationFeatureFlags",
    "ObservationVariant",
    "ObservationsConfig",
    "OptionThrashCanaryConfig",
    "OutageEventConfig",
    "PPOConfig",
    "PersonalityAssignmentConfig",
    "PersonalityNarrationConfig",
    "PerturbationEventConfig",
    "PerturbationKind",
    "PerturbationSchedulerConfig",
    "PolicyRuntimeConfig",
    "PriceSpikeEventConfig",
    "PromotionGateConfig",
    "QueueFairnessConfig",
    "RelationshipNarrationConfig",
    "RewardClips",
    "RewardVarianceCanaryConfig",
    "RewardsConfig",
    "RivalryConfig",
    "RuntimeProviderConfig",
    "RuntimeProviders",
    "ShapingConfig",
    "SimulationConfig",
    "SnapshotAutosaveConfig",
    "SnapshotConfig",
    "SnapshotGuardrailsConfig",
    "SnapshotIdentityConfig",
    "SnapshotMigrationsConfig",
    "SnapshotStorageConfig",
    "SocialRewardScheduleEntry",
    "SocialRewardStage",
    "SocialRewardWeights",
    "StabilityConfig",
    "StageFlags",
    "StarvationCanaryConfig",
    "SystemFlags",
    "TelemetryBufferConfig",
    "TelemetryConfig",
    "TelemetryRetryPolicy",
    "TelemetryTransformEntry",
    "TelemetryTransformsConfig",
    "TelemetryTransportConfig",
    "TelemetryWorkerConfig",
    "TrainingConfig",
    "TrainingFlags",
    "TrainingSource",
    "load_config",
]

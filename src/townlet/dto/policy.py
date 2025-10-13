"""Policy training result DTOs.

This module defines Pydantic DTOs for all policy training operations, providing
type-safe, validated result structures for BC, PPO, and Anneal training.

All DTOs support serialization via `.model_dump()` for compatibility with legacy
dict-based code and JSON logging.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TrainingResultBase(BaseModel):
    """Base class for all training result DTOs.

    Provides common fields like schema version and duration tracking.
    All training results inherit from this base.
    """

    model_config = ConfigDict(
        frozen=True,  # Immutable after creation
        extra="forbid",  # Reject unknown fields
    )

    schema_version: str = Field(
        default="1.0.0",
        description="DTO schema version for compatibility checks",
    )

    duration_sec: float | None = Field(
        default=None,
        ge=0.0,
        description="Training duration in seconds",
    )


class BCTrainingResultDTO(TrainingResultBase):
    """Result from behaviour cloning training.

    Contains accuracy, loss, and training hyperparameters. Returned by
    BCStrategy.run() and consumed by anneal scheduling.

    Example:
        result = BCTrainingResultDTO(
            mode="bc",
            manifest="/path/to/manifest.json",
            accuracy=0.93,
            loss=0.15,
            learning_rate=1e-3,
            batch_size=32,
            epochs=10,
            duration_sec=45.2,
        )
    """

    mode: str = Field(
        default="bc",
        description="Training mode identifier",
    )

    manifest: str = Field(
        description="Path to BC manifest JSON used for training",
    )

    accuracy: float = Field(
        ge=0.0,
        le=1.0,
        description="Training accuracy (0.0-1.0)",
    )

    loss: float = Field(
        ge=0.0,
        description="Final training loss",
    )

    learning_rate: float = Field(
        gt=0.0,
        description="Learning rate used",
    )

    batch_size: int = Field(
        gt=0,
        description="Batch size used",
    )

    epochs: int = Field(
        gt=0,
        description="Number of epochs completed",
    )

    # Optional fields from BCTrainer
    val_accuracy: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Validation accuracy if validation set used",
    )

    val_loss: float | None = Field(
        default=None,
        ge=0.0,
        description="Validation loss if validation set used",
    )

    weight_decay: float | None = Field(
        default=None,
        ge=0.0,
        description="Weight decay used",
    )

    device: str | None = Field(
        default=None,
        description="Torch device used (e.g., 'cuda', 'cpu')",
    )


class PPOTrainingResultDTO(TrainingResultBase):
    """Result from PPO training.

    Contains detailed metrics from training epochs including losses, advantages,
    gradient norms, and optional anneal context fields.

    This DTO supports multiple telemetry versions (1.0, 1.1, 1.2) with backward
    compatibility. Fields are marked optional if they were added in later versions.

    Dynamic conflict statistics (conflict.*_avg fields) are supported via
    extra="allow" with post-init validation.

    Example:
        result = PPOTrainingResultDTO(
            epoch=5,
            updates=1000,
            transitions=10000,
            loss_policy=0.05,
            loss_value=0.10,
            loss_entropy=0.02,
            loss_total=0.13,
            # ... many more fields
        )
    """

    model_config = ConfigDict(
        frozen=True,
        extra="allow",  # Allow dynamic conflict.* fields
    )

    # Core metrics (v1.0)
    epoch: float = Field(
        gt=0,
        description="Final epoch number completed",
    )

    updates: float = Field(
        ge=0,
        description="Total mini-batch updates performed",
    )

    transitions: float = Field(
        ge=0,
        description="Total transitions processed",
    )

    loss_policy: float = Field(
        description="Policy surrogate loss (averaged)",
    )

    loss_value: float = Field(
        description="Value function loss (averaged)",
    )

    loss_entropy: float = Field(
        description="Entropy bonus (averaged)",
    )

    loss_total: float = Field(
        description="Total loss (policy + value - entropy)",
    )

    clip_fraction: float = Field(
        ge=0.0,
        le=1.0,
        description="Fraction of updates where policy was clipped",
    )

    adv_mean: float = Field(
        description="Mean advantage across mini-batches",
    )

    adv_std: float = Field(
        ge=0.0,
        description="Advantage standard deviation",
    )

    grad_norm: float = Field(
        ge=0.0,
        description="Average gradient norm",
    )

    kl_divergence: float = Field(
        description="KL divergence between old and new policy",
    )

    lr: float = Field(
        gt=0.0,
        description="Learning rate used",
    )

    steps: float = Field(
        ge=0,
        description="Cumulative step count across all runs",
    )

    telemetry_version: float = Field(
        default=1.2,
        description="Telemetry schema version",
    )

    # Health tracking (v1.0)
    adv_zero_std_batches: float = Field(
        default=0.0,
        ge=0.0,
        description="Number of batches with near-zero advantage std",
    )

    adv_min_std: float = Field(
        default=0.0,
        ge=0.0,
        description="Minimum advantage std across batches",
    )

    clip_triggered_minibatches: float = Field(
        default=0.0,
        ge=0.0,
        description="Number of mini-batches where clipping triggered",
    )

    clip_fraction_max: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Maximum clip fraction across mini-batches",
    )

    # Extended metrics (v1.1)
    epoch_duration_sec: float | None = Field(
        default=None,
        ge=0.0,
        description="Duration of final epoch in seconds",
    )

    data_mode: str | None = Field(
        default=None,
        description="Data source mode: 'replay', 'rollout', or 'mixed'",
    )

    cycle_id: float | None = Field(
        default=None,
        description="Training cycle ID",
    )

    batch_entropy_mean: float | None = Field(
        default=None,
        description="Mean entropy across batches",
    )

    batch_entropy_std: float | None = Field(
        default=None,
        ge=0.0,
        description="Entropy standard deviation across batches",
    )

    grad_norm_max: float | None = Field(
        default=None,
        ge=0.0,
        description="Maximum gradient norm across mini-batches",
    )

    kl_divergence_max: float | None = Field(
        default=None,
        description="Maximum KL divergence across mini-batches",
    )

    reward_advantage_corr: float | None = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Correlation between rewards and advantages",
    )

    rollout_ticks: float | None = Field(
        default=None,
        ge=0,
        description="Number of simulation ticks in rollout (if rollout mode)",
    )

    log_stream_offset: float | None = Field(
        default=None,
        ge=0,
        description="Log entry offset for stream continuity",
    )

    # Social/conflict metrics (v1.1)
    queue_conflict_events: float | None = Field(
        default=None,
        ge=0.0,
        description="Queue conflict event count",
    )

    queue_conflict_intensity_sum: float | None = Field(
        default=None,
        ge=0.0,
        description="Total queue conflict intensity",
    )

    shared_meal_events: float | None = Field(
        default=None,
        ge=0.0,
        description="Shared meal event count",
    )

    late_help_events: float | None = Field(
        default=None,
        ge=0.0,
        description="Late help event count",
    )

    shift_takeover_events: float | None = Field(
        default=None,
        ge=0.0,
        description="Shift takeover event count",
    )

    chat_success_events: float | None = Field(
        default=None,
        ge=0.0,
        description="Successful chat event count",
    )

    chat_failure_events: float | None = Field(
        default=None,
        ge=0.0,
        description="Failed chat event count",
    )

    chat_quality_mean: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Mean chat quality score",
    )

    # Anneal context fields (v1.2)
    anneal_cycle: float | None = Field(
        default=None,
        description="Anneal cycle number",
    )

    anneal_stage: str | None = Field(
        default=None,
        description="Anneal stage identifier",
    )

    anneal_dataset: str | None = Field(
        default=None,
        description="Anneal dataset label",
    )

    anneal_bc_accuracy: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="BC accuracy from current cycle",
    )

    anneal_bc_threshold: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="BC accuracy threshold",
    )

    anneal_bc_passed: bool | None = Field(
        default=None,
        description="Whether BC stage passed threshold",
    )

    anneal_loss_baseline: float | None = Field(
        default=None,
        description="Baseline loss from previous stage",
    )

    anneal_queue_baseline: float | None = Field(
        default=None,
        description="Baseline queue conflict events",
    )

    anneal_intensity_baseline: float | None = Field(
        default=None,
        description="Baseline queue conflict intensity",
    )

    anneal_loss_flag: bool | None = Field(
        default=None,
        description="Whether loss exceeded tolerance",
    )

    anneal_queue_flag: bool | None = Field(
        default=None,
        description="Whether queue events dropped below tolerance",
    )

    anneal_intensity_flag: bool | None = Field(
        default=None,
        description="Whether queue intensity dropped below tolerance",
    )

    # Baseline metrics (optional)
    baseline_sample_count: float | None = Field(
        default=None,
        ge=0,
        description="Number of samples in baseline dataset",
    )

    baseline_reward_mean: float | None = Field(
        default=None,
        description="Mean reward in baseline dataset",
    )

    baseline_reward_sum: float | None = Field(
        default=None,
        description="Total reward sum in baseline dataset",
    )

    baseline_reward_sum_mean: float | None = Field(
        default=None,
        description="Mean of per-episode reward sums",
    )

    baseline_log_prob_mean: float | None = Field(
        default=None,
        description="Mean log probability in baseline dataset",
    )

    def model_post_init(self, __context: Any) -> None:
        """Validate that extra fields follow conflict.* naming convention.

        Dynamic conflict statistics fields are allowed but must start with
        'conflict.' prefix to maintain schema consistency.
        """
        # Note: In Pydantic v2 with frozen=True, we can't modify __dict__
        # directly. This validation runs during initialization.
        for key in self.__pydantic_extra__ or {}:
            if not key.startswith("conflict."):
                raise ValueError(
                    f"Unknown field '{key}' in PPOTrainingResultDTO. "
                    "Only 'conflict.*' dynamic fields are allowed."
                )


class AnnealStageResultDTO(TrainingResultBase):
    """Result from a single anneal stage (BC or PPO).

    Tracks whether the stage passed its threshold and carries metrics forward
    to subsequent stages.

    Example:
        # BC stage
        stage = AnnealStageResultDTO(
            cycle=1,
            mode="bc",
            accuracy=0.93,
            loss=0.15,
            threshold=0.90,
            passed=True,
            bc_weight=0.9,
        )

        # PPO stage
        stage = AnnealStageResultDTO(
            cycle=1,
            mode="ppo",
            loss_total=0.12,
            queue_conflict_events=10.0,
            # ... PPO metrics
        )
    """

    cycle: float = Field(
        ge=0,
        description="Anneal cycle number",
    )

    mode: str = Field(
        description="Stage mode: 'bc' or 'ppo'",
    )

    # BC-specific fields
    accuracy: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="BC accuracy (BC stages only)",
    )

    loss: float | None = Field(
        default=None,
        ge=0.0,
        description="Loss value (BC or PPO)",
    )

    threshold: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Accuracy threshold (BC stages only)",
    )

    passed: bool | None = Field(
        default=None,
        description="Whether stage met threshold (BC stages only)",
    )

    bc_weight: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="BC weight for mixed training (BC stages only)",
    )

    rolled_back: bool | None = Field(
        default=None,
        description="Whether training rolled back due to failure",
    )

    # PPO-specific fields (subset of PPOTrainingResultDTO)
    loss_total: float | None = Field(
        default=None,
        description="Total loss (PPO stages only)",
    )

    loss_policy: float | None = Field(
        default=None,
        description="Policy loss (PPO stages only)",
    )

    loss_value: float | None = Field(
        default=None,
        description="Value loss (PPO stages only)",
    )

    queue_conflict_events: float | None = Field(
        default=None,
        ge=0.0,
        description="Queue conflict events (PPO stages only)",
    )

    queue_conflict_intensity_sum: float | None = Field(
        default=None,
        ge=0.0,
        description="Queue conflict intensity (PPO stages only)",
    )

    anneal_loss_flag: bool | None = Field(
        default=None,
        description="Loss flag (PPO stages only)",
    )

    anneal_queue_flag: bool | None = Field(
        default=None,
        description="Queue flag (PPO stages only)",
    )

    anneal_intensity_flag: bool | None = Field(
        default=None,
        description="Intensity flag (PPO stages only)",
    )


class AnnealSummaryDTO(TrainingResultBase):
    """Complete anneal run summary.

    Contains all stage results and final status (PASS/HOLD/FAIL), along with
    tracked baselines and promotion metadata.

    Example:
        summary = AnnealSummaryDTO(
            stages=[stage1, stage2, stage3],
            status="PASS",
            dataset_label="rollout_001",
            baselines={"rollout_001": {"loss_total": 0.12, ...}},
        )
    """

    stages: list[AnnealStageResultDTO] = Field(
        description="Results from each anneal stage",
    )

    status: str = Field(
        description="Final status: 'PASS', 'HOLD', or 'FAIL'",
    )

    dataset_label: str = Field(
        description="Dataset identifier for this anneal run",
    )

    baselines: dict[str, dict[str, float]] = Field(
        default_factory=dict,
        description="Tracked baselines per dataset",
    )

    promotion_pass_streak: int | None = Field(
        default=None,
        ge=0,
        description="Consecutive passes in promotion evaluation",
    )

    promotion_candidate_ready: bool | None = Field(
        default=None,
        description="Whether candidate is ready for promotion",
    )


__all__ = [
    "TrainingResultBase",
    "BCTrainingResultDTO",
    "PPOTrainingResultDTO",
    "AnnealStageResultDTO",
    "AnnealSummaryDTO",
]

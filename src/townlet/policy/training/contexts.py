"""Training context and state management.

This module defines context objects and state containers for training strategies:
- TrainingContext: Shared context passed to strategies before execution
- AnnealContext: PPO training context within anneal schedules
- PPOState: Persistent state for PPO training across runs
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from townlet.config import SimulationConfig
    from townlet.policy.training.services import TrainingServices


@dataclass
class PPOState:
    """Persistent state for PPO training across runs.

    Tracks step count, learning rate, log stream offset, and cycle ID to
    maintain continuity across multiple PPO runs.

    Example:
        state = PPOState()
        # After first run
        state.step = 10000
        state.learning_rate = 1e-3
        state.cycle_id = 0
        # After second run
        state.step = 20000
        state.cycle_id = 1
    """

    step: int = 0
    """Total transitions processed across all PPO runs."""

    learning_rate: float = 1e-3
    """Current optimizer learning rate."""

    log_stream_offset: int = 0
    """Log entry counter for stream continuity."""

    cycle_id: int = -1
    """Current cycle ID (increments on rollout-based training)."""


@dataclass
class AnnealContext:
    """Context for PPO training within anneal schedules.

    Contains baseline metrics and thresholds for evaluating whether PPO
    training has degraded performance relative to BC warm-start.

    Example:
        context = AnnealContext(
            cycle=1,
            stage="ppo",
            dataset_label="rollout_001",
            bc_accuracy=0.93,
            bc_threshold=0.90,
            bc_passed=True,
            loss_baseline=0.15,
            queue_events_baseline=12.0,
            queue_intensity_baseline=45.0,
            loss_tolerance=0.10,
            queue_tolerance=0.15,
        )
        # PPO strategy uses this to emit anneal_* telemetry fields
    """

    cycle: int
    """Anneal cycle number (0-indexed)."""

    stage: str
    """Stage identifier ('bc' or 'ppo')."""

    dataset_label: str
    """Dataset identifier for baseline tracking."""

    bc_accuracy: float | None
    """Accuracy from most recent BC training (if applicable)."""

    bc_threshold: float
    """Minimum BC accuracy required to proceed (e.g., 0.90)."""

    bc_passed: bool
    """Whether BC stage met accuracy threshold."""

    loss_baseline: float | None
    """Baseline total loss from previous PPO stage."""

    queue_events_baseline: float | None
    """Baseline queue conflict event count."""

    queue_intensity_baseline: float | None
    """Baseline queue conflict intensity sum."""

    loss_tolerance: float
    """Relative loss change threshold (e.g., 0.10 = 10%)."""

    queue_tolerance: float
    """Relative queue metric change threshold (e.g., 0.15 = 15%)."""

    def evaluate_ppo_flags(
        self,
        loss_total: float,
        queue_events: float,
        queue_intensity: float,
    ) -> tuple[bool, bool, bool]:
        """Evaluate PPO metrics against baselines.

        Args:
            loss_total: Current PPO total loss.
            queue_events: Current queue conflict event count.
            queue_intensity: Current queue conflict intensity sum.

        Returns:
            Tuple of (loss_flag, queue_flag, intensity_flag).
            True indicates metric exceeded tolerance.
        """
        loss_flag = False
        if self.loss_baseline is not None and self.loss_baseline > 0:
            relative_change = abs(loss_total - self.loss_baseline) / abs(
                self.loss_baseline
            )
            loss_flag = relative_change > self.loss_tolerance

        queue_flag = False
        if self.queue_events_baseline is not None and self.queue_events_baseline > 0:
            queue_flag = queue_events < (1.0 - self.queue_tolerance) * self.queue_events_baseline

        intensity_flag = False
        if (
            self.queue_intensity_baseline is not None
            and self.queue_intensity_baseline > 0
        ):
            intensity_flag = (
                queue_intensity
                < (1.0 - self.queue_tolerance) * self.queue_intensity_baseline
            )

        return (loss_flag, queue_flag, intensity_flag)


@dataclass
class TrainingContext:
    """Shared context passed to strategies before execution.

    Provides access to configuration, services, and optional runtime metadata
    like anneal context or promotion state.

    Example:
        context = TrainingContext(
            config=config,
            services=services,
            anneal_context=AnnealContext(...),
        )
        strategy.prepare(context)
        result = strategy.run(...)
    """

    config: SimulationConfig
    """Simulation configuration (mutable)."""

    services: TrainingServices
    """Shared service instances (rollout, replay, promotion)."""

    anneal_context: AnnealContext | None = None
    """Current anneal stage context (PPO strategies only)."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional runtime metadata (extensible)."""

    @classmethod
    def from_config(cls, config: SimulationConfig) -> TrainingContext:
        """Create context from configuration.

        Args:
            config: Simulation configuration.

        Returns:
            TrainingContext with services initialized.
        """
        from townlet.policy.training.services import TrainingServices

        return cls(
            config=config,
            services=TrainingServices.from_config(config),
        )


__all__ = [
    "AnnealContext",
    "PPOState",
    "TrainingContext",
]

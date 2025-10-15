"""Training orchestrator façade.

This module provides a thin façade over the training strategies, offering a
simple API for BC, PPO, and Anneal training. The orchestrator delegates to
strategy implementations while managing the training context.

This is the new, refactored version that replaces the monolithic
PolicyTrainingOrchestrator with a clean strategy-based architecture.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from townlet.config import SimulationConfig
    from townlet.dto.policy import AnnealSummaryDTO, BCTrainingResultDTO, PPOTrainingResultDTO
    from townlet.policy.replay_buffer import InMemoryReplayDataset
    from townlet.policy.training.contexts import TrainingContext


class TrainingOrchestrator:
    """Training orchestrator façade.

    Provides a simple API for BC, PPO, and Anneal training by delegating to
    strategy implementations. Manages training context and services.

    Example:
        orchestrator = TrainingOrchestrator(config)
        bc_result = orchestrator.run_bc()
        ppo_result = orchestrator.run_ppo()
        anneal_result = orchestrator.run_anneal()
    """

    def __init__(self, config: SimulationConfig) -> None:
        """Initialize training orchestrator.

        Args:
            config: Simulation configuration.
        """
        self.config = config
        self._context: TrainingContext | None = None

    @property
    def context(self) -> TrainingContext:
        """Get or create training context."""
        if self._context is None:
            from townlet.policy.training.contexts import TrainingContext

            self._context = TrainingContext.from_config(self.config)
        return self._context

    def run_bc(
        self,
        *,
        manifest: Path | None = None,
    ) -> BCTrainingResultDTO:
        """Run BC training.

        Args:
            manifest: Optional BC manifest path override.

        Returns:
            BC training result with accuracy and metrics.
        """
        from townlet.policy.training.strategies import BCStrategy

        # Stash original manifest and apply override if provided
        original_manifest = self.config.training.bc.manifest
        if manifest is not None:
            self.config.training.bc.manifest = manifest

        try:
            strategy = BCStrategy()
            return strategy.run(self.context)
        finally:
            # Restore original manifest to avoid persistent mutation
            self.config.training.bc.manifest = original_manifest

    def run_ppo(
        self,
        *,
        dataset_config: object | None = None,
        in_memory_dataset: InMemoryReplayDataset | None = None,
        epochs: int = 1,
        log_path: Path | None = None,
        log_frequency: int = 1,
        max_log_entries: int | None = None,
        device_str: str | None = None,
    ) -> PPOTrainingResultDTO:
        """Run PPO training.

        Args:
            dataset_config: Replay dataset config.
            in_memory_dataset: In-memory dataset for rollouts.
            epochs: Number of training epochs.
            log_path: Optional JSONL log path.
            log_frequency: Log every N epochs.
            max_log_entries: Max entries per log file.
            device_str: Device override (e.g., 'cuda:1').

        Returns:
            PPO training result with losses and metrics.
        """
        from townlet.policy.training.strategies import PPOStrategy

        strategy = PPOStrategy()
        return strategy.run(
            self.context,
            dataset_config=dataset_config,
            in_memory_dataset=in_memory_dataset,
            epochs=epochs,
            log_path=log_path,
            log_frequency=log_frequency,
            max_log_entries=max_log_entries,
            device_str=device_str,
        )

    def run_anneal(
        self,
        *,
        dataset_config: object | None = None,
        in_memory_dataset: object | None = None,
        log_dir: Path | None = None,
        bc_manifest: Path | None = None,
    ) -> AnnealSummaryDTO:
        """Run anneal training schedule.

        Args:
            dataset_config: Replay dataset config for PPO stages.
            in_memory_dataset: In-memory dataset for PPO stages.
            log_dir: Optional directory to save results JSON.
            bc_manifest: Optional BC manifest path override.

        Returns:
            Anneal summary with stage results and status.
        """
        from townlet.policy.training.strategies import AnnealStrategy

        strategy = AnnealStrategy()
        return strategy.run(
            self.context,
            dataset_config=dataset_config,
            in_memory_dataset=in_memory_dataset,
            log_dir=log_dir,
            bc_manifest=bc_manifest,
        )

    def run_rollout_ppo(
        self,
        *,
        ticks: int,
        batch_size: int = 1,
        auto_seed_agents: bool = False,
        output_dir: Path | None = None,
        prefix: str = "rollout_sample",
        compress: bool = True,
        epochs: int = 1,
        log_path: Path | None = None,
        log_frequency: int = 1,
        max_log_entries: int | None = None,
    ) -> PPOTrainingResultDTO:
        """Capture rollout and run PPO training.

        This method applies the social reward schedule stage before capturing
        the rollout, matching the old orchestrator behavior.

        Args:
            ticks: Number of simulation ticks to run.
            batch_size: Batch size for dataset.
            auto_seed_agents: Whether to seed default agents if none exist.
            output_dir: Optional directory to save rollout buffer.
            prefix: Filename prefix for saved rollout.
            compress: Whether to compress saved rollout.
            epochs: Number of PPO training epochs.
            log_path: Optional JSONL log path.
            log_frequency: Log every N epochs.
            max_log_entries: Max entries per log file.

        Returns:
            PPO training result with losses and metrics.
        """
        from townlet.policy.training.strategies import PPOStrategy

        # Get next cycle_id and apply social reward stage before capture
        # This matches old orchestrator behavior (training_orchestrator.py:214-215)
        next_cycle = int(self.context.metadata.get("cycle_id", -1)) + 1
        self._apply_social_reward_stage(next_cycle)

        # Capture rollout with updated stage
        buffer = self.context.services.rollout.capture(
            ticks=ticks,
            auto_seed_agents=auto_seed_agents,
            output_dir=output_dir,
            prefix=prefix,
            compress=compress,
        )

        # Build dataset from buffer
        dataset = buffer.build_dataset(batch_size=batch_size)

        # Run PPO on captured data
        strategy = PPOStrategy()
        return strategy.run(
            self.context,
            dataset_config=None,
            in_memory_dataset=dataset,
            epochs=epochs,
            log_path=log_path,
            log_frequency=log_frequency,
            max_log_entries=max_log_entries,
        )

    def _select_social_reward_stage(self, cycle_id: int) -> str | None:
        """Select social reward stage from schedule based on cycle_id.

        Args:
            cycle_id: Current training cycle ID.

        Returns:
            Selected stage name, or None if no schedule configured.
        """
        training_cfg = getattr(self.config, "training", None)
        if training_cfg is None:
            return None

        # Check for override first
        stage = getattr(training_cfg, "social_reward_stage_override", None)

        # Process schedule
        schedule = getattr(training_cfg, "social_reward_schedule", []) or []
        try:
            iterable = sorted(
                schedule,
                key=lambda entry: int(getattr(entry, "cycle", 0)),
            )
        except TypeError:
            iterable = []

        # Find the stage for the highest cycle <= cycle_id
        for entry in iterable:
            entry_cycle = int(getattr(entry, "cycle", 0))
            if cycle_id >= entry_cycle:
                stage = getattr(entry, "stage", stage)

        return stage

    def _apply_social_reward_stage(self, cycle_id: int) -> None:
        """Apply social reward stage from schedule to config.

        Args:
            cycle_id: Current training cycle ID.
        """
        stage = self._select_social_reward_stage(cycle_id)
        if stage is None:
            return

        # Get current stage
        current = getattr(self.config.features.stages, "social_rewards", None)

        # Only mutate if changed (use setattr to avoid literal type constraint)
        if stage != current:
            setattr(self.config.features.stages, "social_rewards", stage)  # noqa: B010

    def run(self) -> None:
        """Entry point for CLI training runs based on config.training.source.

        Delegates to run_bc() or run_anneal() based on configuration.

        Raises:
            NotImplementedError: If training mode is not supported.
        """
        mode = self.config.training.source
        if mode == "bc":
            self.run_bc()
            return
        if mode == "anneal":
            self.run_anneal()
            return
        raise NotImplementedError(
            f"Training mode '{mode}' is not supported via run(); "
            "use scripts/run_training.py with --mode."
        )


__all__ = ["TrainingOrchestrator"]

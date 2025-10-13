"""Behaviour cloning training strategy.

This module implements the BC training strategy, extracting the logic from
PolicyTrainingOrchestrator into a focused, testable, stateless class.

BC training warm-starts the policy network using expert demonstrations before
RL fine-tuning. This strategy is used standalone or as part of anneal schedules.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from townlet.dto.policy import BCTrainingResultDTO
    from townlet.policy.training.contexts import TrainingContext


class BCStrategy:
    """Behaviour cloning training strategy.

    Trains a policy network using imitation learning from expert demonstrations.
    Returns typed DTOs with validation and duration tracking.

    Requires PyTorch to be installed. Checks availability before execution.

    Example:
        strategy = BCStrategy()
        result = strategy.run(context)
        print(f"BC accuracy: {result.accuracy:.2%}")
    """

    def run(self, context: TrainingContext) -> BCTrainingResultDTO:
        """Execute BC training.

        Args:
            context: Training context with config and services.

        Returns:
            BC training result with accuracy, loss, and hyperparameters.

        Raises:
            TorchNotAvailableError: If PyTorch is not installed.
            ValueError: If BC manifest is not configured or invalid.
        """
        from townlet.dto.policy import BCTrainingResultDTO
        from townlet.policy.bc import BCTrainer, BCTrajectoryDataset, load_bc_samples
        from townlet.policy.bc import BCTrainingConfig as BCTrainingParams
        from townlet.policy.models import (
            ConflictAwarePolicyConfig,
            TorchNotAvailableError,
            torch_available,
        )

        # Guard: Check torch availability
        if not torch_available():
            raise TorchNotAvailableError(
                "PyTorch is required for behaviour cloning training. "
                "Install with: pip install -e .[ml]"
            )

        start_time = time.perf_counter()

        # Resolve manifest path
        bc_settings = context.config.training.bc
        manifest_path = bc_settings.manifest
        if manifest_path is None:
            raise ValueError(
                "BC manifest is required for behaviour cloning. "
                "Configure training.bc.manifest in your config."
            )

        # Load BC dataset
        samples = load_bc_samples(manifest_path)
        dataset = BCTrajectoryDataset(samples)

        # Build training parameters
        params = BCTrainingParams(
            learning_rate=bc_settings.learning_rate,
            batch_size=bc_settings.batch_size,
            epochs=bc_settings.epochs,
            weight_decay=bc_settings.weight_decay,
            device=bc_settings.device,
        )

        # Build policy config
        policy_cfg = ConflictAwarePolicyConfig(
            feature_dim=dataset.feature_dim,
            map_shape=dataset.map_shape,
            action_dim=dataset.action_dim,
        )

        # Train
        trainer = BCTrainer(params, policy_cfg)
        metrics = trainer.fit(dataset)

        # Calculate duration
        duration_sec = time.perf_counter() - start_time

        # Build typed DTO
        result = BCTrainingResultDTO(
            mode="bc",
            manifest=str(manifest_path),
            accuracy=float(metrics.get("accuracy", 0.0)),
            loss=float(metrics.get("loss", 0.0)),
            learning_rate=float(params.learning_rate),
            batch_size=int(params.batch_size),
            epochs=int(params.epochs),
            duration_sec=duration_sec,
            val_accuracy=(
                float(metrics["val_accuracy"])
                if "val_accuracy" in metrics
                else None
            ),
            val_loss=(
                float(metrics["val_loss"])
                if "val_loss" in metrics
                else None
            ),
            weight_decay=(
                float(params.weight_decay)
                if params.weight_decay is not None
                else None
            ),
            device=params.device,
        )

        return result


__all__ = ["BCStrategy"]

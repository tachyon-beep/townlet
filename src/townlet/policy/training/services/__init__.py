"""Training services (torch-free).

This module contains torch-free training support services:
- ReplayDatasetService: Replay dataset management
- RolloutCaptureService: Rollout capture and buffering
- PromotionServiceAdapter: Promotion tracking and evaluation
- TrainingServices: Service composition and factory

All services are importable without PyTorch installed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from townlet.policy.training.services.promotion import PromotionServiceAdapter
from townlet.policy.training.services.replay import ReplayDatasetService
from townlet.policy.training.services.rollout import RolloutCaptureService

if TYPE_CHECKING:
    from townlet.config import SimulationConfig


class TrainingServices:
    """Composition of all training services.

    Provides a single access point to all training support services:
    replay dataset management, rollout capture, and promotion tracking.
    All services are torch-free and independently testable.

    Example:
        services = TrainingServices.from_config(config)
        dataset = services.replay.build_dataset(manifest_path)
        buffer = services.rollout.capture(ticks=100)
        services.promotion.record_evaluation(status="PASS", results=[...])
    """

    def __init__(
        self,
        replay: ReplayDatasetService,
        rollout: RolloutCaptureService,
        promotion: PromotionServiceAdapter,
    ) -> None:
        """Initialize training services with individual service instances.

        Args:
            replay: Replay dataset service.
            rollout: Rollout capture service.
            promotion: Promotion service adapter.
        """
        self.replay = replay
        self.rollout = rollout
        self.promotion = promotion

    @classmethod
    def from_config(cls, config: SimulationConfig) -> TrainingServices:
        """Create training services from configuration.

        Args:
            config: Simulation configuration.

        Returns:
            TrainingServices with all services initialized.
        """
        replay = ReplayDatasetService(config)
        rollout = RolloutCaptureService(config)
        promotion = PromotionServiceAdapter(config)
        return cls(replay=replay, rollout=rollout, promotion=promotion)


__all__ = [
    "PromotionServiceAdapter",
    "ReplayDatasetService",
    "RolloutCaptureService",
    "TrainingServices",
]

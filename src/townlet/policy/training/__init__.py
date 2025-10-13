"""Policy training strategies and orchestration.

This package provides the training infrastructure for policy learning, including:
- Training strategies (BC, PPO, Anneal)
- Training services (Rollout, Replay, Promotion)
- Training orchestrator façade
- Context and state management

The package is designed with torch isolation in mind - services are importable
without PyTorch, while strategies require torch and check availability at runtime.
"""

from __future__ import annotations

from townlet.policy.training.orchestrator import TrainingOrchestrator
from townlet.policy.training.services import (
    PromotionServiceAdapter,
    ReplayDatasetService,
    RolloutCaptureService,
    TrainingServices,
)

# Alias for backward compatibility during transition
PolicyTrainingOrchestrator = TrainingOrchestrator

__all__ = [
    "PolicyTrainingOrchestrator",  # Alias for compatibility
    "PromotionServiceAdapter",
    "ReplayDatasetService",
    "RolloutCaptureService",
    "TrainingOrchestrator",
    "TrainingServices",
]

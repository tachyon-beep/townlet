"""Policy training strategies.

This package provides training strategy implementations following the strategy
pattern. Each strategy encapsulates a specific training algorithm and returns
typed DTOs.

Strategies:
- BCStrategy: Behaviour cloning from expert demonstrations
- PPOStrategy: Proximal Policy Optimization reinforcement learning
- AnnealStrategy: Anneal schedule orchestration (coordinates BC + PPO)

All strategies require PyTorch and check availability before execution.
"""

from __future__ import annotations

from townlet.policy.training.strategies.anneal import AnnealStrategy
from townlet.policy.training.strategies.base import TrainingStrategy
from townlet.policy.training.strategies.bc import BCStrategy
from townlet.policy.training.strategies.ppo import PPOStrategy

__all__ = [
    "AnnealStrategy",
    "BCStrategy",
    "PPOStrategy",
    "TrainingStrategy",
]

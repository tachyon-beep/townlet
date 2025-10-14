"""Base training strategy protocol.

This module defines the protocol that all training strategies must implement.
Strategies encapsulate specific training algorithms (BC, PPO, Anneal) and
return typed DTOs rather than dicts.

All strategies require PyTorch and should check availability before execution.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from townlet.dto.policy import TrainingResultBase
    from townlet.policy.training.contexts import TrainingContext


@runtime_checkable
class TrainingStrategy(Protocol):
    """Protocol for training strategies.

    All training strategies must implement a `run()` method that:
    1. Accepts a TrainingContext with config and services
    2. Checks torch availability before execution
    3. Returns a typed DTO (subclass of TrainingResultBase)
    4. Tracks execution duration

    Strategies are stateless and reusable. All state management should
    be done through the context or services.

    Example:
        strategy = BCStrategy()
        result = strategy.run(context)
        print(f"BC accuracy: {result.accuracy}")
    """

    def run(self, context: TrainingContext) -> TrainingResultBase:
        """Execute the training strategy.

        Args:
            context: Training context with config, services, and metadata.

        Returns:
            Typed training result DTO.

        Raises:
            TorchNotAvailableError: If PyTorch is not available.
            ValueError: If required configuration is missing or invalid.
        """
        ...


__all__ = ["TrainingStrategy"]

"""Policy/training configuration models.

Separated from the legacy loader to align configuration schemas with subsystem
packages and keep the config package acyclic.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PPOConfig(BaseModel):
    """Config for PPO training hyperparameters."""

    learning_rate: float = Field(3e-4, gt=0.0, description="Optimizer learning rate")
    clip_param: float = Field(0.2, ge=0.0, le=1.0, description="Policy ratio clip parameter")
    value_loss_coef: float = Field(0.5, ge=0.0, description="Weight of value loss term")
    entropy_coef: float = Field(0.01, ge=0.0, description="Entropy bonus weight")
    num_epochs: int = Field(4, ge=1, le=64, description="Epochs per PPO update")
    mini_batch_size: int = Field(32, ge=1, description="Minibatch size for PPO updates")
    gae_lambda: float = Field(0.95, ge=0.0, le=1.0, description="GAE lambda")
    gamma: float = Field(0.99, ge=0.0, le=1.0, description="Discount factor")
    max_grad_norm: float = Field(0.5, ge=0.0, description="Max gradient norm for clipping")
    value_clip: float = Field(0.2, ge=0.0, le=1.0, description="Clipping for value function updates")
    advantage_normalization: bool = True
    num_mini_batches: int = Field(4, ge=1, le=1024, description="Number of minibatches per epoch")


__all__ = ["PPOConfig"]


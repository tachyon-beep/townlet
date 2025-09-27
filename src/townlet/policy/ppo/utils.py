"""Utility functions for PPO advantage and loss computation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import torch


@dataclass
class AdvantageReturns:
    """Container for PPO advantage and return tensors."""

    advantages: torch.Tensor
    returns: torch.Tensor


def compute_gae(
    rewards: torch.Tensor,
    value_preds: torch.Tensor,
    dones: torch.Tensor,
    gamma: float,
    gae_lambda: float,
) -> AdvantageReturns:
    """Compute Generalized Advantage Estimation (GAE).

    Args:
        rewards: Tensor shaped (batch, timesteps).
        value_preds: Tensor shaped (batch, timesteps) or (batch, timesteps + 1).
        dones: Tensor shaped (batch, timesteps) with 1.0 when episode terminates.
        gamma: Discount factor.
        gae_lambda: GAE smoothing coefficient.

    Returns:
        AdvantageReturns with tensors shaped (batch, timesteps).
    """

    if rewards.ndim != 2 or dones.ndim != 2:
        raise ValueError("Rewards and dones must be 2D tensors (batch, timesteps)")

    batch_size, timesteps = rewards.shape
    if value_preds.ndim != 2:
        raise ValueError("value_preds must be a 2D tensor (batch, steps or steps+1)")

    value_steps = value_preds.shape[1]
    if value_steps not in {timesteps, timesteps + 1}:
        raise ValueError(
            "value_preds must align with rewards (same length) or provide bootstrap "
            "value for the final timestep"
        )

    advantages = torch.zeros_like(rewards)
    returns = torch.zeros_like(rewards)

    for b in range(batch_size):
        gae = torch.zeros(1, dtype=rewards.dtype, device=rewards.device)
        for t in reversed(range(timesteps)):
            mask = 1.0 - dones[b, t]
            next_value = (
                value_preds[b, t + 1]
                if value_steps == timesteps + 1
                else value_preds[b, t]
            )
            delta = rewards[b, t] + gamma * next_value * mask - value_preds[b, t]
            gae = delta + gamma * gae_lambda * mask * gae
            advantages[b, t] = gae
            returns[b, t] = gae + value_preds[b, t]

    return AdvantageReturns(advantages=advantages, returns=returns)


def normalize_advantages(advantages: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    """Normalize advantage estimates to zero mean/unit variance."""

    mean = advantages.mean()
    std = advantages.std(unbiased=False)
    if torch.isnan(mean) or torch.isnan(std):  # pragma: no cover - defensive guard
        return advantages
    return (advantages - mean) / (std + eps)


def value_baseline_from_old_preds(
    value_preds: torch.Tensor, timesteps: int
) -> torch.Tensor:
    """Extract baseline values aligned with each timestep from stored predictions."""

    if value_preds.ndim != 2:
        raise ValueError("value_preds must be 2D (batch, steps)")
    if value_preds.shape[1] == timesteps + 1:
        return value_preds[:, :timesteps]
    if value_preds.shape[1] == timesteps:
        return value_preds
    raise ValueError(
        "value_preds must provide estimates for each timestep or include a bootstrap value"
    )


def clipped_value_loss(
    new_values: torch.Tensor,
    returns: torch.Tensor,
    old_values: torch.Tensor,
    value_clip: float,
) -> torch.Tensor:
    """Compute the clipped value loss term."""

    if new_values.shape != returns.shape or new_values.shape != old_values.shape:
        raise ValueError(
            "new_values, returns, and old_values must share the same shape"
        )

    if value_clip > 0.0:
        value_pred_clipped = old_values + torch.clamp(
            new_values - old_values, -value_clip, value_clip
        )
        value_losses = torch.max(
            (new_values - returns).pow(2),
            (value_pred_clipped - returns).pow(2),
        )
    else:
        value_losses = (new_values - returns).pow(2)
    return 0.5 * value_losses.mean()


def policy_surrogate(
    new_log_probs: torch.Tensor,
    old_log_probs: torch.Tensor,
    advantages: torch.Tensor,
    clip_param: float,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Compute PPO clipped policy loss and clip fraction."""

    if not (new_log_probs.shape == old_log_probs.shape == advantages.shape):
        raise ValueError("log_probs and advantages must share identical shape")

    ratio = torch.exp(new_log_probs - old_log_probs)
    unclipped = ratio * advantages
    clipped = torch.clamp(ratio, 1.0 - clip_param, 1.0 + clip_param) * advantages
    loss = -torch.min(unclipped, clipped).mean()
    clip_frac = (ratio.gt(1.0 + clip_param) | ratio.lt(1.0 - clip_param)).float().mean()
    return loss, clip_frac

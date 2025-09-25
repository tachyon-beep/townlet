from __future__ import annotations

import torch

from townlet.policy.ppo import utils


def test_compute_gae_single_step() -> None:
    rewards = torch.tensor([[1.0]])
    value_preds = torch.tensor([[0.5, 0.4]])
    dones = torch.tensor([[0.0]])
    result = utils.compute_gae(
        rewards=rewards,
        value_preds=value_preds,
        dones=dones,
        gamma=0.99,
        gae_lambda=0.95,
    )
    assert torch.allclose(result.advantages, torch.tensor([[0.896]]), atol=1e-6)
    assert torch.allclose(result.returns, torch.tensor([[1.396]]), atol=1e-6)


def test_value_baseline_from_old_preds_handles_bootstrap() -> None:
    tensor = torch.tensor([[0.5, 0.4]])
    baseline = utils.value_baseline_from_old_preds(tensor, timesteps=1)
    assert torch.allclose(baseline, torch.tensor([[0.5]]))

    tensor_same = torch.tensor([[0.7]])
    baseline_same = utils.value_baseline_from_old_preds(tensor_same, timesteps=1)
    assert torch.allclose(baseline_same, torch.tensor([[0.7]]))


def test_policy_surrogate_clipping_behaviour() -> None:
    new_log_probs = torch.log(torch.tensor([0.5, 0.1]))
    old_log_probs = torch.log(torch.tensor([0.2, 0.2]))
    advantages = torch.tensor([1.0, -1.0])
    loss, clip_frac = utils.policy_surrogate(
        new_log_probs=new_log_probs,
        old_log_probs=old_log_probs,
        advantages=advantages,
        clip_param=0.2,
    )
    assert loss.item() < 0
    assert clip_frac.item() > 0.0


def test_clipped_value_loss_respects_clip() -> None:
    new_values = torch.tensor([1.0, 1.5])
    returns = torch.tensor([1.2, 1.0])
    old_values = torch.tensor([0.8, 1.4])
    loss = utils.clipped_value_loss(
        new_values=new_values,
        returns=returns,
        old_values=old_values,
        value_clip=0.1,
    )
    value_pred_clipped = old_values + torch.clamp(new_values - old_values, -0.1, 0.1)
    manual = 0.5 * torch.max(
        (new_values - returns).pow(2),
        (value_pred_clipped - returns).pow(2),
    ).mean()
    assert torch.allclose(loss, manual)

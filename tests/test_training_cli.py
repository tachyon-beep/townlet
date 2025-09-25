from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from townlet.config import PPOConfig, load_config

from scripts import run_training


def _make_namespace(**kwargs: object) -> Namespace:
    defaults = {
        "ppo_learning_rate": None,
        "ppo_clip_param": None,
        "ppo_value_loss_coef": None,
        "ppo_entropy_coef": None,
        "ppo_num_epochs": None,
        "ppo_mini_batch_size": None,
        "ppo_num_mini_batches": None,
        "ppo_gae_lambda": None,
        "ppo_gamma": None,
        "ppo_max_grad_norm": None,
        "ppo_value_clip": None,
        "ppo_normalize_advantages": None,
    }
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_collect_ppo_overrides_handles_values() -> None:
    ns = _make_namespace(
        ppo_learning_rate=1e-4,
        ppo_clip_param=0.15,
        ppo_value_loss_coef=0.7,
        ppo_entropy_coef=0.02,
        ppo_num_epochs=8,
        ppo_mini_batch_size=64,
        ppo_num_mini_batches=4,
        ppo_gae_lambda=0.9,
        ppo_gamma=0.995,
        ppo_max_grad_norm=0.8,
        ppo_value_clip=0.1,
        ppo_normalize_advantages=True,
    )
    overrides = run_training._collect_ppo_overrides(ns)
    assert overrides["learning_rate"] == 1e-4
    assert overrides["clip_param"] == 0.15
    assert overrides["value_loss_coef"] == 0.7
    assert overrides["entropy_coef"] == 0.02
    assert overrides["num_epochs"] == 8
    assert overrides["mini_batch_size"] == 64
    assert overrides["num_mini_batches"] == 4
    assert overrides["gae_lambda"] == 0.9
    assert overrides["gamma"] == 0.995
    assert overrides["max_grad_norm"] == 0.8
    assert overrides["value_clip"] == 0.1
    assert overrides["advantage_normalization"] is True


def test_apply_ppo_overrides_creates_config_when_missing() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    assert config.ppo is None
    overrides = {
        "learning_rate": 5e-4,
        "clip_param": 0.25,
        "advantage_normalization": False,
    }
    run_training._apply_ppo_overrides(config, overrides)
    assert isinstance(config.ppo, PPOConfig)
    assert config.ppo.learning_rate == 5e-4
    assert config.ppo.clip_param == 0.25
    assert config.ppo.advantage_normalization is False


def test_apply_ppo_overrides_updates_existing_model() -> None:
    base = PPOConfig(learning_rate=3e-4, clip_param=0.2)
    overrides = {"learning_rate": 1e-4, "max_grad_norm": 1.0}
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.ppo = base
    run_training._apply_ppo_overrides(config, overrides)
    assert config.ppo.learning_rate == 1e-4
    assert config.ppo.max_grad_norm == 1.0

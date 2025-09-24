from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.rewards.engine import RewardEngine
from townlet.world.grid import AgentSnapshot, WorldState


def _make_world(hunger: float = 0.5) -> WorldState:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": hunger, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    return world


def test_reward_negative_with_high_deficit() -> None:
    world = _make_world(hunger=0.1)
    rewards = RewardEngine(world.config).compute(world, terminated={})
    assert rewards["alice"] < 0.0


def test_reward_clipped_by_config() -> None:
    world = _make_world(hunger=0.0)
    engine = RewardEngine(world.config)
    rewards = engine.compute(world, terminated={})
    assert rewards["alice"] >= -world.config.rewards.clip.clip_per_tick


def test_survival_tick_positive_when_balanced() -> None:
    world = _make_world(hunger=0.8)
    engine = RewardEngine(world.config)
    rewards = engine.compute(world, terminated={})
    expected = world.config.rewards.survival_tick
    weights = world.config.rewards.needs_weights
    for need, value in world.agents["alice"].needs.items():
        weight = getattr(weights, need, 0.0)
        deficit = 1.0 - value
        expected -= weight * max(0.0, deficit) ** 2
    clip = world.config.rewards.clip.clip_per_tick
    expected = max(min(expected, clip), -clip)
    assert rewards["alice"] == pytest.approx(expected)

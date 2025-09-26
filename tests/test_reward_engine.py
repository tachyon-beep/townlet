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


def test_chat_reward_applied_for_successful_conversation() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    for agent_id in ("alice", "bob"):
        world.agents[agent_id] = AgentSnapshot(
            agent_id=agent_id,
            position=(0, 0),
            needs={"hunger": 1.0, "hygiene": 1.0, "energy": 1.0},
            wallet=1.0,
        )
    world.tick = 100
    world.record_chat_success("alice", "bob", quality=1.0)

    engine = RewardEngine(world.config)
    terminated = {agent_id: False for agent_id in world.agents}
    rewards = engine.compute(world, terminated)

    base = world.config.rewards.survival_tick
    social_cfg = world.config.rewards.social
    expected_bonus = (
        social_cfg.C1_chat_base
        + social_cfg.C1_coeff_trust * 0.05
        + social_cfg.C1_coeff_fam * 0.10
    )
    assert rewards["alice"] == pytest.approx(base + expected_bonus, rel=1e-5)
    assert rewards["bob"] == pytest.approx(base + expected_bonus, rel=1e-5)


def test_chat_reward_skipped_when_needs_override_triggers() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.1, "hygiene": 1.0, "energy": 1.0},
        wallet=1.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(0, 0),
        needs={"hunger": 1.0, "hygiene": 1.0, "energy": 1.0},
        wallet=1.0,
    )
    world.tick = 5
    world.record_chat_success("alice", "bob", quality=1.0)

    engine = RewardEngine(world.config)
    terminated = {agent_id: False for agent_id in world.agents}
    rewards = engine.compute(world, terminated)

    assert rewards["bob"] > rewards["alice"]
    assert rewards["alice"] <= 0.0


def test_chat_reward_blocked_within_termination_window() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    for agent_id in ("alice", "bob"):
        world.agents[agent_id] = AgentSnapshot(
            agent_id=agent_id,
            position=(0, 0),
            needs={"hunger": 1.0, "hygiene": 1.0, "energy": 1.0},
            wallet=1.0,
        )
    engine = RewardEngine(world.config)

    world.tick = 50
    world.record_chat_success("alice", "bob", quality=1.0)
    rewards = engine.compute(world, {"alice": True, "bob": False})
    assert rewards["alice"] <= 0.0
    assert rewards["bob"] > 0.0

    world.tick = 55
    world.record_chat_success("alice", "bob", quality=1.0)
    rewards = engine.compute(world, {"alice": False, "bob": False})
    assert rewards["alice"] <= 0.0  # still within termination window

    world.tick = 70
    world.record_chat_success("alice", "bob", quality=1.0)
    rewards = engine.compute(world, {"alice": False, "bob": False})
    assert rewards["alice"] > 0.0

from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.lifecycle.manager import LifecycleManager
from townlet.world.grid import AgentSnapshot, WorldState

CONFIG_PATH = Path("configs/examples/poc_hybrid.yaml")


def _make_world() -> tuple[LifecycleManager, WorldState]:
    config = load_config(CONFIG_PATH)
    world = WorldState.from_config(config)
    world.agents.clear()
    world.tick = 0
    manager = LifecycleManager(config)
    return manager, world


def _spawn_agent(
    world: WorldState,
    *,
    hunger: float = 0.8,
    hygiene: float = 0.7,
    energy: float = 0.6,
) -> AgentSnapshot:
    snapshot = world.lifecycle_service.spawn_agent(
        "alice",
        (0, 0),
        needs={"hunger": hunger, "hygiene": hygiene, "energy": energy},
        wallet=0.0,
    )
    return world.agents[snapshot.agent_id]


def test_need_decay_matches_config() -> None:
    _, world = _make_world()
    snapshot = _spawn_agent(world)
    decay = world.config.rewards.decay_rates

    world._apply_need_decay()

    assert snapshot.needs["hunger"] == pytest.approx(0.8 - decay["hunger"])
    assert snapshot.needs["hygiene"] == pytest.approx(0.7 - decay["hygiene"])
    assert snapshot.needs["energy"] == pytest.approx(0.6 - decay["energy"])
    assert all(0.0 <= value <= 1.0 for value in snapshot.needs.values())


def test_need_decay_clamps_at_zero() -> None:
    _, world = _make_world()
    snapshot = _spawn_agent(world, hunger=0.002, hygiene=0.003, energy=0.001)

    world._apply_need_decay()

    assert snapshot.needs["hunger"] == pytest.approx(0.0)
    assert snapshot.needs["hygiene"] == pytest.approx(0.0)
    assert snapshot.needs["energy"] == pytest.approx(0.0)


def test_lifecycle_hunger_threshold_applies() -> None:
    manager, world = _make_world()
    snapshot = _spawn_agent(world)

    snapshot.needs["hunger"] = 0.04
    result = manager.evaluate(world, tick=0)
    assert result["alice"] is False

    snapshot.needs["hunger"] = 0.03
    result = manager.evaluate(world, tick=1)
    assert result["alice"] is True


def test_agent_snapshot_clamps_on_init() -> None:
    snapshot = AgentSnapshot(
        agent_id="test",
        position=(0, 0),
        needs={"hunger": 1.5, "hygiene": -0.2, "energy": "0.4"},
        wallet=0.0,
    )

    assert snapshot.needs["hunger"] == pytest.approx(1.0)
    assert snapshot.needs["hygiene"] == pytest.approx(0.0)
    assert snapshot.needs["energy"] == pytest.approx(0.4)

from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config.loader import load_config
from townlet.policy.behavior import ScriptedBehavior
from townlet.world.grid import AgentSnapshot, WorldState


@pytest.fixture(scope="module")
def base_config():
    return load_config(Path("configs/examples/poc_hybrid.yaml"))


def _build_world(base_config):
    world = WorldState.from_config(base_config)
    fridge_id = next(
        object_id
        for object_id, obj in world.objects.items()
        if obj.object_type == "fridge"
    )
    world.objects[fridge_id].stock.setdefault("meals", 0)
    world.objects[fridge_id].stock["meals"] = 5
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(10, 10),
        needs={"hunger": 0.15, "hygiene": 0.5, "energy": 0.5},
        wallet=2.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(11, 10),
        needs={"hunger": 0.4, "hygiene": 0.5, "energy": 0.5},
        wallet=2.0,
    )
    return world, fridge_id


def _occupy(world: WorldState, object_id: str, agent_id: str) -> None:
    assert world.queue_manager.request_access(object_id, agent_id, tick=0)


def test_agents_avoid_rivals_when_rivalry_high(base_config):
    world, fridge_id = _build_world(base_config)
    _occupy(world, fridge_id, "bob")
    world.register_rivalry_conflict("alice", "bob", intensity=5.0)
    behaviour = ScriptedBehavior(base_config)

    intent = behaviour.decide(world, "alice")

    assert intent.kind == "wait"


def test_agents_request_again_after_rivalry_decay(base_config):
    world, fridge_id = _build_world(base_config)
    _occupy(world, fridge_id, "bob")
    world.register_rivalry_conflict("alice", "bob", intensity=2.0)
    ledger = world._rivalry_ledgers["alice"]  # type: ignore[attr-defined]
    ledger.decay(ticks=200)
    behaviour = ScriptedBehavior(base_config)

    intent = behaviour.decide(world, "alice")

    assert intent.kind == "request"
    assert intent.object_id == fridge_id

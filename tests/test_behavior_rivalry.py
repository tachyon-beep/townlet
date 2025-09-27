from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.policy.behavior import ScriptedBehavior
from townlet.world.grid import AgentSnapshot, WorldState


def _make_world() -> WorldState:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.conflict.rivalry.avoid_threshold = 0.1
    world = WorldState.from_config(config)
    world.register_object(object_id="shower_1", object_type="shower")
    world.register_object(object_id="fridge_1", object_type="fridge")
    world.register_object(object_id="stove_1", object_type="stove")
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.2, "hygiene": 0.2, "energy": 0.2},
        wallet=1.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(0, 1),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    world.register_rivalry_conflict("alice", "bob")
    return world


def test_scripted_behavior_avoids_queue_with_rival() -> None:
    world = _make_world()
    behavior = ScriptedBehavior(world.config)

    # Force Bob into the front of the fridge queue so Alice sees rival.
    world.queue_manager.request_access("fridge_1", "bob", tick=world.tick)
    world.queue_manager.request_access("fridge_1", "alice", tick=world.tick)

    intent = behavior.decide(world, "alice")
    if intent.kind == "request":
        assert intent.object_id != "fridge_1"
    else:
        assert intent.kind != "request"


def test_scripted_behavior_requests_when_no_rival() -> None:
    world = _make_world()
    behavior = ScriptedBehavior(world.config)

    intent = behavior.decide(world, "alice")
    assert intent.kind == "request"
    assert intent.object_id in {"fridge_1", "stove_1"}


def test_behavior_retries_after_rival_leaves() -> None:
    world = _make_world()
    behavior = ScriptedBehavior(world.config)

    world.queue_manager.request_access("fridge_1", "bob", tick=world.tick)
    world.queue_manager.request_access("fridge_1", "alice", tick=world.tick)
    behavior.decide(world, "alice")

    # Bob leaves the queue; Alice should now proceed.
    world.queue_manager.release("fridge_1", "bob", world.tick, success=False)
    behavior.pending.pop("alice", None)
    intent = behavior.decide(world, "alice")
    assert intent.kind == "request"

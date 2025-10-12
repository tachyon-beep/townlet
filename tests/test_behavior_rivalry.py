from pathlib import Path

from townlet.config import load_config
from townlet.policy.behavior import ScriptedBehavior
from townlet.rewards.engine import RewardEngine
from townlet.world.grid import AgentSnapshot, WorldState

from tests.helpers.modular_world import ModularTestWorld


def _make_world() -> ModularTestWorld:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.conflict.rivalry.avoid_threshold = 0.1
    world = ModularTestWorld.from_config(config)
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


def test_scripted_behavior_initiates_chat_when_conditions_met() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    for agent_id in ("alice", "bob"):
        world.agents[agent_id] = AgentSnapshot(
            agent_id=agent_id,
            position=(0, 0),
            needs={"hunger": 0.9, "hygiene": 0.9, "energy": 0.9},
            wallet=1.0,
        )
        world.agents[agent_id].personality.extroversion = 0.8
    world.tick = 100

    behavior = ScriptedBehavior(config)
    intent = behavior.decide(world, "alice")
    assert intent.kind == "chat"
    assert intent.target_agent == "bob"
    assert 0.1 <= intent.quality <= 1.0

    follow_up = behavior.decide(world, "alice")
    assert follow_up.kind != "chat"

    world.record_chat_success("alice", "bob", quality=intent.quality or 1.0)
    engine = RewardEngine(config)
    rewards = engine.compute(world, dict.fromkeys(world.agents, False))
    assert rewards["alice"] > config.rewards.survival_tick


def test_scripted_behavior_avoids_chat_when_relationships_disabled() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.config.features.stages.relationships = "OFF"
    for agent_id in ("alice", "bob"):
        world.agents[agent_id] = AgentSnapshot(
            agent_id=agent_id,
            position=(0, 0),
            needs={"hunger": 0.9, "hygiene": 0.9, "energy": 0.9},
            wallet=1.0,
        )
        world.agents[agent_id].personality.extroversion = 0.9
    world.tick = 50

    behavior = ScriptedBehavior(config)
    intent = behavior.decide(world, "alice")
    assert intent.kind != "chat"


def test_scripted_behavior_moves_when_rival_on_same_tile() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.conflict.rivalry.avoid_threshold = 0.1
    world = WorldState.from_config(config)
    for agent_id in ("alice", "bob"):
        world.agents[agent_id] = AgentSnapshot(
            agent_id=agent_id,
            position=(0, 0),
            needs={"hunger": 0.9, "hygiene": 0.9, "energy": 0.9},
            wallet=1.0,
        )
        world.agents[agent_id].personality.extroversion = 0.0
    world.register_rivalry_conflict("alice", "bob", intensity=1.0)
    world.tick = 10

    behavior = ScriptedBehavior(config)
    intent = behavior.decide(world, "alice")
    assert intent.kind == "move"
    assert intent.position is not None

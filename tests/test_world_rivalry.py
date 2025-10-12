from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.world.grid import AgentSnapshot

from tests.helpers.modular_world import ModularTestWorld


def _make_world() -> ModularTestWorld:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.conflict.rivalry.increment_per_conflict = 0.2
    world = ModularTestWorld.from_config(config)
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(1, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    return world


def test_register_rivalry_conflict_updates_snapshot() -> None:
    world = _make_world()
    world.register_rivalry_conflict("alice", "bob")
    snapshot = world.rivalry_snapshot()
    assert snapshot["alice"]["bob"] == pytest.approx(0.2)
    assert snapshot["bob"]["alice"] == pytest.approx(0.2)

def test_rivalry_events_record_reason() -> None:
    world = _make_world()
    world.tick = 42
    world.register_rivalry_conflict("alice", "bob", intensity=1.5, reason="queue_conflict")
    events = world.consume_rivalry_events()
    assert events
    event = events[0]
    assert event["tick"] == 42
    assert event["agent_a"] == "alice"
    assert event["agent_b"] == "bob"
    assert event["reason"] == "queue_conflict"
    assert event["intensity"] == pytest.approx(1.5)
    # Second call drains the buffer
    assert world.consume_rivalry_events() == []


def test_rivalry_decays_over_time() -> None:
    world = _make_world()
    world.config.conflict.rivalry.decay_per_tick = 0.1
    world.config.conflict.rivalry.eviction_threshold = 0.05
    world.register_rivalry_conflict("alice", "bob")
    initial = world.rivalry_value("alice", "bob")

    world.tick = 1
    world.resolve_affordances(current_tick=world.tick)
    after_decay = world.rivalry_value("alice", "bob")
    assert after_decay < initial

    # Large decay should remove rivalry entirely
    for offset in range(2, 5):
        world.tick = offset
        world.resolve_affordances(current_tick=world.tick)

    snapshot = world.rivalry_snapshot()
    assert "alice" not in snapshot
    assert "bob" not in snapshot


def test_queue_conflict_event_emitted_with_intensity() -> None:
    world = _make_world()
    world.queue_manager._settings.ghost_step_after = 1
    world.register_object(object_id="stove_1", object_type="stove")
    world.tick = 0
    world.apply_actions(
        {
            "alice": {"kind": "request", "object": "stove_1"},
            "bob": {"kind": "request", "object": "stove_1"},
        }
    )
    world.resolve_affordances(current_tick=world.tick)
    world.tick = 1
    result = world.resolve_affordances(current_tick=world.tick)
    events = result.events
    queue_events = [event for event in events if event.get("event") == "queue_conflict"]
    assert queue_events
    conflict = queue_events[0]
    assert conflict["reason"] == "ghost_step"
    assert conflict["intensity"] >= 1.0
    assert {conflict["actor"], conflict["rival"]} == {"alice", "bob"}

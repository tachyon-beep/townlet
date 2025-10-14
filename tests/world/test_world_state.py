from __future__ import annotations

import random
from types import SimpleNamespace

import pytest

from townlet.world.agents.snapshot import AgentSnapshot
from townlet.world.state import WorldState


def make_world(seed: int | None = None) -> WorldState:
    cfg = SimpleNamespace(name="test-config")
    return WorldState(config=cfg, rng_seed=seed)


def make_snapshot(agent_id: str, position: tuple[int, int] = (0, 0)) -> AgentSnapshot:
    return AgentSnapshot(
        agent_id=agent_id,
        position=position,
        needs={"hunger": 0.5, "energy": 0.5, "hygiene": 0.5},
        wallet=1.0,
    )


def test_register_agent_updates_records_and_view() -> None:
    world = make_world()
    alice = make_snapshot("alice", position=(1, 2))

    world.register_agent(alice, tick=5, metadata={"team": "A"})

    view = world.agent_snapshots_view()
    assert "alice" in view
    with pytest.raises(TypeError):
        view["alice"] = alice  # type: ignore[misc]

    record = world.agent_records_view()["alice"]
    assert record.created_tick == 5
    assert record.metadata["team"] == "A"


def test_reset_clears_state_and_reseeds_rng() -> None:
    world = make_world()
    world.register_agent(make_snapshot("bob"))
    world.metadata["foo"] = "bar"
    world.request_ctx_reset("bob")
    world.emit_event("domain.test", {"value": 1})
    world.tick = 42

    world.reset(seed=321)

    assert world.tick == 0
    assert world.metadata == {}
    assert list(world.agent_snapshots_view().keys()) == []
    assert world.consume_ctx_reset_requests() == set()
    assert world.drain_events() == []

    expected_rng = random.Random(321).random()
    assert world.rng.random() == expected_rng


def test_ctx_reset_queue_round_trip() -> None:
    world = make_world()
    world.request_ctx_reset("carol")
    world.request_ctx_reset("dave")
    pending = world.consume_ctx_reset_requests()
    assert pending == {"carol", "dave"}
    assert world.consume_ctx_reset_requests() == set()


def test_emit_event_and_drain_returns_payload() -> None:
    world = make_world()
    world.emit_event("system.tick", {"tick": 1}, tick=1, ts=1.5)
    events = world.drain_events()
    assert events == [
        {"type": "system.tick", "payload": {"tick": 1}, "tick": 1, "ts": 1.5}
    ]
    assert world.drain_events() == []


def test_snapshot_returns_deep_copy() -> None:
    world = make_world()
    alice = make_snapshot("alice")
    world.register_agent(alice)
    snapshot = world.snapshot()

    alice.needs["hunger"] = 0.1

    stored = snapshot["agents"]["alice"]
    assert stored.needs["hunger"] == 0.5
    assert snapshot["tick"] == 0
    assert snapshot["metadata"] == {}

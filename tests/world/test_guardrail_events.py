from __future__ import annotations

from pathlib import Path

from townlet.config import load_config
from townlet.world.grid import AgentSnapshot, WorldState


def make_world() -> WorldState:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    return world


def test_guardrail_chat_failure_request_updates_relationships() -> None:
    world = make_world()
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.2},
        wallet=1.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(0, 0),
        needs={"hunger": 0.2},
        wallet=1.0,
    )

    world.drain_events()
    world.consume_chat_events()

    world.emit_event(
        "policy.guardrail.request",
        {
            "variant": "chat_failure",
            "speaker": "alice",
            "listener": "bob",
        },
    )

    chat_events = world.consume_chat_events()
    assert any(event.get("event") == "chat_failure" for event in chat_events)

    tie = world.relationship_tie("alice", "bob")
    assert tie is not None
    assert getattr(tie, "rivalry", 0.0) >= 0.05

    emitted = world.drain_events()
    assert any(event.get("event") == "chat_failure" for event in emitted)


def test_guardrail_relationship_block_request_records_avoidance() -> None:
    world = make_world()
    world.register_object(object_id="fridge_1", object_type="fridge")
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.2},
        wallet=1.0,
    )

    world.drain_events()
    world.consume_relationship_avoidance_events()

    world.emit_event(
        "policy.guardrail.request",
        {
            "variant": "relationship_block",
            "agent_id": "alice",
            "reason": "queue_rival",
            "object_id": "fridge_1",
        },
    )

    avoidance_events = world.consume_relationship_avoidance_events()
    assert avoidance_events
    assert avoidance_events[0]["reason"] == "queue_rival"

    emitted = world.drain_events()
    assert any(event.get("event") == "policy.guardrail.block" for event in emitted)

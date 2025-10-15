from __future__ import annotations

from types import SimpleNamespace

import pytest

from townlet.world.actions import (
    Action,
    ActionValidationError,
    apply_actions,
    validate_actions,
)
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


def test_validate_actions_normalises_move_payload() -> None:
    action = Action(agent_id="alice", kind="move", payload={"position": [1, 2], "duration": "3"})
    result = validate_actions([action])

    assert result[0].payload["position"] == (1, 2)
    assert result[0].payload["duration"] == 3


def test_validate_actions_rejects_unknown_kind() -> None:
    action = Action(agent_id="alice", kind="dance", payload={})
    with pytest.raises(ActionValidationError):
        validate_actions([action])


def test_apply_actions_updates_snapshot_and_emits_event() -> None:
    world = make_world()
    world.register_agent(make_snapshot("alice"))

    events = apply_actions(
        world,
        [Action(agent_id="alice", kind="move", payload={"position": (3, 4), "duration": 2})],
    )

    snapshot = world.agent_snapshots_view()["alice"]
    assert snapshot.position == (3, 4)
    assert snapshot.last_action_id == "move"
    assert snapshot.last_action_success is True
    assert snapshot.last_action_duration == 2

    assert len(events) == 1
    event = events[0]
    assert event.type == "action.move"
    assert event.payload["position"] == (3, 4)
    assert event.payload["success"] is True
    assert world.drain_events()  # mirror events recorded on state


def test_apply_actions_records_invalid_action_event() -> None:
    world = make_world()
    world.register_agent(make_snapshot("alice"))

    events = apply_actions(
        world,
        [Action(agent_id="alice", kind="move", payload={})],
    )

    assert events[0].type == "action.invalid"
    assert events[0].payload["agent_id"] == "alice"


def test_apply_actions_marks_pending_for_unimplemented_kinds() -> None:
    world = make_world()
    world.register_agent(make_snapshot("alice"))

    events = apply_actions(
        world,
        [
            Action(
                agent_id="alice",
                kind="request",
                payload={"object": "stall_1"},
            )
        ],
    )

    snapshot = world.agent_snapshots_view()["alice"]
    assert snapshot.last_action_success is False

    event = events[0]
    assert event.type == "action.request"
    assert event.payload["pending"] is True

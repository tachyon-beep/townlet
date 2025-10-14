from __future__ import annotations

import pytest

from townlet.world.agents import AgentRegistry
from townlet.world.agents.snapshot import AgentSnapshot


def make_snapshot(agent_id: str, position: tuple[int, int] = (0, 0)) -> AgentSnapshot:
    return AgentSnapshot(
        agent_id=agent_id,
        position=position,
        needs={"hunger": 0.5, "energy": 0.5, "hygiene": 0.5},
        wallet=0.0,
    )


def test_add_registers_snapshot_and_triggers_callback() -> None:
    added: list[str] = []

    def on_add(snapshot: AgentSnapshot) -> None:
        added.append(snapshot.agent_id)

    registry = AgentRegistry(on_add=on_add)
    alice = make_snapshot("alice", position=(1, 2))
    registry.add(alice, tick=3, metadata={"team": "A"})

    assert registry["alice"].position == (1, 2)
    assert added == ["alice"]

    record = registry.record("alice")
    assert record is not None
    assert record.created_tick == 3
    assert record.metadata["team"] == "A"


def test_add_overwrites_existing_snapshot_and_updates_metadata() -> None:
    registry = AgentRegistry()
    original = make_snapshot("bob", position=(0, 0))
    registry.add(original, tick=1, metadata={"team": "A"})

    updated = make_snapshot("bob", position=(5, 6))
    registry.add(updated, tick=7, metadata={"tier": "gold"})

    record = registry.record("bob")
    assert record is not None
    assert record.snapshot.position == (5, 6)
    assert record.created_tick == 1
    assert record.updated_tick == 7
    assert record.metadata == {"team": "A", "tier": "gold"}


def test_discard_removes_snapshot_and_invokes_callback() -> None:
    removed: list[str] = []

    def on_remove(snapshot: AgentSnapshot) -> None:
        removed.append(snapshot.agent_id)

    registry = AgentRegistry(on_remove=on_remove)
    registry.add(make_snapshot("carol"))

    snapshot = registry.discard("carol")
    assert snapshot is not None and snapshot.agent_id == "carol"
    assert "carol" not in registry
    assert removed == ["carol"]


def test_snapshots_view_is_read_only_but_live() -> None:
    registry = AgentRegistry()
    registry.add(make_snapshot("dave"))

    view = registry.snapshots_view()
    assert "dave" in view

    with pytest.raises(TypeError):
        view["dave"] = make_snapshot("other")  # type: ignore[misc]

    registry.add(make_snapshot("erin"))
    assert "erin" in view


def test_values_map_returns_copy() -> None:
    registry = AgentRegistry()
    registry.add(make_snapshot("frank"))

    mapping = registry.values_map()
    mapping.pop("frank")

    assert "frank" in registry
    assert "frank" in registry.snapshots_view()

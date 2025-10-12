from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers.modular_world import ModularTestWorld
from townlet.config import load_config
from townlet.world.grid import AgentSnapshot


def _make_world() -> ModularTestWorld:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = ModularTestWorld.from_config(config)
    world.agents.clear()
    return world


def test_active_reservations_view_blocks_mutation() -> None:
    world = _make_world()
    world.register_object(object_id="bed_1", object_type="bed", position=(0, 0))
    world.queue_manager.request_access("bed_1", "alice", world.tick)
    world.refresh_reservations()

    view = world.active_reservations_view()

    assert view["bed_1"] == "alice"
    with pytest.raises(TypeError):
        view["bed_1"] = "bob"  # type: ignore[misc]

    # Underlying changes propagate to the view.
    world.queue_manager.release("bed_1", "alice", world.tick, success=False)
    world.queue_manager.request_access("bed_1", "bob", world.tick + 1)
    world.refresh_reservations()
    assert view["bed_1"] == "bob"


def test_agent_snapshots_view_is_read_only() -> None:
    world = _make_world()
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5},
        wallet=1.0,
    )

    view = world.agent_snapshots_view()
    assert "alice" in view
    with pytest.raises(TypeError):
        view["alice"] = view["alice"]  # type: ignore[misc]

    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(1, 0),
        needs={"hunger": 0.7},
        wallet=0.5,
    )
    assert "bob" in view


def test_objects_by_position_view_returns_tuples() -> None:
    world = _make_world()
    world.register_object(object_id="bed_1", object_type="bed", position=(0, 0))

    view = world.objects_by_position_view()
    assert view[(0, 0)] == ("bed_1",)
    with pytest.raises(TypeError):
        view[(0, 0)] = ("bed_1",)  # type: ignore[misc]

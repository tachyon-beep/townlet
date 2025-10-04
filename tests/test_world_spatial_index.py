from __future__ import annotations

from pathlib import Path

from townlet.config import load_config
from townlet.world.grid import WorldState


def _make_world() -> WorldState:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.agents.clear()
    return world


def test_agents_move_between_tiles_updates_index() -> None:
    world = _make_world()
    world.respawn_agent({"agent_id": "alice", "position": [0, 0]})

    world.apply_actions({"alice": {"kind": "move", "position": (1, 0)}})

    assert "alice" in world.agents_at_tile((1, 0))
    assert world.agents_at_tile((0, 0)) == ()

    world.kill_agent("alice")
    assert world.agents_at_tile((1, 0)) == ()


def test_reservation_tiles_toggle_with_queue_activity() -> None:
    world = _make_world()
    world.register_object(object_id="bed_1", object_type="bed", position=(0, 1))
    world.respawn_agent({"agent_id": "alice", "position": [0, 0]})

    granted = world.queue_manager.request_access("bed_1", "alice", world.tick)
    assert granted is True
    world.refresh_reservations()
    assert (0, 1) in world.reservation_tiles()

    world.queue_manager.release("bed_1", "alice", world.tick, success=True)
    world.refresh_reservations()
    assert (0, 1) not in world.reservation_tiles()

from __future__ import annotations

from pathlib import Path

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world.grid import AgentSnapshot


def make_loop() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.world.agents.clear()
    return loop


def tile_for_position(tiles, position):
    for row in tiles:
        for tile in row:
            if tuple(tile["position"]) == position:
                return tile
    raise AssertionError(f"Tile not found for position {position}")


def test_local_view_includes_objects_and_agents() -> None:
    loop = make_loop()
    world = loop.world
    world.register_object(object_id="fridge_1", object_type="fridge", position=(1, 0))
    world.register_object(object_id="stove_1", object_type="stove", position=(0, 1))

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5},
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(1, 0),
        needs={"hunger": 0.3},
    )

    world._active_reservations["fridge_1"] = "bob"

    view = world.local_view("alice", radius=1)
    assert view["center"] == (0, 0)
    tile = tile_for_position(view["tiles"], (1, 0))
    assert "bob" in tile["agent_ids"]
    assert "fridge_1" in tile["object_ids"]
    assert tile["reservation_active"] is True

    objects = {entry["object_id"] for entry in view["objects"]}
    assert objects == {"fridge_1", "stove_1"}


def test_agent_context_defaults() -> None:
    loop = make_loop()
    world = loop.world
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.2},
        last_action_id="move",
        last_action_success=True,
        last_action_duration=3,
    )

    context = world.agent_context("alice")
    assert context["needs"]["hunger"] == 0.2
    assert context["last_action_id"] == "move"
    assert context["last_action_success"] is True
    assert context["last_action_duration"] == 3

from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.world.grid import AgentSnapshot, WorldState
from townlet.world.observation import (
    agent_context,
    build_local_cache,
    find_nearest_object_of_type,
    local_view,
)


def _make_world() -> WorldState:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.employment.enforce_job_loop = False
    world = WorldState.from_config(config)
    world.register_object(object_id="shower", object_type="shower", position=(0, 1))
    world.register_object(object_id="fridge_1", object_type="fridge", position=(2, 0))
    world.register_object(object_id="stove_1", object_type="stove", position=(5, 0))
    world.register_object(object_id="bed_1", object_type="bed", position=(0, 2))
    world.agents["alice"] = AgentSnapshot(
        "alice",
        (0, 0),
        {"hunger": 0.4, "hygiene": 0.3, "energy": 0.2},
        wallet=2.0,
    )
    world.agents["bob"] = AgentSnapshot(
        "bob",
        (1, 0),
        {"hunger": 0.6, "hygiene": 0.5, "energy": 0.7},
        wallet=1.5,
    )
    return world


def test_local_view_includes_neighbouring_agents_and_objects() -> None:
    world = _make_world()
    snapshot = local_view(world, "alice", radius=1)

    assert snapshot["center"] == (0, 0)
    assert snapshot["radius"] == 1
    agent_ids = {entry["agent_id"] for entry in snapshot["agents"]}
    assert "bob" in agent_ids
    object_ids = {entry["object_id"] for entry in snapshot["objects"]}
    assert "shower" in object_ids


def test_agent_context_exposes_core_metrics() -> None:
    world = _make_world()
    world._employment_exit_queue.append("alice")  # noqa: SLF001 - legacy structure access
    context = agent_context(world, "alice")

    expected_keys = {
        "needs",
        "wallet",
        "lateness_counter",
        "on_shift",
        "attendance_ratio",
        "wages_withheld",
        "shift_state",
        "last_action_id",
        "last_action_success",
        "last_action_duration",
    }
    assert expected_keys.issubset(context.keys())
    assert context["needs"]["hunger"] == pytest.approx(0.4)


def test_find_nearest_object_of_type_returns_closest_position() -> None:
    world = _make_world()
    pos = find_nearest_object_of_type(world, "stove", (0, 0))
    assert pos == (5, 0)


def test_build_local_cache_matches_world_state() -> None:
    world = _make_world()
    world._active_reservations["bed_1"] = "alice"  # noqa: SLF001 - transitional access
    snapshots = world.snapshot()
    agent_lookup, object_lookup, reservation_tiles = build_local_cache(world, snapshots)

    assert snapshots["alice"].position in agent_lookup
    assert (0, 1) in object_lookup
    assert (0, 2) in reservation_tiles

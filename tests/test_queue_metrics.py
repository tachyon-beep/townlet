from __future__ import annotations

from pathlib import Path

from townlet.config import load_config

from tests.helpers.modular_world import ModularTestWorld


def _make_world() -> ModularTestWorld:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = ModularTestWorld.from_config(config)
    world.agents.clear()
    world.tick = 0
    return world


def test_queue_metrics_capture_ghost_step_and_rotation() -> None:
    world = _make_world()
    world.register_object(object_id="fridge_a", object_type="fridge")
    world.objects["fridge_a"].stock["meals"] = 10
    world.store_stock["fridge_a"] = world.objects["fridge_a"].stock

    for agent_id, position in (("alice", (0, 0)), ("bob", (1, 0))):
        world.lifecycle_service.spawn_agent(
            agent_id,
            position,
            needs={"hunger": 0.6, "hygiene": 0.6, "energy": 0.6},
            wallet=1.0,
        )

    queue = world.queue_manager
    queue._settings.ghost_step_after = 2

    tick = 0
    queue.request_access("fridge_a", "alice", tick)
    queue.request_access("fridge_a", "bob", tick)

    assert queue.record_blocked_attempt("fridge_a") is False
    assert queue.record_blocked_attempt("fridge_a") is True
    queue.requeue_to_tail("fridge_a", "alice", tick)
    metrics = queue.metrics()
    assert metrics["ghost_step_events"] == 1
    assert metrics["rotation_events"] == 1


def test_nightly_reset_preserves_queue_metrics() -> None:
    world = _make_world()
    world.lifecycle_service.spawn_agent(
        "alice",
        (0, 0),
        needs={"hunger": 0.6, "hygiene": 0.6, "energy": 0.6},
        wallet=1.0,
    )
    world.queue_manager._metrics["ghost_step_events"] = 5
    world.apply_nightly_reset()
    metrics = world.queue_manager.metrics()
    assert metrics["ghost_step_events"] == 5

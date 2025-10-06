from __future__ import annotations

from pathlib import Path

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world.grid import AgentSnapshot, WorldState


def make_world() -> tuple[SimulationLoop, WorldState]:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    world = loop.world
    world.agents.clear()
    return loop, world


def request_object(world, object_id: str, agent_id: str) -> None:
    granted = world.queue_manager.request_access(object_id, agent_id, world.tick)
    assert granted is True
    world._sync_reservation(object_id)


def test_affordance_before_after_hooks_fire_once() -> None:
    _loop, world = make_world()
    hook_log: list[tuple[str, str]] = []

    world.register_affordance_hook(
        "on_attempt_sleep",
        lambda ctx: hook_log.append((ctx["stage"], ctx["hook"])),
    )
    world.register_affordance_hook(
        "on_finish_sleep",
        lambda ctx: hook_log.append((ctx["stage"], ctx["hook"])),
    )

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"energy": 0.1},
        wallet=1.0,
    )

    request_object(world, "bed_1", "alice")
    assert world.affordance_runtime.start("alice", "bed_1", "rest_sleep", tick=world.tick)[0]

    running = world.running_affordances_snapshot()["bed_1"]
    assert running.agent_id == "alice"
    assert hook_log == [("before", "on_attempt_sleep")]

    world.affordance_runtime.running_affordances["bed_1"].duration_remaining = 0
    world.resolve_affordances(world.tick)

    assert hook_log == [
        ("before", "on_attempt_sleep"),
        ("after", "on_finish_sleep"),
    ]


def test_affordance_fail_hook_runs_once_per_failure() -> None:
    _loop, world = make_world()
    hook_log: list[tuple[str, str, str | None]] = []

    world.register_affordance_hook(
        "on_attempt_cook",
        lambda ctx: hook_log.append((ctx["stage"], ctx["hook"], None)),
    )
    world.register_affordance_hook(
        "on_cook_fail",
        lambda ctx: hook_log.append(
            (ctx["stage"], ctx["hook"], ctx.get("reason"))
        ),
    )

    world.register_object(object_id="test_stove", object_type="stove", position=(2, 0))

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(2, 0),
        needs={"hunger": 0.2},
        wallet=0.0,
    )

    # First attempt fails because agent cannot afford ingredients.
    request_object(world, "test_stove", "alice")
    assert not world.affordance_runtime.start("alice", "test_stove", "cook_meal", tick=world.tick)[0]
    fail_events = [entry for entry in hook_log if entry[0] == "fail"]
    assert len(fail_events) == 1
    assert fail_events[0] == ("fail", "on_cook_fail", "insufficient_funds")

    # Duplicate release should not trigger another fail hook.
    world.queue_manager.release("test_stove", "alice", world.tick, success=False)
    fail_events = [entry for entry in hook_log if entry[0] == "fail"]
    assert len(fail_events) == 1

    # Second attempt in the same tick should emit a new fail hook.
    request_object(world, "test_stove", "alice")
    assert not world.affordance_runtime.start("alice", "test_stove", "cook_meal", tick=world.tick)[0]
    fail_events = [entry for entry in hook_log if entry[0] == "fail"]
    assert len(fail_events) == 2
    assert fail_events[1] == ("fail", "on_cook_fail", "insufficient_funds")


def test_shower_requires_power() -> None:
    _loop, world = make_world()
    shower = world.objects["shower_1"]
    shower.stock["power_on"] = 0
    world.store_stock["shower_1"] = shower.stock

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(1, 1),
        needs={"hygiene": 0.1},
        wallet=5.0,
    )

    request_object(world, "shower_1", "alice")
    assert world._start_affordance("alice", "shower_1", "use_shower") is False

    events = world.drain_events()
    precondition_event = next(
        e for e in events if e["event"] == "affordance_precondition_fail"
    )
    assert precondition_event["condition"] == "power_on == true"
    fail_event = next(e for e in events if e["event"] == "affordance_fail")
    assert fail_event["reason"] == "precondition_failed"
    assert any(e["event"] == "shower_power_outage" for e in events)
    assert world.queue_manager.active_agent("shower_1") is None


def test_shower_completion_emits_event() -> None:
    _loop, world = make_world()
    shower = world.objects["shower_1"]
    shower.stock["power_on"] = 1
    world.store_stock["shower_1"] = shower.stock

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(1, 1),
        needs={"hygiene": 0.1},
        wallet=5.0,
    )

    request_object(world, "shower_1", "alice")
    assert world._start_affordance("alice", "shower_1", "use_shower") is True
    running = world.affordance_runtime.running_affordances["shower_1"]
    running.duration_remaining = 0
    world.resolve_affordances(world.tick)

    events = world.drain_events()
    assert any(e["event"] == "shower_complete" for e in events)
    assert world.agents["alice"].inventory.get("showers_taken", 0) == 1


def test_sleep_slots_cycle_and_completion_event() -> None:
    _loop, world = make_world()
    bed = world.objects["bed_1"]
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"energy": 0.1},
        wallet=1.0,
    )

    request_object(world, "bed_1", "alice")
    assert world._start_affordance("alice", "bed_1", "rest_sleep") is True
    assert bed.stock["sleep_slots"] == bed.stock["sleep_capacity"] - 1

    running = world.affordance_runtime.running_affordances["bed_1"]
    running.duration_remaining = 0
    world.resolve_affordances(world.tick)

    assert bed.stock["sleep_slots"] == bed.stock["sleep_capacity"]
    events = world.drain_events()
    assert any(e["event"] == "sleep_complete" for e in events)
    assert world.agents["alice"].inventory.get("sleep_sessions", 0) == 1


def test_sleep_attempt_fails_when_no_slots() -> None:
    _loop, world = make_world()
    bed = world.objects["bed_1"]
    bed.stock["sleep_slots"] = 0
    bed.stock.setdefault("sleep_capacity", 0)
    world.store_stock["bed_1"] = bed.stock

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"energy": 0.1},
        wallet=1.0,
    )

    request_object(world, "bed_1", "alice")
    assert world._start_affordance("alice", "bed_1", "rest_sleep") is False
    events = world.drain_events()
    fail_event = next(e for e in events if e["event"] == "affordance_fail")
    assert fail_event["reason"] == "bed_unavailable"


def test_runtime_running_snapshot_and_remove_agent() -> None:
    _loop, world = make_world()
    bed = world.objects["bed_1"]

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"energy": 0.1},
        wallet=1.0,
    )

    request_object(world, "bed_1", "alice")
    start_ok, _meta = world.affordance_runtime.start("alice", "bed_1", "rest_sleep", tick=world.tick)
    assert start_ok is True

    snapshot = world.running_affordances_snapshot()
    assert "bed_1" in snapshot
    entry = snapshot["bed_1"]
    assert entry.agent_id == "alice"
    assert entry.object_id == "bed_1"
    assert entry.affordance_id == "rest_sleep"
    assert entry.duration_remaining > 0
    assert entry.effects == {"energy": 0.8}

    world.remove_agent("alice", world.tick)
    assert world.running_affordances_snapshot() == {}
    assert bed.occupied_by is None


def test_affordance_outcome_log_is_capped() -> None:
    _loop, world = make_world()
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"energy": 0.5},
        wallet=1.0,
    )

    # ensure log fills beyond the cap
    for index in range(15):
        world.queue_manager.request_access("bed_1", "alice", world.tick)
        world._sync_reservation("bed_1")
        world.apply_actions(
            {
                "alice": {
                    "kind": "start",
                    "object": "bed_1",
                    "affordance": "rest_sleep",
                }
            }
        )
        world.apply_actions(
            {
                "alice": {
                    "kind": "release",
                    "object": "bed_1",
                    "success": False,
                    "reason": f"test_{index}",
                }
            }
        )
    log = world.agents["alice"].inventory.get("_affordance_outcomes", [])
    assert 0 < len(log) <= 10

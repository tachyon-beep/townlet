from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.console.handlers import ConsoleCommand, create_console_router
from townlet.core.sim_loop import SimulationLoop
from townlet.world.grid import AgentSnapshot
from townlet.world.preconditions import (
    PreconditionSyntaxError,
    compile_preconditions,
    evaluate_preconditions,
)


def _make_loop() -> tuple[SimulationLoop, object]:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.world.agents.clear()
    return loop, config


def _request_object(world, object_id: str, agent_id: str) -> None:
    granted = world.queue_manager.request_access(object_id, agent_id, world.tick)
    assert granted is True
    world._sync_reservation(object_id)  


def test_compile_preconditions_normalises_booleans() -> None:
    compiled = compile_preconditions(["power_on == true", "occupied == FALSE"])
    ok, failed = evaluate_preconditions(compiled, {"power_on": True, "occupied": False})
    assert ok is True
    assert failed is None


def test_compile_preconditions_rejects_function_calls() -> None:
    with pytest.raises(PreconditionSyntaxError):
        compile_preconditions(["unsafe()"])


def test_evaluate_preconditions_supports_nested_attributes() -> None:
    compiled = compile_preconditions(["agent.needs.hunger < 0.6", "wallet >= 0.1"])
    context = {"agent": {"needs": {"hunger": 0.4}}, "wallet": 0.5}
    ok, failed = evaluate_preconditions(compiled, context)
    assert ok is True
    assert failed is None


def test_precondition_failure_blocks_affordance_and_emits_event() -> None:
    loop, config = _make_loop()
    world = loop.world
    router = create_console_router(
        loop.telemetry,
        world,
        loop.perturbations,
        policy=loop.policy,
        config=config,
    )

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(1, 1),
        needs={"hygiene": 0.2, "hunger": 0.5, "energy": 0.5},
        wallet=5.0,
    )

    shower = world.objects["shower_1"]
    shower.stock["power_on"] = 0
    world.store_stock["shower_1"] = shower.stock

    _request_object(world, "shower_1", "alice")
    success = world._start_affordance("alice", "shower_1", "use_shower")
    assert success is False

    events = world.drain_events()
    fail_event = next(event for event in events if event["event"] == "affordance_precondition_fail")
    assert fail_event["condition"] == "power_on == true"
    assert fail_event["context"]["power_on"] is False
    assert fail_event["context"]["occupied"] is False

    failures = [event for event in events if event.get("event") == "affordance_precondition_fail"]

    loop.telemetry.emit_event(
        "loop.tick",
        {
            "tick": world.tick,
            "world": world,
            "rewards": {},
            "events": events,
            "policy_snapshot": {},
            "kpi_history": False,
            "reward_breakdown": {},
            "stability_inputs": {},
            "perturbations": {},
            "policy_identity": {},
            "possessed_agents": [],
            "social_events": [],
            "global_context": {
                "queue_metrics": {},
                "reward_breakdown": {},
                "perturbations": {},
            },
            "precondition_failures": failures,
        },
    )
    failures = loop.telemetry.latest_precondition_failures()
    assert len(failures) >= 1
    assert all(entry["agent_id"] == "alice" for entry in failures)

    snapshot = router.dispatch(ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={}))
    assert "precondition_failures" in snapshot
    assert snapshot["precondition_failures"][0]["condition"] == "power_on == true"
    assert snapshot["precondition_failures"][0]["object_id"] == "shower_1"


def test_precondition_success_allows_affordance_start() -> None:
    loop, _config = _make_loop()
    world = loop.world

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(1, 1),
        needs={"hygiene": 0.2, "hunger": 0.5, "energy": 0.5},
        wallet=5.0,
    )

    _request_object(world, "shower_1", "alice")
    shower = world.objects["shower_1"]
    shower.stock["power_on"] = 1
    world.store_stock["shower_1"] = shower.stock

    success = world._start_affordance("alice", "shower_1", "use_shower")
    assert success is True
    running = world.affordance_runtime.running_affordances["shower_1"]
    assert running.affordance_id == "use_shower"

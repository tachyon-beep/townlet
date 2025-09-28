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


def test_shower_events_in_telemetry() -> None:
    loop = make_loop()
    world = loop.world
    telemetry = loop.telemetry

    shower = world.objects["shower_1"]
    shower.stock["power_on"] = 0
    world.store_stock["shower_1"] = shower.stock

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(1, 1),
        needs={"hygiene": 0.1},
        wallet=5.0,
    )

    loop.tick = 0
    telemetry.publish_tick(
        tick=loop.tick,
        world=world,
        observations={},
        rewards={},
        events=[],
        policy_snapshot={},
        kpi_history=False,
        reward_breakdown={},
        stability_inputs={},
        perturbations={},
        policy_identity={},
        possessed_agents=[],
    )
    world.apply_console([])
    world.consume_console_results()

    granted = world.queue_manager.request_access("shower_1", "alice", world.tick)
    assert granted is True
    world._sync_reservation("shower_1")
    assert world._start_affordance("alice", "shower_1", "use_shower") is False

    events = world.drain_events()
    telemetry.record_console_results([])
    telemetry.publish_tick(
        tick=loop.tick + 1,
        world=world,
        observations={},
        rewards={},
        events=events,
        policy_snapshot={},
        kpi_history=False,
        reward_breakdown={},
        stability_inputs={},
        perturbations={},
        policy_identity={},
        possessed_agents=[],
    )
    published = telemetry.export_state()
    recorded_events = published["events"]
    assert any(e.get("event") == "shower_power_outage" for e in recorded_events)
    assert any(e.get("event") == "affordance_fail" for e in recorded_events)
    narrations = telemetry.latest_narrations()
    assert any(n["category"] == "utility_outage" for n in narrations)


def test_shower_complete_narration() -> None:
    loop = make_loop()
    world = loop.world
    telemetry = loop.telemetry

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(1, 1),
        needs={"hygiene": 0.1},
        wallet=5.0,
    )

    telemetry.publish_tick(
        tick=loop.tick,
        world=world,
        observations={},
        rewards={},
        events=[],
        policy_snapshot={},
        kpi_history=False,
        reward_breakdown={},
        stability_inputs={},
        perturbations={},
        policy_identity={},
        possessed_agents=[],
    )
    world.apply_console([])
    world.consume_console_results()

    request = world.queue_manager.request_access("shower_1", "alice", world.tick)
    assert request is True
    world._sync_reservation("shower_1")
    assert world._start_affordance("alice", "shower_1", "use_shower") is True
    running = world._running_affordances["shower_1"]
    running.duration_remaining = 0
    world.resolve_affordances(world.tick)
    events = world.drain_events()

    telemetry.publish_tick(
        tick=loop.tick + 1,
        world=world,
        observations={},
        rewards={},
        events=events,
        policy_snapshot={},
        kpi_history=False,
        reward_breakdown={},
        stability_inputs={},
        perturbations={},
        policy_identity={},
        possessed_agents=[],
    )
    published = telemetry.export_state()
    recorded_events = published["events"]
    assert any(e.get("event") == "shower_complete" for e in recorded_events)
    narrations = telemetry.latest_narrations()
    assert any(n["category"] == "shower_complete" for n in narrations)


def test_sleep_events_in_telemetry() -> None:
    loop = make_loop()
    world = loop.world
    telemetry = loop.telemetry

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"energy": 0.1},
        wallet=1.0,
    )

    loop.tick = 0
    telemetry.publish_tick(
        tick=loop.tick,
        world=world,
        observations={},
        rewards={},
        events=[],
        policy_snapshot={},
        kpi_history=False,
        reward_breakdown={},
        stability_inputs={},
        perturbations={},
        policy_identity={},
        possessed_agents=[],
    )
    world.apply_console([])
    world.consume_console_results()

    granted = world.queue_manager.request_access("bed_1", "alice", world.tick)
    assert granted is True
    world._sync_reservation("bed_1")
    assert world._start_affordance("alice", "bed_1", "rest_sleep") is True
    running = world._running_affordances["bed_1"]
    running.duration_remaining = 0
    events = []
    world.resolve_affordances(world.tick)
    events.extend(world.drain_events())

    telemetry.record_console_results([])
    telemetry.publish_tick(
        tick=loop.tick + 1,
        world=world,
        observations={},
        rewards={},
        events=events,
        policy_snapshot={},
        kpi_history=False,
        reward_breakdown={},
        stability_inputs={},
        perturbations={},
        policy_identity={},
        possessed_agents=[],
    )
    published = telemetry.export_state()
    recorded_events = published["events"]
    assert any(e.get("event") == "sleep_complete" for e in recorded_events)
    narrations = telemetry.latest_narrations()
    assert any(n["category"] == "sleep_complete" for n in narrations)

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
    runtime = published["affordance_runtime"]
    assert runtime["event_counts"]["fail"] >= 1
    assert runtime["event_counts"]["precondition_fail"] >= 1
    assert runtime["running_count"] == 0


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
    running = world.affordance_runtime.running_affordances["shower_1"]
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
    runtime = published["affordance_runtime"]
    assert runtime["event_counts"]["finish"] >= 1


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
    running = world.affordance_runtime.running_affordances["bed_1"]
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
    runtime = published["affordance_runtime"]
    assert runtime["event_counts"]["finish"] >= 1


def test_relationship_summary_and_social_events() -> None:
    loop = make_loop()
    world = loop.world
    telemetry = loop.telemetry

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 1.0, "hygiene": 1.0, "energy": 1.0},
        wallet=1.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(0, 0),
        needs={"hunger": 1.0, "hygiene": 1.0, "energy": 1.0},
        wallet=1.0,
    )
    world.update_relationship("alice", "bob", trust=0.4, familiarity=0.2)
    world.record_chat_success("alice", "bob", quality=0.9)
    world.record_relationship_guard_block(
        agent_id="alice", reason="queue_rival", object_id="stove_1"
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
        social_events=[
            {"type": "chat_success", "speaker": "alice", "listener": "bob", "quality": 0.9},
            {"type": "rivalry_avoidance", "agent": "alice", "object": "stove_1", "reason": "queue_rival"},
        ],
    )

    exported = telemetry.export_state()
    social_events = exported.get("social_events")
    assert social_events and any(e.get("type") == "chat_success" for e in social_events)
    summary = exported.get("relationship_summary")
    assert summary is not None
    assert "alice" in summary
    alice_summary = summary["alice"]
    assert alice_summary["top_friends"]


def test_affordance_runtime_running_snapshot() -> None:
    loop = make_loop()
    world = loop.world
    telemetry = loop.telemetry

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"energy": 0.2},
        wallet=1.0,
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

    granted = world.queue_manager.request_access("bed_1", "alice", world.tick)
    assert granted is True
    world._sync_reservation("bed_1")
    started = world._start_affordance("alice", "bed_1", "rest_sleep")
    assert started is True
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
    runtime = telemetry.export_state()["affordance_runtime"]
    assert runtime["running_count"] == 1
    assert "bed_1" in runtime["running"]
    assert runtime["running"]["bed_1"]["agent_id"] == "alice"

def test_rivalry_events_surface_in_telemetry() -> None:
    loop = make_loop()
    world = loop.world
    telemetry = loop.telemetry

    for agent_id, position in (("alice", (0, 0)), ("bob", (1, 0))):
        snapshot = AgentSnapshot(
            agent_id=agent_id,
            position=position,
            needs={"hunger": 0.6, "hygiene": 0.6, "energy": 0.6},
            wallet=1.0,
        )
        world.agents[agent_id] = snapshot
        world._assign_job_if_missing(snapshot)
        world._sync_agent_spawn(snapshot)

    world.register_rivalry_conflict("alice", "bob", intensity=1.5, reason="queue_conflict")
    events = world.drain_events()
    telemetry.publish_tick(
        tick=loop.tick,
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
    snapshot = telemetry.export_state()
    conflict = snapshot.get("conflict_snapshot", {})
    rivalry_events = conflict.get("rivalry_events", [])
    assert rivalry_events
    assert any(event.get("reason") == "queue_conflict" for event in rivalry_events)

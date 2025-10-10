from pathlib import Path

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world.grid import AgentSnapshot


def test_conflict_snapshot_reports_rivalry_counts() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.conflict.rivalry.avoid_threshold = 0.1
    loop = SimulationLoop(config)
    world = loop.world
    world.queue_manager._settings.ghost_step_after = 1

    world.register_object(object_id="stove_1", object_type="stove")
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(1, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )

    world.tick = 0
    world.apply_actions(
        {
            "alice": {"kind": "request", "object": "stove_1"},
            "bob": {"kind": "request", "object": "stove_1"},
        }
    )
    world.resolve_affordances(current_tick=world.tick)

    world.tick = 1
    world.resolve_affordances(current_tick=world.tick)
    events = list(world.drain_events())
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
        },
    )
    loop.telemetry._ingest_loop_tick(  # type: ignore[attr-defined]
        tick=world.tick,
        world=world,
        rewards={},
        events=events,
        policy_snapshot={},
        kpi_history=False,
        reward_breakdown={},
        stability_inputs={},
        perturbations={},
        policy_identity={},
        possessed_agents=[],
        social_events=[],
        runtime_variant="facade",
    )

    conflict_snapshot = loop.telemetry.latest_conflict_snapshot()
    assert conflict_snapshot["queues"]["cooldown_events"] >= 0
    rivalry = conflict_snapshot["rivalry"]
    queue_history = conflict_snapshot['queue_history']
    assert queue_history
    entry = queue_history[-1]
    assert {'tick', 'delta', 'totals'} <= entry.keys()
    latest_alerts = loop.telemetry.latest_stability_alerts()
    assert isinstance(latest_alerts, list)
    assert rivalry["alice"]["bob"] > 0
    assert rivalry["bob"]["alice"] > 0

    telemetry_events = list(loop.telemetry.latest_events())
    queue_events = [
        event for event in telemetry_events if event.get("event") == "queue_conflict"
    ]
    assert queue_events
    payload = queue_events[0]
    assert payload["reason"] == "ghost_step"
    assert payload["intensity"] >= 1.0


def test_replay_sample_matches_schema(tmp_path: Path) -> None:
    sample = Path("docs/samples/observation_hybrid_sample.npz")
    meta = Path("docs/samples/observation_hybrid_metadata.json")
    telemetry = Path("docs/samples/telemetry_conflict_snapshot.json")
    assert sample.exists()
    assert meta.exists()
    assert telemetry.exists()


def test_conflict_export_import_preserves_history() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.conflict.rivalry.avoid_threshold = 0.1
    loop = SimulationLoop(config)
    world = loop.world
    world.queue_manager._settings.ghost_step_after = 1
    world.register_object(object_id="stove_1", object_type="stove")
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(1, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    for tick in range(3):
        world.tick = tick
        world.apply_actions(
            {
                "alice": {"kind": "request", "object": "stove_1"},
                "bob": {"kind": "request", "object": "stove_1"},
            }
        )
        world.resolve_affordances(current_tick=world.tick)
        loop.telemetry.emit_event(
            "loop.tick",
            {
                "tick": world.tick,
                "world": world,
                "rewards": {},
                "events": list(world.drain_events()),
                "policy_snapshot": {},
                "kpi_history": False,
                "reward_breakdown": {},
                "stability_inputs": {},
                "perturbations": {},
                "policy_identity": {},
                "possessed_agents": [],
                "social_events": [],
            },
        )
    loop.telemetry._ingest_loop_tick(  # type: ignore[attr-defined]
        tick=world.tick,
        world=world,
        rewards={},
        events=[],
        policy_snapshot={},
        kpi_history=False,
        reward_breakdown={},
        stability_inputs={},
        perturbations={},
        policy_identity={},
        possessed_agents=[],
        social_events=[],
        runtime_variant="facade",
    )
    exported = loop.telemetry.export_state()
    from townlet.telemetry.publisher import TelemetryPublisher

    restored = TelemetryPublisher(config)
    restored.import_state(exported)
    snapshot = restored.latest_conflict_snapshot()
    assert snapshot["queues"]["ghost_step_events"] >= 1
    assert restored.latest_stability_alerts() == loop.telemetry.latest_stability_alerts()
    assert len(snapshot.get("queue_history", [])) == len(exported["queue_history"])

from pathlib import Path

from tests.helpers.telemetry import build_global_context
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
    relationships = world.context.relationships
    relationships.apply_rivalry_conflict("alice", "bob", intensity=1.0)
    events.append(
        {
            "event": "queue_conflict",
            "tick": world.tick,
            "agent_a": "alice",
            "agent_b": "bob",
            "intensity": 1.0,
            "reason": "ghost_step",
        }
    )
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
            "global_context": build_global_context(
                queue_metrics=world.context.export_queue_metrics(),
                queues=world.context.export_queue_state(),
                relationship_snapshot={
                    "alice": {"bob": {"trust": 0.0, "familiarity": 0.0, "rivalry": 1.0}},
                    "bob": {"alice": {"trust": 0.0, "familiarity": 0.0, "rivalry": 1.0}},
                },
                relationship_metrics={
                    "total": 2,
                    "owners": {"alice": 1, "bob": 1},
                    "reasons": {"ghost_step": 1},
                    "history": [],
                },
                employment_snapshot=world.context.export_employment_snapshot(),
                job_snapshot=world.context.export_job_snapshot(),
                economy_snapshot=world.context.export_economy_snapshot(),
                queue_affinity_metrics=world.context.export_queue_affinity_metrics(),
            ),
        },
    )

    conflict_snapshot = loop.telemetry.latest_conflict_snapshot()
    assert conflict_snapshot["queues"]["cooldown_events"] >= 0
    rivalry = conflict_snapshot["rivalry"]
    queue_history = conflict_snapshot["queue_history"]
    assert queue_history
    entry = queue_history[-1]
    assert {"tick", "delta", "totals"} <= entry.keys()
    latest_alerts = loop.telemetry.latest_stability_alerts()
    assert isinstance(latest_alerts, list)
    assert rivalry["alice"]["bob"]["rivalry"] > 0
    assert rivalry["bob"]["alice"]["rivalry"] > 0

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
        events = list(world.drain_events())
        relationships = world.context.relationships
        relationships.apply_rivalry_conflict("alice", "bob", intensity=0.5 + 0.2 * tick)
        events.append(
            {
                "event": "queue_conflict",
                "tick": world.tick,
                "agent_a": "alice",
                "agent_b": "bob",
                "intensity": 1.0,
                "reason": "ghost_step",
            }
        )
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
            "global_context": build_global_context(
                queue_metrics=world.context.export_queue_metrics(),
                queues=world.context.export_queue_state(),
                relationship_snapshot={
                    "alice": {"bob": {"trust": 0.0, "familiarity": 0.0, "rivalry": 0.5 + 0.2 * tick}},
                    "bob": {"alice": {"trust": 0.0, "familiarity": 0.0, "rivalry": 0.5 + 0.2 * tick}},
                },
                relationship_metrics={
                    "total": 2,
                    "owners": {"alice": 1, "bob": 1},
                    "reasons": {"ghost_step": tick + 1},
                    "history": [],
                },
            ),
        },
    )
    exported = loop.telemetry.export_state()
    from townlet.telemetry.publisher import TelemetryPublisher

    restored = TelemetryPublisher(config)
    restored.import_state(exported)
    snapshot = restored.latest_conflict_snapshot()
    assert snapshot["rivalry"]["alice"]["bob"]["rivalry"] > 0
    assert restored.latest_stability_alerts() == loop.telemetry.latest_stability_alerts()
    restored_history = snapshot.get("queue_history", [])
    assert restored_history
    assert restored_history[-1]["tick"] == exported["queue_history"][-1]["tick"]

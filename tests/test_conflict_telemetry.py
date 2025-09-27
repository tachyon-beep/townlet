from pathlib import Path

import pytest

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
    loop.telemetry.publish_tick(
        tick=world.tick,
        world=world,
        observations={},
        rewards={},
        events=events,
    )

    conflict_snapshot = loop.telemetry.latest_conflict_snapshot()
    assert conflict_snapshot["queues"]["cooldown_events"] >= 0
    rivalry = conflict_snapshot["rivalry"]
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

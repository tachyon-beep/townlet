from __future__ import annotations

import json
from pathlib import Path
import base64
import pickle
import random

import pytest

from townlet.config import SimulationConfig, load_config
from townlet.snapshots.state import (
    SNAPSHOT_SCHEMA_VERSION,
    SnapshotManager,
    SnapshotState,
    apply_snapshot_to_world,
    snapshot_from_world,
)
from townlet.world.grid import AgentSnapshot, WorldState
from townlet.telemetry.publisher import TelemetryPublisher


@pytest.fixture(scope="module")
def sample_config() -> SimulationConfig:
    config_path = Path("configs/examples/poc_hybrid.yaml")
    if not config_path.exists():
        pytest.skip("example config not found")
    return load_config(config_path)


def test_snapshot_round_trip(tmp_path: Path, sample_config) -> None:
    random.seed(42)
    manager = SnapshotManager(root=tmp_path)
    state = SnapshotState(
        config_id=sample_config.config_id,
        tick=42,
        agents={
            "alice": {
                "position": [0, 0],
                "needs": {"hunger": 0.5},
                "wallet": 1.0,
                "personality": {
                    "extroversion": 0.1,
                    "forgiveness": 0.2,
                    "ambition": 0.3,
                },
                "inventory": {"meals_cooked": 1},
                "job_id": "grocer",
                "on_shift": True,
                "lateness_counter": 2,
                "last_late_tick": 10,
                "shift_state": "on_time",
                "late_ticks_today": 1,
                "attendance_ratio": 0.8,
                "absent_shifts_7d": 0,
                "wages_withheld": 0.0,
                "exit_pending": False,
            }
        },
        objects={
            "fridge_1": {
                "object_type": "fridge",
                "occupied_by": None,
                "stock": {"meals": 3},
            }
        },
        queues={
            "active": {"fridge_1": "alice"},
            "queues": {
                "fridge_1": [
                    {"agent_id": "alice", "joined_tick": 5},
                    {"agent_id": "bob", "joined_tick": 6},
                ]
            },
            "cooldowns": [
                {"object_id": "fridge_1", "agent_id": "alice", "expiry": 50}
            ],
            "stall_counts": {"fridge_1": 1},
        },
        embeddings={
            "assignments": {"alice": 0},
            "available": [1, 2],
            "slot_state": {"0": 10, "1": None, "2": None},
            "metrics": {"allocations_total": 1.0, "forced_reuse_count": 0.0},
        },
        employment={
            "exit_queue": ["alice"],
            "queue_timestamps": {"alice": 40},
            "manual_exits": ["bob"],
            "exits_today": 1,
        },
        lifecycle={
            "exits_today": 2,
            "employment_day": 3,
        },
        rng_state=base64.b64encode(pickle.dumps(random.getstate())).decode("ascii"),
        relationships={
            "alice": {
                "bob": {"trust": 0.5, "familiarity": 0.2, "rivalry": 0.0},
                "carol": {"trust": -0.2, "familiarity": 0.0, "rivalry": 0.3},
            },
            "bob": {
                "alice": {"trust": 0.4, "familiarity": 0.1, "rivalry": 0.0},
            },
        },
    )
    path = manager.save(state)
    loaded = manager.load(path, sample_config)
    assert loaded == state


def test_snapshot_config_mismatch_raises(tmp_path: Path, sample_config) -> None:
    manager = SnapshotManager(root=tmp_path)
    state = SnapshotState(config_id="other-config", tick=3)
    path = manager.save(state)
    with pytest.raises(ValueError):
        manager.load(path, sample_config)


def test_snapshot_missing_relationships_field_rejected(tmp_path: Path, sample_config) -> None:
    manager = SnapshotManager(root=tmp_path)
    path = tmp_path / "snapshot-1.json"
    payload = {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "state": {"config_id": sample_config.config_id, "tick": 1},
    }
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        manager.load(path, sample_config)


def test_snapshot_schema_version_mismatch(tmp_path: Path, sample_config) -> None:
    manager = SnapshotManager(root=tmp_path)
    state = SnapshotState(config_id=sample_config.config_id, tick=1)
    path = manager.save(state)
    data = json.loads(path.read_text())
    data["schema_version"] = "0.9"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        manager.load(path, sample_config)


def test_world_relationship_snapshot_round_trip(tmp_path: Path, sample_config: SimulationConfig) -> None:
    random.seed(1337)
    world = WorldState.from_config(sample_config)
    world.tick = 77
    world.update_relationship("alice", "bob", trust=0.4, familiarity=0.2)
    world.update_relationship("alice", "carol", rivalry=0.3)

    world.register_object("fridge_1", "fridge")
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.4, "energy": 0.6},
        wallet=1.5,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(1, 0),
        needs={"hunger": 0.6, "energy": 0.4},
        wallet=0.5,
    )

    # Seed queue state to ensure persistence covers active reservations.
    world.queue_manager.request_access("fridge_1", "alice", world.tick)
    world.queue_manager.request_access("fridge_1", "bob", world.tick)
    world.queue_manager.release("fridge_1", "alice", world.tick, success=True)
    world._employment_exit_queue = ["alice"]
    world._employment_exit_queue_timestamps = {"alice": world.tick}
    world._employment_manual_exits = {"bob"}
    world._employment_exits_today = 1

    telemetry = TelemetryPublisher(sample_config)
    telemetry._latest_queue_metrics = {"cooldown_events": 2}
    telemetry._latest_embedding_metrics = {"forced_reuse_rate": 0.1}
    telemetry._latest_conflict_snapshot = {
        "queues": {"cooldown_events": 2, "ghost_step_events": 1},
        "rivalry": {"alice": {"bob": 0.5}},
    }
    telemetry._latest_relationship_metrics = {"total": 3}
    telemetry._latest_job_snapshot = {"alice": {"job_id": "grocer"}}
    telemetry._latest_economy_snapshot = {"fridge_1": {"stock": {"meals": 3}}}
    telemetry._latest_employment_metrics = {"pending": ["alice"]}
    telemetry._latest_events = [{"event": "test"}]
    telemetry.queue_console_command({"cmd": "foo"})

    state = snapshot_from_world(sample_config, world, telemetry=telemetry)
    baseline_rng_state = random.getstate()

    manager = SnapshotManager(root=tmp_path)
    saved_path = manager.save(state)
    loaded = manager.load(saved_path, sample_config)

    restored_world = WorldState.from_config(sample_config)
    apply_snapshot_to_world(restored_world, loaded)
    restored_telemetry = TelemetryPublisher(sample_config)
    from townlet.snapshots.state import apply_snapshot_to_telemetry

    apply_snapshot_to_telemetry(restored_telemetry, loaded)

    assert restored_world.tick == world.tick
    assert restored_world.relationships_snapshot() == world.relationships_snapshot()
    assert set(restored_world.agents.keys()) == set(world.agents.keys())
    assert restored_world.agents["alice"].needs == world.agents["alice"].needs
    assert restored_world.objects.keys() == world.objects.keys()
    assert restored_world.queue_manager.export_state() == world.queue_manager.export_state()
    assert restored_world._employment_exit_queue == world._employment_exit_queue
    assert restored_world._employment_manual_exits == world._employment_manual_exits
    assert restored_world._employment_exits_today == world._employment_exits_today
    assert random.getstate() == baseline_rng_state
    assert restored_telemetry.export_state() == telemetry.export_state()
    assert restored_telemetry.export_console_buffer() == telemetry.export_console_buffer()

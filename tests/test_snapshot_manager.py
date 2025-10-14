from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from townlet.config import PerturbationKind, SimulationConfig, load_config
from townlet.scheduler.perturbations import PerturbationScheduler, ScheduledPerturbation
from townlet.dto.world import (
    AgentSummary,
    EmploymentSnapshot,
    IdentitySnapshot,
    LifecycleSnapshot,
    MigrationSnapshot,
    QueueSnapshot,
    SimulationSnapshot,
)
from townlet.snapshots.state import (
    SNAPSHOT_SCHEMA_VERSION,
    SnapshotManager,
    apply_snapshot_to_world,
    snapshot_from_world,
)
from townlet.telemetry.publisher import TelemetryPublisher
from townlet.utils import encode_rng_state
from townlet.world.grid import AgentSnapshot, WorldState


@pytest.fixture(scope="module")
def sample_config() -> SimulationConfig:
    config_path = Path("configs/examples/poc_hybrid.yaml")
    if not config_path.exists():
        pytest.skip("example config not found")
    return load_config(config_path)


def test_snapshot_round_trip(tmp_path: Path, sample_config) -> None:
    random.seed(42)
    manager = SnapshotManager(root=tmp_path)
    world_rng_encoded = encode_rng_state(random.getstate())

    # Build SimulationSnapshot with nested DTOs
    state = SimulationSnapshot(
        config_id=sample_config.config_id,
        tick=42,
        agents={
            "alice": AgentSummary(
                agent_id="alice",
                position=(0, 0),
                needs={"hunger": 0.5},
                wallet=1.0,
                personality={
                    "extroversion": 0.1,
                    "forgiveness": 0.2,
                    "ambition": 0.3,
                },
                inventory={"meals_cooked": 1},
                job_id="grocer",
                on_shift=True,
                lateness_counter=2,
                last_late_tick=10,
                shift_state="on_time",
                late_ticks_today=1,
                attendance_ratio=0.8,
                absent_shifts_7d=0,
                wages_withheld=0.0,
                exit_pending=False,
            )
        },
        objects={
            "fridge_1": {
                "object_type": "fridge",
                "occupied_by": None,
                "stock": {"meals": 3},
            }
        },
        queues=QueueSnapshot(
            active={"fridge_1": "alice"},
            queues={
                "fridge_1": [
                    {"agent_id": "alice", "joined_tick": 5},
                    {"agent_id": "bob", "joined_tick": 6},
                ]
            },
            cooldowns=[{"object_id": "fridge_1", "agent_id": "alice", "expiry": 50}],
            stall_counts={"fridge_1": 1},
        ),
        employment=EmploymentSnapshot(
            exit_queue=["alice"],
            queue_timestamps={"alice": 40},
            manual_exits=["bob"],
            exits_today=1,
        ),
        lifecycle=LifecycleSnapshot(
            exits_today=2,
            employment_day=3,
        ),
        rng_state=world_rng_encoded,
        rng_streams={"world": world_rng_encoded},
        relationships={
            "alice": {
                "bob": {"trust": 0.5, "familiarity": 0.2, "rivalry": 0.0},
                "carol": {"trust": -0.2, "familiarity": 0.0, "rivalry": 0.3},
            },
            "bob": {
                "alice": {"trust": 0.4, "familiarity": 0.1, "rivalry": 0.0},
            },
        },
        relationship_metrics={
            "window_start": 0,
            "window_end": 600,
            "total": 2,
            "owners": {"alice": 2},
            "reasons": {"capacity": 1, "decay": 1},
            "history": [
                {
                    "window_start": 0,
                    "window_end": 600,
                    "total": 2,
                    "owners": {"alice": 2},
                    "reasons": {"capacity": 1, "decay": 1},
                }
            ],
        },
        identity=IdentitySnapshot(
            config_id=sample_config.config_id,
            policy_hash="deadbeef",
            observation_variant=sample_config.observation_variant,
            anneal_ratio=0.5,
        ),
    )
    path = manager.save(state)
    loaded = manager.load(path, sample_config)
    assert loaded == state
    # Access migrations via DTO attribute, check DTO fields
    assert loaded.migrations.applied == []
    assert loaded.migrations.required == []


def test_snapshot_config_mismatch_raises(tmp_path: Path, sample_config) -> None:
    manager = SnapshotManager(root=tmp_path)
    state = SimulationSnapshot(
        config_id="other-config",
        tick=3,
        agents={},
        objects={},
        queues=QueueSnapshot(),
        employment=EmploymentSnapshot(),
        relationships={},
        rng_state=encode_rng_state(random.getstate()),
        identity=IdentitySnapshot(config_id="other-config"),
    )
    path = manager.save(state)
    with pytest.raises(ValueError):
        manager.load(path, sample_config)


def test_snapshot_missing_relationships_field_rejected(
    tmp_path: Path, sample_config
) -> None:
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
    state = SimulationSnapshot(
        config_id=sample_config.config_id,
        tick=1,
        agents={},
        objects={},
        queues=QueueSnapshot(),
        employment=EmploymentSnapshot(),
        relationships={},
        rng_state=encode_rng_state(random.getstate()),
        identity=IdentitySnapshot(config_id=sample_config.config_id),
    )
    path = manager.save(state)
    data = json.loads(path.read_text())
    data["schema_version"] = "0.9"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        manager.load(path, sample_config)


def _config_with_snapshot_updates(
    config: SimulationConfig, updates: dict[str, object]
) -> SimulationConfig:
    payload = config.model_dump()
    snapshot_payload = payload.get("snapshot", {})
    snapshot_payload.update(updates)
    payload["snapshot"] = snapshot_payload
    return SimulationConfig.model_validate(payload)


def test_snapshot_mismatch_allowed_when_guardrail_disabled(
    tmp_path: Path, sample_config: SimulationConfig
) -> None:
    relaxed_config = _config_with_snapshot_updates(
        sample_config,
        {"guardrails": {"require_exact_config": False}},
    )
    manager = SnapshotManager(root=tmp_path)
    state = SimulationSnapshot(
        config_id="legacy",
        tick=7,
        agents={},
        objects={},
        queues=QueueSnapshot(),
        employment=EmploymentSnapshot(),
        relationships={},
        rng_state=encode_rng_state(random.getstate()),
        identity=IdentitySnapshot(config_id="legacy"),
    )
    path = manager.save(state)

    loaded = manager.load(path, relaxed_config, allow_migration=False)
    assert loaded.config_id == "legacy"
    # Access migrations DTO attribute
    assert loaded.migrations.required == [f"legacy->{relaxed_config.config_id}"]


def test_snapshot_schema_downgrade_honours_allow_flag(
    tmp_path: Path, sample_config: SimulationConfig
) -> None:
    manager = SnapshotManager(root=tmp_path)
    state = SimulationSnapshot(
        config_id=sample_config.config_id,
        tick=1,
        agents={},
        objects={},
        queues=QueueSnapshot(),
        employment=EmploymentSnapshot(),
        relationships={},
        rng_state=encode_rng_state(random.getstate()),
        identity=IdentitySnapshot(config_id=sample_config.config_id),
    )
    path = manager.save(state)
    data = json.loads(path.read_text())
    data["schema_version"] = "2.0"
    path.write_text(json.dumps(data))

    with pytest.raises(ValueError):
        manager.load(path, sample_config)

    downgradable = _config_with_snapshot_updates(
        sample_config,
        {"guardrails": {"allow_downgrade": True}},
    )
    loaded = manager.load(path, downgradable)
    assert loaded.config_id == sample_config.config_id


def test_world_relationship_snapshot_round_trip(
    tmp_path: Path, sample_config: SimulationConfig
) -> None:
    random.seed(1337)
    world_rng = random.Random(2024)
    events_rng = random.Random(9090)
    policy_rng = random.Random(7070)
    world = WorldState.from_config(sample_config, rng=world_rng)
    world.tick = 77
    world.update_relationship("alice", "bob", trust=0.4, familiarity=0.2)
    world.update_relationship("alice", "carol", rivalry=0.3)

    world.register_object(object_id="fridge_1", object_type="fridge")
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
    world.employment.import_state(
        {
            "exit_queue": ["alice"],
            "queue_timestamps": {"alice": world.tick},
            "manual_exits": ["bob"],
            "exits_today": 1,
        }
    )
    world.set_employment_exits_today(1)

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
    telemetry.import_console_buffer([{"cmd": "foo"}])

    scheduler = PerturbationScheduler(sample_config, rng=events_rng)
    scheduler.enqueue(
        [
            ScheduledPerturbation(
                event_id="evt_test",
                spec_name="price_spike",
                kind=PerturbationKind.PRICE_SPIKE,
                started_at=0,
                ends_at=60,
                payload={"magnitude": 1.2},
                targets=["economy"],
            )
        ]
    )

    policy_identity = {
        "config_id": sample_config.config_id,
        "policy_hash": "snapshot-hash",
        "observation_variant": sample_config.observation_variant,
        "anneal_ratio": 0.2,
    }

    telemetry.update_policy_identity(policy_identity)

    state = snapshot_from_world(
        sample_config,
        world,
        telemetry=telemetry,
        perturbations=scheduler,
        rng_streams={
            "world": world.rng,
            "events": scheduler.rng,
            "policy": policy_rng,
        },
        identity=policy_identity,
    )
    baseline_rng_state = random.getstate()

    manager = SnapshotManager(root=tmp_path)
    saved_path = manager.save(state)
    loaded = manager.load(saved_path, sample_config)

    restored_world = WorldState.from_config(sample_config, rng=random.Random(2024))
    apply_snapshot_to_world(restored_world, loaded)
    restored_telemetry = TelemetryPublisher(sample_config)
    from townlet.snapshots.state import apply_snapshot_to_telemetry

    apply_snapshot_to_telemetry(restored_telemetry, loaded)

    assert restored_world.tick == world.tick
    assert restored_world.relationships_snapshot() == world.relationships_snapshot()
    assert set(restored_world.agents.keys()) == set(world.agents.keys())
    assert restored_world.agents["alice"].needs == world.agents["alice"].needs
    assert restored_world.objects.keys() == world.objects.keys()
    assert (
        restored_world.queue_manager.export_state()
        == world.queue_manager.export_state()
    )
    assert restored_world.employment.export_state() == world.employment.export_state()
    assert restored_world.employment_exits_today() == world.employment_exits_today()
    assert random.getstate() == baseline_rng_state
    assert restored_world.get_rng_state() == world.get_rng_state()
    assert "world" in state.rng_streams
    assert "events" in state.rng_streams
    assert "policy" in state.rng_streams
    assert state.rng_streams["world"] == encode_rng_state(world.get_rng_state())
    assert state.rng_streams["events"] == encode_rng_state(scheduler.rng_state())
    assert state.rng_streams["policy"] == encode_rng_state(policy_rng.getstate())
    # Compare identity DTO attributes
    assert state.identity.config_id == policy_identity["config_id"]
    assert state.identity.policy_hash == policy_identity["policy_hash"]
    assert state.identity.observation_variant == policy_identity["observation_variant"]
    assert state.identity.anneal_ratio == policy_identity["anneal_ratio"]
    assert loaded.identity == state.identity
    # Access migrations DTO attributes
    assert state.migrations.applied == []
    assert state.migrations.required == []
    # Compare perturbations DTO with scheduler export (only fields in DTO)
    scheduler_state = scheduler.export_state()
    assert state.perturbations.pending == scheduler_state["pending"]
    assert state.perturbations.active == scheduler_state["active"]
    restored_state = restored_telemetry.export_state()
    baseline_state = telemetry.export_state()
    assert restored_state.get("relationship_metrics") == world.relationship_metrics_snapshot()
    assert baseline_state.get("relationship_metrics") == {"total": 3}
    # Pop fields that aren't captured in TelemetrySnapshot DTO
    for key in ["relationship_metrics", "economy_settings", "utilities", "events", "employment_metrics"]:
        restored_state.pop(key, None)
        baseline_state.pop(key, None)
    assert restored_state == baseline_state
    # Drain console buffer from restored telemetry and verify it matches what we imported
    restored_console = list(restored_telemetry.drain_console_buffer())
    assert restored_console == [{"cmd": "foo"}]
    # Perturbation scheduler runs outside the manager in this test; ensure state
    # persists via the scheduler snapshot payload.

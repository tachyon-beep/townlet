from __future__ import annotations

import pytest

from pathlib import Path

from townlet.config import load_config
from townlet.telemetry.relationship_metrics import (
    RelationshipChurnAccumulator,
    RelationshipEvictionSample,
)
from townlet.world.grid import AgentSnapshot, InteractiveObject, WorldState


def test_record_eviction_tracks_counts() -> None:
    acc = RelationshipChurnAccumulator(window_ticks=10, max_samples=4)
    acc.record_eviction(tick=0, owner_id="alice", evicted_id="bob", reason="capacity")
    acc.record_eviction(tick=5, owner_id="alice", evicted_id="carol", reason="decay")
    snapshot = acc.snapshot()
    assert snapshot["total"] == 2
    assert snapshot["owners"] == {"alice": 2}
    assert snapshot["reasons"] == {"capacity": 1, "decay": 1}


def test_window_rolls_and_history_records_samples() -> None:
    acc = RelationshipChurnAccumulator(window_ticks=3, max_samples=2)
    # Two events in first window
    acc.record_eviction(tick=0, owner_id="alice", evicted_id="bob", reason="capacity")
    acc.record_eviction(tick=1, owner_id="bob", evicted_id="carol", reason="decay")
    # Advance into next window, triggering roll
    acc.record_eviction(tick=3, owner_id="carol", evicted_id="alice", reason="capacity")

    history = list(acc.history())
    assert len(history) == 1
    sample: RelationshipEvictionSample = history[0]
    assert sample.window_start == 0
    assert sample.window_end == 3
    assert sample.total_evictions == 2
    assert sample.per_owner == {"alice": 1, "bob": 1}
    assert sample.per_reason == {"capacity": 1, "decay": 1}

    snapshot = acc.snapshot()
    assert snapshot["window_start"] == 3
    assert snapshot["total"] == 1
    assert snapshot["owners"] == {"carol": 1}


def test_latest_payload_round_trips_via_ingest() -> None:
    acc = RelationshipChurnAccumulator(window_ticks=4, max_samples=3)
    for idx in range(6):
        acc.record_eviction(tick=idx, owner_id=f"agent-{idx % 2}", evicted_id=f"evicted-{idx}")
    payload = acc.latest_payload()

    restored = RelationshipChurnAccumulator(window_ticks=4, max_samples=3)
    restored.ingest_payload(payload)

    assert restored.snapshot() == acc.snapshot()
    assert [s.to_payload() for s in restored.history()] == [
        s.to_payload() for s in acc.history()
    ]


def test_invalid_configuration_raises() -> None:
    with pytest.raises(ValueError):
        RelationshipChurnAccumulator(window_ticks=0)
    acc = RelationshipChurnAccumulator(window_ticks=5)
    with pytest.raises(ValueError):
        acc.record_eviction(tick=-1, owner_id="agent", evicted_id="other")


def test_world_relationship_metrics_records_evictions() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    max_edges = world.config.conflict.rivalry.max_edges
    for idx in range(max_edges + 2):
        world.register_rivalry_conflict("alice", f"agent-{idx}")

    payload = world.relationship_metrics_snapshot()
    assert payload["total"] > 0
    assert payload["owners"]["alice"] >= 1
    assert payload["reasons"]["capacity"] >= 1


def test_world_relationship_update_symmetry() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.update_relationship("alice", "bob", trust=0.3, familiarity=0.1)

    snapshot = world.relationships_snapshot()
    assert "alice" in snapshot and "bob" in snapshot
    assert snapshot["alice"]["bob"]["trust"] == pytest.approx(0.3)
    assert snapshot["bob"]["alice"]["trust"] == pytest.approx(0.3)


def test_queue_events_modify_relationships() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
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

    world._record_queue_conflict(
        object_id="shower_1",
        actor="alice",
        rival="bob",
        reason="ghost_step",
        queue_length=2,
        intensity=None,
    )
    negative_snapshot = world.relationships_snapshot()
    assert negative_snapshot["alice"]["bob"]["rivalry"] > 0.0

    world._record_queue_conflict(
        object_id="shower_1",
        actor="alice",
        rival="bob",
        reason="handover",
        queue_length=1,
        intensity=None,
    )
    positive_snapshot = world.relationships_snapshot()
    assert positive_snapshot["alice"]["bob"]["trust"] > 0.0


def test_shared_meal_updates_relationship() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=5.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=5.0,
    )
    world.objects["fridge_1"] = InteractiveObject(object_id="fridge_1", object_type="fridge", stock={"meals": 5})

    world.tick = 10
    world._handle_eat_meal_start("alice", "fridge_1")
    world._handle_eat_meal_start("bob", "fridge_1")

    snapshot = world.relationships_snapshot()
    assert snapshot["alice"]["bob"]["trust"] > 0.0
    assert snapshot["alice"]["bob"]["familiarity"] > 0.0


def test_absence_triggers_took_my_shift_relationships() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    job_id = next(iter(config.jobs))
    job_loc = tuple(config.jobs[job_id].location) if config.jobs[job_id].location else (0, 0)

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(10, 10),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=5.0,
        job_id=job_id,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=job_loc,
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=5.0,
        job_id=job_id,
    )
    ctx_alice = world._get_employment_context("alice")
    ctx_bob = world._get_employment_context("bob")
    ctx_bob["state"] = "on_time"
    world.agents["bob"].on_shift = True

    world._employment_apply_state_effects(
        snapshot=world.agents["alice"],
        ctx=ctx_alice,
        state="absent",
        at_required_location=False,
        wage_rate=0.0,
        lateness_penalty=0.0,
        employment_cfg=config.employment,
    )

    snapshot = world.relationships_snapshot()
    assert snapshot["alice"]["bob"]["trust"] < 0.0
    assert snapshot["alice"]["bob"]["rivalry"] > 0.0


def test_late_help_creates_positive_relationship() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    job_id = next(iter(config.jobs))
    job_loc = tuple(config.jobs[job_id].location) if config.jobs[job_id].location else (0, 0)

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(10, 10),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=5.0,
        job_id=job_id,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=job_loc,
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=5.0,
        job_id=job_id,
    )
    ctx_alice = world._get_employment_context("alice")
    ctx_bob = world._get_employment_context("bob")
    ctx_bob["state"] = "on_time"
    world.agents["bob"].on_shift = True

    world._employment_apply_state_effects(
        snapshot=world.agents["alice"],
        ctx=ctx_alice,
        state="late",
        at_required_location=False,
        wage_rate=0.0,
        lateness_penalty=0.0,
        employment_cfg=config.employment,
    )

    snapshot = world.relationships_snapshot()
    assert snapshot["alice"]["bob"]["trust"] > 0.0
    assert snapshot["alice"]["bob"]["rivalry"] < 0.1


def test_chat_outcomes_adjust_relationships() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )

    world.record_chat_success("alice", "bob", quality=0.8)
    snapshot = world.relationships_snapshot()
    assert snapshot["alice"]["bob"]["trust"] > 0.0
    assert snapshot["alice"]["bob"]["familiarity"] > 0.0

    world.record_chat_failure("alice", "bob")
    snapshot = world.relationships_snapshot()
    assert snapshot["alice"]["bob"]["familiarity"] < 0.1
    assert snapshot["alice"]["bob"]["rivalry"] > 0.0

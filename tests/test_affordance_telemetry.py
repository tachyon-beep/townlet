from __future__ import annotations

from tests.test_affordance_hooks import make_world, request_object
from townlet.world.affordances import AffordanceOutcome, apply_affordance_outcome
from townlet.world.grid import AgentSnapshot


def test_affordance_runtime_snapshot_contains_ids() -> None:
    loop, world = make_world()
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"energy": 0.2},
        wallet=2.0,
    )

    request_object(world, "bed_1", "alice")
    started, _ = world.affordance_runtime.start("alice", "bed_1", "rest_sleep", tick=world.tick)
    assert started is True

    loop.step()

    runtime = loop.telemetry.latest_affordance_runtime()
    running = runtime.get("running", {})
    assert "bed_1" in running
    entry = running["bed_1"]
    assert entry["agent_id"] == "alice"
    assert entry["object_id"] == "bed_1"
    assert entry["affordance_id"] == "rest_sleep"
    assert entry["duration_remaining"] >= 0

    loop.telemetry.close()


def test_apply_affordance_outcome_retains_metadata() -> None:
    snapshot = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"energy": 0.5},
        wallet=1.0,
    )
    outcome = AffordanceOutcome(
        agent_id="alice",
        kind="release",
        success=False,
        duration=0,
        object_id="bed_1",
        affordance_id="rest_sleep",
        tick=5,
        metadata={"reason": "manual_cancel"},
    )
    apply_affordance_outcome(snapshot, outcome)
    history = snapshot.inventory.get("_affordance_outcomes")
    assert history is not None
    assert history[-1] == {
        "kind": "release",
        "success": False,
        "duration": 0,
        "object_id": "bed_1",
        "affordance_id": "rest_sleep",
        "tick": 5,
        "metadata": {"reason": "manual_cancel"},
    }

    # Ensure history is capped at 10 entries
    for index in range(12):
        apply_affordance_outcome(
            snapshot,
            AffordanceOutcome(
                agent_id="alice",
                kind="release",
                success=False,
                duration=0,
                object_id="bed_1",
                affordance_id="rest_sleep",
                tick=6 + index,
                metadata={"reason": f"extra-{index}"},
            ),
        )
    history = snapshot.inventory.get("_affordance_outcomes")
    assert history is not None
    assert len(history) <= 10
    latest = history[-1]
    assert latest["affordance_id"] == "rest_sleep"
    assert latest["object_id"] == "bed_1"

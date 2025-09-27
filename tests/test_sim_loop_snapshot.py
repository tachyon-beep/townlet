from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import pytest

from townlet.config import SimulationConfig, load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.snapshots.state import snapshot_from_world
from townlet.world.grid import AgentSnapshot


@pytest.fixture(scope="module")
def base_config():
    config_path = Path("configs/examples/poc_hybrid.yaml")
    if not config_path.exists():
        pytest.skip("example config not found")
    return load_config(config_path)


def test_simulation_loop_snapshot_round_trip(tmp_path: Path, base_config) -> None:
    random.seed(2024)
    loop = SimulationLoop(base_config)
    loop.world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.4, "energy": 0.6},
    )
    loop.world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(1, 0),
        needs={"hunger": 0.4, "hygiene": 0.3, "energy": 0.7},
    )
    loop.world.register_object(object_id="fridge_1", object_type="fridge")

    loop.world.update_relationship("alice", "bob", trust=0.3, familiarity=0.1)
    loop.telemetry.queue_console_command({"cmd": "noop"})
    loop.perturbations.enqueue([{"event": "test"}])
    saved_path = loop.save_snapshot(tmp_path)

    restored = SimulationLoop(base_config)
    restored.load_snapshot(saved_path)

    assert restored.tick == loop.tick
    assert (
        restored.world.relationships_snapshot() == loop.world.relationships_snapshot()
    )
    assert set(restored.world.agents.keys()) == set(loop.world.agents.keys())
    assert restored.world.agents["alice"].needs == loop.world.agents["alice"].needs
    assert restored.world.objects.keys() == loop.world.objects.keys()

    restored_telemetry = restored.telemetry.export_state()
    baseline_telemetry = loop.telemetry.export_state()
    for key in (
        "queue_metrics",
        "employment_metrics",
        "conflict_snapshot",
        "policy_identity",
    ):
        assert restored_telemetry.get(key) == baseline_telemetry.get(key)
    assert (
        restored.telemetry.export_console_buffer()
        == loop.telemetry.export_console_buffer()
    )
    assert restored.perturbations.export_state() == loop.perturbations.export_state()


def test_save_snapshot_uses_config_root_and_identity_override(
    tmp_path: Path, base_config
) -> None:
    custom_root = tmp_path / "autosave"
    payload = base_config.model_dump()
    payload["snapshot"] = {
        **payload.get("snapshot", {}),
        "storage": {"root": str(custom_root)},
        "identity": {
            "policy_hash": "feedface" * 5,
            "policy_artifact": str(tmp_path / "policy.pt"),
            "observation_variant": "full",
        },
    }
    override_config = SimulationConfig.model_validate(payload)
    loop = SimulationLoop(override_config)
    snapshot_path = loop.save_snapshot()
    assert snapshot_path.parent == custom_root
    document = json.loads(snapshot_path.read_text())
    identity = document["state"]["identity"]
    assert identity["policy_hash"] == "feedface" * 5
    assert identity["policy_artifact"] == str(tmp_path / "policy.pt")
    assert identity["observation_variant"] == "full"
    latest_identity = loop.telemetry.latest_policy_identity()
    assert latest_identity is not None
    assert latest_identity["policy_hash"] == "feedface" * 5


def test_simulation_resume_equivalence(tmp_path: Path, base_config) -> None:
    random.seed(2025)

    def setup_loop() -> SimulationLoop:
        loop = SimulationLoop(base_config)
        loop.world.register_object(object_id="fridge_1", object_type="fridge")
        loop.world.agents["alice"] = AgentSnapshot(
            agent_id="alice",
            position=(0, 0),
            needs={"hunger": 0.3, "hygiene": 0.6, "energy": 0.7},
            wallet=5.0,
        )
        loop.world.agents["bob"] = AgentSnapshot(
            agent_id="bob",
            position=(1, 0),
            needs={"hunger": 0.35, "hygiene": 0.5, "energy": 0.65},
            wallet=4.0,
        )
        return loop

    baseline = setup_loop()
    baseline_steps = 2
    for _ in range(baseline_steps):
        baseline.step()

    snapshot_root = tmp_path / "snapshots"
    snapshot_root.mkdir()
    saved_path = baseline.save_snapshot(snapshot_root)
    baseline.telemetry.queue_console_command({"cmd": "pending"})

    baseline_snapshots: list[dict[str, object]] = []
    for _ in range(3):
        baseline.step()
        baseline_snapshots.append(
            _normalise_snapshot(
                snapshot_from_world(
                    base_config,
                    baseline.world,
                    telemetry=baseline.telemetry,
                ).as_dict()
            )
        )

    resumed = SimulationLoop(base_config)
    resumed.load_snapshot(saved_path)
    resumed.telemetry.queue_console_command({"cmd": "pending"})

    resumed_snapshots: list[dict[str, object]] = []
    for _ in range(3):
        resumed.step()
        resumed_snapshots.append(
            _normalise_snapshot(
                snapshot_from_world(
                    base_config,
                    resumed.world,
                    telemetry=resumed.telemetry,
                ).as_dict()
            )
        )

    assert resumed_snapshots == baseline_snapshots
    restored_telemetry = resumed.telemetry.export_state()
    baseline_telemetry = baseline.telemetry.export_state()
    for key in (
        "queue_metrics",
        "employment_metrics",
        "conflict_snapshot",
        "policy_identity",
    ):
        assert restored_telemetry.get(key) == baseline_telemetry.get(key)
    assert (
        resumed.telemetry.export_console_buffer()
        == baseline.telemetry.export_console_buffer()
    )


def test_policy_transitions_resume(tmp_path: Path, base_config) -> None:
    random.seed(303)
    loop = SimulationLoop(base_config)
    loop.world.register_object(object_id="fridge_1", object_type="fridge")
    loop.world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.4, "hygiene": 0.4, "energy": 0.6},
    )
    loop.step()

    trajectory_before = loop.policy.collect_trajectory(clear=True)
    snapshot_path = loop.save_snapshot(tmp_path)

    resumed = SimulationLoop(base_config)
    resumed.load_snapshot(snapshot_path)
    loop.step()
    resumed.step()
    resumed_frames = resumed.policy.collect_trajectory(clear=True)
    baseline_frames = loop.policy.collect_trajectory(clear=True)
    assert len(resumed_frames) == len(baseline_frames)
    compare_keys = {"agent_id", "action", "rewards", "dones"}
    for lhs, rhs in zip(resumed_frames, baseline_frames):
        for key in compare_keys:
            assert lhs[key] == rhs[key]


def _normalise_snapshot(snapshot: dict[str, object]) -> dict[str, object]:
    keys = {
        "config_id",
        "tick",
        "agents",
        "objects",
        "queues",
        "embeddings",
        "employment",
        "lifecycle",
        "identity",
        "rng_streams",
    }
    return {key: snapshot[key] for key in keys if key in snapshot}

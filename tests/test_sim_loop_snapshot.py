from __future__ import annotations

from pathlib import Path
import random

import numpy as np

import pytest

from townlet.config import load_config
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
    assert restored.world.relationships_snapshot() == loop.world.relationships_snapshot()
    assert set(restored.world.agents.keys()) == set(loop.world.agents.keys())
    assert restored.world.agents["alice"].needs == loop.world.agents["alice"].needs
    assert restored.world.objects.keys() == loop.world.objects.keys()
    assert restored.telemetry.export_state() == loop.telemetry.export_state()
    assert restored.telemetry.export_console_buffer() == loop.telemetry.export_console_buffer()
    assert restored.perturbations.export_state() == loop.perturbations.export_state()


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
            snapshot_from_world(
                base_config,
                baseline.world,
                telemetry=baseline.telemetry,
            ).as_dict()
        )

    resumed = SimulationLoop(base_config)
    resumed.load_snapshot(saved_path)
    resumed.telemetry.queue_console_command({"cmd": "pending"})

    resumed_snapshots: list[dict[str, object]] = []
    for _ in range(3):
        resumed.step()
        resumed_snapshots.append(
            snapshot_from_world(
                base_config,
                resumed.world,
                telemetry=resumed.telemetry,
            ).as_dict()
        )

    assert resumed_snapshots == baseline_snapshots
    assert resumed.telemetry.export_state() == baseline.telemetry.export_state()
    assert resumed.telemetry.export_console_buffer() == baseline.telemetry.export_console_buffer()

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

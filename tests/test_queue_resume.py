from __future__ import annotations

from pathlib import Path

import random

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world.grid import AgentSnapshot


@pytest.fixture(scope="module")
def base_config():
    config_path = Path("configs/examples/poc_hybrid.yaml")
    if not config_path.exists():
        pytest.skip("example config not found")
    return load_config(config_path)


def _setup_loop(config) -> SimulationLoop:
    loop = SimulationLoop(config)
    world = loop.world
    world.register_object(object_id="stove_1", object_type="stove")
    for idx in range(3):
        agent_id = f"agent_{idx}"
        world.agents[agent_id] = AgentSnapshot(
            agent_id=agent_id,
            position=(idx, 0),
            needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
            wallet=1.0,
        )
    return loop


def test_queue_metrics_resume(tmp_path: Path, base_config) -> None:
    random.seed(99)
    loop = _setup_loop(base_config)
    world = loop.world

    object_id = "stove_1"
    for idx in range(2):
        world.queue_manager.request_access(object_id, f"agent_{idx}", world.tick)
    world.queue_manager.record_blocked_attempt(object_id)
    world.queue_manager.record_blocked_attempt(object_id)

    snapshot_path = loop.save_snapshot(tmp_path)
    baseline_metrics = world.queue_manager.metrics()
    baseline_state = world.queue_manager.export_state()

    resumed = SimulationLoop(base_config)
    resumed.load_snapshot(snapshot_path)

    assert resumed.world.queue_manager.metrics() == baseline_metrics
    assert resumed.world.queue_manager.export_state() == baseline_state

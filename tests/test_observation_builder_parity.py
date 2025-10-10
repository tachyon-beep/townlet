from __future__ import annotations

from pathlib import Path

import numpy as np

from townlet.config.loader import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.observations.builder import ObservationBuilder
from townlet.world.grid import AgentSnapshot


def _make_loop() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.conflict.rivalry.avoid_threshold = 0.1
    config.employment.enforce_job_loop = True
    config.observations_config.hybrid.include_targets = True
    loop = SimulationLoop(config)
    loop.world.agents.clear()
    loop.world.register_object(object_id="stove_test", object_type="stove", position=(2, 0))
    loop.world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.4, "hygiene": 0.5, "energy": 0.6},
        wallet=2.0,
        last_action_id="wait",
        last_action_success=True,
        last_action_duration=4,
    )
    loop.world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(1, 0),
        needs={"hunger": 0.7, "hygiene": 0.8, "energy": 0.9},
        wallet=3.0,
    )
    loop.world.assign_jobs_to_agents()
    return loop


def test_observation_builder_matches_baseline_snapshot(tmp_path):
    baseline_path = Path("tmp/wp-c/phase4_baseline_shapes.json")
    if not baseline_path.exists():
        raise RuntimeError("Baseline snapshot missing; rerun Phase 0 capture (tmp/wp-c/phase4_baseline_shapes.json)")

    loop = _make_loop()
    builder = ObservationBuilder(loop.config)

    batch = builder.build_batch(loop.world_adapter, terminated={})
    assert set(batch) == {"alice", "bob"}
    for _agent_id, payload in batch.items():
        features = payload["features"]
        metadata = payload["metadata"]
        assert len(metadata["feature_names"]) == features.shape[0]
        assert metadata["variant"] == builder.variant
        assert metadata["map_channels"] == list(builder.MAP_CHANNELS)
    loop.close()


def test_observation_builder_adapter_parity():
    loop = _make_loop()
    builder = ObservationBuilder(loop.config)

    batch_raw = builder.build_batch(loop.world, terminated={})
    batch_adapter = builder.build_batch(loop.world_adapter, terminated={})

    for agent_id in ("alice", "bob"):
        raw_payload = batch_raw[agent_id]
        adapter_payload = batch_adapter[agent_id]
        np.testing.assert_allclose(raw_payload["features"], adapter_payload["features"])
        assert raw_payload["metadata"]["map_channels"] == adapter_payload["metadata"]["map_channels"]
    loop.close()

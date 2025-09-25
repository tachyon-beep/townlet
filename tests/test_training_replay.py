from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from townlet.config import load_config
from townlet.policy.models import torch_available
from townlet.policy.replay import (
    ReplayDataset,
    ReplayDatasetConfig,
    frames_to_replay_sample,
    load_replay_sample,
)
from townlet.policy.runner import TrainingHarness
from townlet.world.grid import AgentSnapshot, WorldState
from townlet.observations.builder import ObservationBuilder
from townlet.core.sim_loop import SimulationLoop


def _make_sample(base_dir: Path, rivalry_increment: float, avoid_threshold: float, suffix: str) -> tuple[Path, Path]:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.conflict.rivalry.increment_per_conflict = rivalry_increment
    config.conflict.rivalry.avoid_threshold = avoid_threshold
    world = WorldState.from_config(config)
    world.register_object("stove_1", "stove")
    world.agents["alice"] = AgentSnapshot(
        "alice",
        (0, 0),
        {"hunger": 0.3, "hygiene": 0.4, "energy": 0.5},
        wallet=2.0,
    )
    world.agents["bob"] = AgentSnapshot(
        "bob",
        (1, 0),
        {"hunger": 0.6, "hygiene": 0.7, "energy": 0.8},
        wallet=3.0,
    )
    world.register_rivalry_conflict("alice", "bob")
    builder = ObservationBuilder(config)
    obs = builder.build_batch(world, terminated={})["alice"]
    timesteps = 2
    map_seq = np.stack([obs["map"], obs["map"]], axis=0)
    feature_seq = np.stack([obs["features"], obs["features"]], axis=0)
    sample_path = base_dir / f"replay_sample_{suffix}.npz"
    meta_path = base_dir / f"replay_sample_{suffix}.json"
    actions = np.array([1, 0], dtype=np.int64)
    old_log_probs = np.array([-0.5, -0.4], dtype=np.float32)
    value_preds = np.array([0.1, 0.05, 0.02], dtype=np.float32)
    rewards = np.array([0.05, 0.02], dtype=np.float32)
    dones = np.array([False, True], dtype=np.bool_)
    np.savez(
        sample_path,
        map=map_seq,
        features=feature_seq,
        actions=actions,
        old_log_probs=old_log_probs,
        value_preds=value_preds,
        rewards=rewards,
        dones=dones,
    )
    feature_names = obs["metadata"]["feature_names"]
    obs["metadata"]["rivalry_example"] = {
        "rivalry_max": float(obs["features"][feature_names.index("rivalry_max")]),
        "rivalry_avoid_count": float(obs["features"][feature_names.index("rivalry_avoid_count")]),
    }
    obs["metadata"]["training_arrays"] = [
        "actions",
        "old_log_probs",
        "value_preds",
        "rewards",
        "dones",
    ]
    obs["metadata"]["timesteps"] = timesteps
    obs["metadata"]["value_pred_steps"] = len(value_preds)
    obs["metadata"]["action_dim"] = 3
    meta_path.write_text(json.dumps(obs["metadata"], indent=2))
    return sample_path, meta_path


def test_training_harness_replay_stats(tmp_path: Path) -> None:
    sample_path, meta_path = _make_sample(tmp_path, 0.2, 0.3, "single")
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    harness = TrainingHarness(config)
    stats = harness.run_replay(sample_path=sample_path, meta_path=meta_path)
    assert stats["feature_dim"] > 0
    assert stats["conflict.rivalry_max_mean"] >= 0.0


def test_replay_dataset_batch_iteration(tmp_path: Path) -> None:
    sample_a = _make_sample(tmp_path, 0.2, 0.3, "a")
    sample_b = _make_sample(tmp_path, 0.6, 0.2, "b")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            [
                {"sample": str(sample_a[0]), "meta": str(sample_a[1])},
                {"sample": str(sample_b[0]), "meta": str(sample_b[1])},
            ],
            indent=2,
        )
    )
    dataset_config = ReplayDatasetConfig.from_manifest(manifest, batch_size=1, shuffle=True, seed=42)
    dataset = ReplayDataset(dataset_config)
    batches = list(dataset)
    assert len(batches) == 2
    for batch in batches:
        assert batch.maps.shape == (1, 2, *batch.maps.shape[2:])
        assert batch.features.shape == (1, 2, batch.features.shape[2])
        assert batch.conflict_stats()
        assert batch.actions.shape == (1, 2)
        assert batch.value_preds.shape[1] in {2, 3}


def test_replay_loader_schema_guard(tmp_path: Path) -> None:
    sample_path, meta_path = _make_sample(tmp_path, 0.2, 0.3, "guard")
    meta = json.loads(meta_path.read_text())
    meta["feature_names"].remove("rivalry_max")
    meta_path.write_text(json.dumps(meta, indent=2))
    with pytest.raises(ValueError):
        load_replay_sample(sample_path, meta_path)


def test_replay_dataset_streaming(tmp_path: Path) -> None:
    sample_a = _make_sample(tmp_path, 0.3, 0.4, "stream_a")
    sample_b = _make_sample(tmp_path, 0.4, 0.5, "stream_b")
    manifest = tmp_path / "manifest_stream.json"
    manifest.write_text(
        json.dumps(
            [
                {"sample": str(sample_a[0]), "meta": str(sample_a[1])},
                {"sample": str(sample_b[0]), "meta": str(sample_b[1])},
            ],
            indent=2,
        )
    )
    config = ReplayDatasetConfig.from_manifest(manifest, batch_size=2, streaming=True)
    dataset = ReplayDataset(config)
    batches = list(dataset)
    assert batches
    for batch in batches:
        assert batch.maps.ndim == 5
        assert batch.maps.shape[1] == 2
        assert batch.conflict_stats()
        assert batch.actions.shape[0] == batch.features.shape[0]
        assert batch.actions.shape[1] == 2
        assert batch.value_preds.shape[1] in {2, 3}


def test_replay_loader_missing_training_arrays(tmp_path: Path) -> None:
    sample_path, meta_path = _make_sample(tmp_path, 0.2, 0.3, "missing")
    stripped_path = tmp_path / "replay_sample_missing_actions.npz"
    with np.load(sample_path) as handle:
        np.savez(
            stripped_path,
            map=handle["map"],
            features=handle["features"],
            old_log_probs=handle["old_log_probs"],
            value_preds=handle["value_preds"],
            rewards=handle["rewards"],
            dones=handle["dones"],
        )
    with pytest.raises(ValueError):
        load_replay_sample(stripped_path, meta_path)


def test_replay_loader_value_length_mismatch(tmp_path: Path) -> None:
    sample_path, meta_path = _make_sample(tmp_path, 0.2, 0.3, "value_mismatch")
    broken_path = tmp_path / "replay_sample_value_mismatch.npz"
    with np.load(sample_path) as handle:
        value_preds = np.concatenate([handle["value_preds"], np.array([0.0], dtype=np.float32)])
        np.savez(
            broken_path,
            map=handle["map"],
            features=handle["features"],
            actions=handle["actions"],
            old_log_probs=handle["old_log_probs"],
            value_preds=value_preds,
            rewards=handle["rewards"],
            dones=handle["dones"],
        )
    with pytest.raises(ValueError):
        load_replay_sample(broken_path, meta_path)



@pytest.mark.skipif(not torch_available(), reason="Torch not installed")
def test_training_harness_run_ppo(tmp_path: Path) -> None:
    sample_a = _make_sample(tmp_path, 0.2, 0.3, 'ppo_a')
    sample_b = _make_sample(tmp_path, 0.5, 0.2, 'ppo_b')
    dataset_config = ReplayDatasetConfig(
        entries=[sample_a, sample_b],
        batch_size=2,
        shuffle=False,
    )
    harness = TrainingHarness(load_config(Path('configs/examples/poc_hybrid.yaml')))
    log_path = tmp_path / 'ppo_log.jsonl'
    summary = harness.run_ppo(dataset_config, epochs=2, log_path=log_path)
    assert summary['epoch'] == 2.0
    assert 'loss_total' in summary
    assert summary['transitions'] == pytest.approx(4.0)
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 2
    last = json.loads(lines[-1])
    assert last['epoch'] == 2.0
    assert 'loss_policy' in last


def test_policy_runtime_collects_frames(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.world.register_object("stove_1", "stove")
    loop.world.agents["alice"] = AgentSnapshot(
        "alice",
        (0, 0),
        {"hunger": 0.3, "hygiene": 0.5, "energy": 0.4},
        wallet=1.0,
    )
    loop.world.agents["bob"] = AgentSnapshot(
        "bob",
        (1, 0),
        {"hunger": 0.6, "hygiene": 0.6, "energy": 0.7},
        wallet=1.5,
    )

    for _ in range(3):
        loop.step()

    frames = [frame for frame in loop.policy.collect_trajectory() if frame["agent_id"] == "alice"]
    assert len(frames) == 3
    sample = frames_to_replay_sample(frames)
    assert sample.map.shape[0] == 3
    assert sample.features.shape[0] == 3
    assert sample.actions.shape[0] == 3
    assert sample.value_preds.shape[0] == 4
    assert sample.metadata["timesteps"] == 3

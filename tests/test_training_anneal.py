from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from townlet.config import AnnealStage, load_config
from townlet.policy.models import torch_available
from townlet.policy.replay import ReplayDatasetConfig, frames_to_replay_sample
from townlet.policy.runner import TrainingHarness


def _write_sample(
    output_dir: Path, stem: str, timesteps: int, action_dim: int = 2
) -> tuple[Path, Path]:
    feature_names = [f"f{i}" for i in range(4)] + ["rivalry_max", "rivalry_avoid_count"]
    frames = []
    for idx in range(timesteps):
        features = np.zeros(len(feature_names), dtype=np.float32)
        features[0] = float(idx % action_dim)
        frames.append(
            {
                "map": np.zeros((4, 4, 1), dtype=np.float32),
                "features": features,
                "action_id": idx % action_dim,
                "rewards": [0.1],
                "dones": [idx == timesteps - 1],
                "value_pred": 0.0,
                "metadata": {
                    "feature_names": feature_names,
                    "trajectory_id": stem,
                    "agent_id": "agent",
                },
            }
        )
    sample = frames_to_replay_sample(frames)
    npz_path = output_dir / f"{stem}.npz"
    json_path = output_dir / f"{stem}.json"
    np.savez(
        npz_path,
        map=sample.map,
        features=sample.features,
        actions=sample.actions,
        old_log_probs=sample.old_log_probs,
        value_preds=sample.value_preds,
        rewards=sample.rewards,
        dones=sample.dones,
    )
    json_path.write_text(json.dumps(sample.metadata, indent=2))
    return npz_path, json_path


@pytest.mark.skipif(not torch_available(), reason="Torch not installed")
def test_run_anneal_bc_then_ppo(tmp_path: Path) -> None:
    # Prepare BC manifest
    bc_dir = tmp_path / "bc"
    bc_dir.mkdir()
    npz_path, json_path = _write_sample(bc_dir, "bc_sample", timesteps=8)
    bc_manifest = tmp_path / "bc_manifest.json"
    bc_manifest.write_text(
        json.dumps(
            [
                {
                    "sample": str(npz_path),
                    "meta": str(json_path),
                    "metrics": {"reward_sum": 0.8},
                    "accepted": True,
                }
            ],
            indent=2,
        )
    )

    # Prepare replay manifest for PPO stage
    replay_dir = tmp_path / "replay"
    replay_dir.mkdir()
    r_npz, r_json = _write_sample(replay_dir, "replay_sample", timesteps=6)
    replay_manifest = tmp_path / "replay_manifest.json"
    replay_manifest.write_text(
        json.dumps([{"sample": str(r_npz), "meta": str(r_json)}], indent=2)
    )

    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.training.bc.manifest = bc_manifest
    config.training.anneal_schedule = [
        AnnealStage(cycle=0, mode="bc", epochs=5, bc_weight=1.0),
        AnnealStage(cycle=1, mode="ppo", epochs=1),
    ]
    config.training.replay_manifest = replay_manifest
    harness = TrainingHarness(config)

    results = harness.run_anneal(log_dir=tmp_path / "logs")
    assert len(results) >= 2
    bc_stage = results[0]
    assert bc_stage["mode"] == "bc"
    assert bc_stage["passed"]
    ppo_stage = results[1]
    assert ppo_stage["mode"] == "ppo"
    assert "loss_total" in ppo_stage

    log_file = tmp_path / "logs" / "anneal_results.json"
    assert log_file.exists()

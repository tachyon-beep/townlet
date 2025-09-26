from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import runpy

from townlet.policy.replay import frames_to_replay_sample


def _write_sample(output_dir: Path, stem: str, rewards: np.ndarray, timesteps: int) -> None:
    frames = []
    feature_names = [f"f{i}" for i in range(8)] + ["rivalry_max", "rivalry_avoid_count"]
    for idx in range(timesteps):
        frames.append(
            {
                "map": np.zeros((4, 4, 1), dtype=np.float32),
                "features": np.ones(len(feature_names), dtype=np.float32) * idx,
                "action_id": idx % 2,
                "rewards": [float(rewards[idx])],
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
    sample_path = output_dir / f"{stem}.npz"
    meta_path = output_dir / f"{stem}.json"
    np.savez(
        sample_path,
        map=sample.map,
        features=sample.features,
        actions=sample.actions,
        old_log_probs=sample.old_log_probs,
        value_preds=sample.value_preds,
        rewards=sample.rewards,
        dones=sample.dones,
    )
    meta_path.write_text(json.dumps(sample.metadata, indent=2))


def test_curate_trajectories(tmp_path: Path) -> None:
    captures = tmp_path / "captures"
    captures.mkdir()
    # sample A: timesteps 10, reward sum 5
    _write_sample(captures, "sample_a", np.full(10, 0.5, dtype=np.float32), timesteps=10)
    # sample B: timesteps 5, reward sum 1
    _write_sample(captures, "sample_b", np.full(5, 0.2, dtype=np.float32), timesteps=5)

    manifest_path = tmp_path / "manifest.json"
    module = runpy.run_path("scripts/curate_trajectories.py")
    main = module["main"]
    main([
        str(captures),
        "--output",
        str(manifest_path),
        "--min-timesteps",
        "8",
        "--min-reward",
        "3.0",
    ])

    manifest = json.loads(manifest_path.read_text())
    assert len(manifest) == 2
    accepted = [entry for entry in manifest if entry["accepted"]]
    rejected = [entry for entry in manifest if not entry["accepted"]]
    assert len(accepted) == 1
    assert len(rejected) == 1
    assert Path(accepted[0]["sample"]).name.startswith("sample_a")
    assert Path(rejected[0]["sample"]).name.startswith("sample_b")

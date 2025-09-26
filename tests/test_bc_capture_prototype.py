from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from townlet.policy.replay import frames_to_replay_sample, load_replay_sample


def test_synthetic_bc_capture_round_trip(tmp_path: Path) -> None:
    map_frame = np.zeros((4, 4, 1), dtype=np.float32)
    feature_names = [f"f{i}" for i in range(8)] + ["rivalry_max", "rivalry_avoid_count"]
    feature_vec = np.linspace(0.0, 1.0, num=len(feature_names), dtype=np.float32)
    frames = []
    for step in range(3):
        frames.append(
            {
                "map": map_frame,
                "features": feature_vec + step * 0.1,
                "action_id": step % 2,
                "log_prob": -0.25 * (step + 1),
                "rewards": [0.05 * step],
                "dones": [step == 2],
                "value_pred": 0.2 - 0.05 * step,
                "metadata": {
                    "agent_id": "synthetic_agent",
                    "trajectory_id": "bc_prototype",
                    "feature_names": feature_names,
                    "map_shape": [4, 4, 1],
                },
            }
        )

    sample = frames_to_replay_sample(frames)
    assert sample.map.shape == (3, 4, 4, 1)
    assert sample.features.shape == (3, len(feature_names))
    assert sample.actions.tolist() == [0, 1, 0]
    assert sample.dones.tolist() == [False, False, True]
    assert sample.metadata["timesteps"] == 3
    assert sample.metadata["action_dim"] == 2

    output_dir = tmp_path / "synthetic_bc"
    output_dir.mkdir()
    sample_path = output_dir / "bc_prototype.npz"
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
    meta_path = output_dir / "bc_prototype.json"
    meta_path.write_text(json.dumps(sample.metadata, indent=2))

    reloaded = load_replay_sample(sample_path, meta_path)
    np.testing.assert_allclose(reloaded.map, sample.map)
    np.testing.assert_allclose(reloaded.features, sample.features)
    assert reloaded.actions.tolist() == sample.actions.tolist()
    assert reloaded.metadata["timesteps"] == 3
    assert reloaded.metadata["action_dim"] == 2

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from townlet.policy import BCTrainer, BCTrainingConfig, BCTrajectoryDataset
from townlet.policy.models import ConflictAwarePolicyConfig, torch_available
from townlet.policy.replay import frames_to_replay_sample


@pytest.mark.skipif(not torch_available(), reason="Torch not installed")
def test_bc_trainer_overfits_toy_dataset(tmp_path: Path) -> None:
    feature_names = [f"f{i}" for i in range(4)] + ["rivalry_max", "rivalry_avoid_count"]
    samples = []
    for action in range(2):
        frames = []
        for _ in range(4):
            features = np.zeros(len(feature_names), dtype=np.float32)
            features[0] = float(action)
            frame = {
                "map": np.zeros((4, 4, 1), dtype=np.float32),
                "features": features,
                "action_id": action,
                "rewards": [1.0],
                "dones": [False],
                "value_pred": 0.0,
                "metadata": {
                    "feature_names": feature_names,
                    "trajectory_id": f"toy_{action}",
                    "agent_id": "agent",
                },
            }
            frames.append(frame)
        samples.append(frames_to_replay_sample(frames))

    dataset = BCTrajectoryDataset(samples)
    policy_cfg = ConflictAwarePolicyConfig(
        feature_dim=len(feature_names), map_shape=(1, 4, 4), action_dim=2
    )
    trainer = BCTrainer(
        BCTrainingConfig(learning_rate=0.05, batch_size=4, epochs=50), policy_cfg
    )
    metrics = trainer.fit(dataset)
    assert metrics["accuracy"] >= 0.95


@pytest.mark.skipif(not torch_available(), reason="Torch not installed")
def test_bc_evaluate_accuracy(tmp_path: Path) -> None:
    feature_names = [f"f{i}" for i in range(4)] + ["rivalry_max", "rivalry_avoid_count"]
    frames = []
    for idx in range(3):
        features = np.zeros(len(feature_names), dtype=np.float32)
        features[0] = float(idx % 2)
        frames.append(
            {
                "map": np.zeros((4, 4, 1), dtype=np.float32),
                "features": features,
                "action_id": idx % 2,
                "rewards": [0.0],
                "dones": [False],
                "value_pred": 0.0,
                "metadata": {
                    "feature_names": feature_names,
                    "trajectory_id": "eval",
                    "agent_id": "agent",
                },
            }
        )
    sample = frames_to_replay_sample(frames)
    dataset = BCTrajectoryDataset([sample])
    policy_cfg = ConflictAwarePolicyConfig(
        feature_dim=len(feature_names), map_shape=(1, 4, 4), action_dim=2
    )
    trainer = BCTrainer(
        BCTrainingConfig(learning_rate=0.05, batch_size=2, epochs=30), policy_cfg
    )
    trainer.fit(dataset)
    eval_metrics = trainer.evaluate(dataset)
    assert eval_metrics["accuracy"] >= 0.99

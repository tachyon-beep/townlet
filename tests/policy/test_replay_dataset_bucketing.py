from pathlib import Path

import json
import numpy as np

from townlet.policy.replay import ReplayDataset, ReplayDatasetConfig, TRAINING_ARRAY_FIELDS


def _write_sample(dirpath: Path, stem: str, timesteps: int, feat_dim: int = 4) -> tuple[Path, Path]:
    dirpath.mkdir(parents=True, exist_ok=True)
    map_tensor = np.zeros((timesteps, 3, 4, 4), dtype=np.float32)
    features = np.zeros((timesteps, feat_dim), dtype=np.float32)
    actions = np.zeros((timesteps,), dtype=np.int64)
    old_log_probs = np.zeros((timesteps,), dtype=np.float32)
    rewards = np.zeros((timesteps,), dtype=np.float32)
    dones = np.zeros((timesteps,), dtype=np.bool_)
    value_preds = np.zeros((timesteps + 1,), dtype=np.float32)
    sample_path = dirpath / f"{stem}.npz"
    np.savez_compressed(
        sample_path,
        map=map_tensor,
        features=features,
        actions=actions,
        old_log_probs=old_log_probs,
        value_preds=value_preds,
        rewards=rewards,
        dones=dones,
    )
    meta = {
        "feature_names": ["rivalry_max", "rivalry_avoid_count"],
        "training_arrays": list(TRAINING_ARRAY_FIELDS),
        "timesteps": timesteps,
        "value_pred_steps": timesteps + 1,
        "action_dim": 1,
    }
    meta_path = dirpath / f"{stem}.json"
    meta_path.write_text(json.dumps(meta))
    return sample_path, meta_path


def test_replay_dataset_buckets_by_shape(tmp_path: Path):
    p1, m1 = _write_sample(tmp_path, "s1", 8)
    p2, m2 = _write_sample(tmp_path, "s2", 12)

    cfg = ReplayDatasetConfig(entries=[(p1, m1), (p2, m2)], batch_size=2, shuffle=False)
    ds = ReplayDataset(cfg)
    batches = list(ds)
    # Heterogeneous shapes should yield two batches of size 1
    assert len(batches) == 2
    assert batches[0].actions.shape[0] == 1
    assert batches[1].actions.shape[0] == 1


def test_replay_dataset_buckets_by_shape_streaming(tmp_path: Path):
    p1, m1 = _write_sample(tmp_path, "s1", 6)
    p2, m2 = _write_sample(tmp_path, "s2", 9)

    cfg = ReplayDatasetConfig(
        entries=[(p1, m1), (p2, m2)], batch_size=2, shuffle=False, streaming=True
    )
    ds = ReplayDataset(cfg)
    batches = list(ds)
    assert len(batches) == 2
    assert batches[0].actions.shape[0] == 1
    assert batches[1].actions.shape[0] == 1


import numpy as np

from townlet.policy.replay import TRAINING_ARRAY_FIELDS, ReplaySample
from townlet.policy.replay_buffer import (
    InMemoryReplayDataset,
    InMemoryReplayDatasetConfig,
)


def _make_sample(timesteps: int, feat_dim: int = 4) -> ReplaySample:
    # Map: (T, C, H, W)
    map_tensor = np.zeros((timesteps, 3, 4, 4), dtype=np.float32)
    # Features: (T, D)
    features = np.zeros((timesteps, feat_dim), dtype=np.float32)
    # Step arrays: (T,)
    actions = np.zeros((timesteps,), dtype=np.int64)
    old_log_probs = np.zeros((timesteps,), dtype=np.float32)
    rewards = np.zeros((timesteps,), dtype=np.float32)
    dones = np.zeros((timesteps,), dtype=np.bool_)
    # Value preds: (T + 1,)
    value_preds = np.zeros((timesteps + 1,), dtype=np.float32)
    meta = {
        "feature_names": ["rivalry_max", "rivalry_avoid_count"],
        "training_arrays": list(TRAINING_ARRAY_FIELDS),
        "timesteps": timesteps,
        "value_pred_steps": timesteps + 1,
    }
    return ReplaySample(
        map=map_tensor,
        features=features,
        actions=actions,
        old_log_probs=old_log_probs,
        value_preds=value_preds,
        rewards=rewards,
        dones=dones,
        metadata=meta,
    )


def test_inmemory_dataset_allows_variable_timesteps_with_batch_size_one():
    s1 = _make_sample(8)
    s2 = _make_sample(12)
    dataset = InMemoryReplayDataset(
        InMemoryReplayDatasetConfig(entries=[s1, s2], batch_size=1)
    )
    batches = list(dataset)
    assert len(batches) == 2
    # Ensure each batch corresponds to a single sample with preserved timesteps
    assert batches[0].actions.shape[1] == 8
    assert batches[1].actions.shape[1] == 12


def test_inmemory_dataset_groups_mismatched_timesteps_when_batching():
    s1 = _make_sample(8)
    s2 = _make_sample(12)
    cfg = InMemoryReplayDatasetConfig(entries=[s1, s2], batch_size=2)
    ds = InMemoryReplayDataset(cfg)
    batches = list(ds)
    # Two buckets of size 1 → two batches of size 1
    assert len(batches) == 2
    assert batches[0].actions.shape[0] == 1
    assert batches[1].actions.shape[0] == 1

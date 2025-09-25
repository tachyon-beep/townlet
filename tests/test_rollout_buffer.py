from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from townlet.config import load_config
from townlet.policy.rollout import RolloutBuffer
from townlet.policy.runner import TrainingHarness


def _dummy_frame(agent_id: str) -> dict[str, object]:
    return {
        "agent_id": agent_id,
        "map": np.zeros((1, 1, 1), dtype=np.float32),
        "features": np.zeros(1, dtype=np.float32),
        "metadata": {"feature_names": []},
        "action_id": 0,
        "rewards": [0.0],
        "dones": [False],
    }


def test_rollout_buffer_grouping_to_samples() -> None:
    buffer = RolloutBuffer()
    buffer.extend([_dummy_frame("alice"), _dummy_frame("alice")])
    samples = buffer.to_samples()
    assert set(samples) == {"alice"}
    assert samples["alice"].map.shape[0] == 2


def test_training_harness_capture_rollout(tmp_path: Path) -> None:
    harness = TrainingHarness(load_config(Path("configs/examples/poc_hybrid.yaml")))
    output_dir = tmp_path / "captured"
    buffer = harness.capture_rollout(
        ticks=2,
        auto_seed_agents=True,
        output_dir=output_dir,
        prefix="test_rollout",
        compress=False,
    )
    assert len(buffer) > 0
    manifest = output_dir / "test_rollout_manifest.json"
    metrics = output_dir / "test_rollout_metrics.json"
    assert manifest.exists()
    assert metrics.exists()
    manifest_entries = json.loads(manifest.read_text())
    metrics_map = json.loads(metrics.read_text())
    assert manifest_entries
    assert metrics_map
    for entry in manifest_entries:
        sample_path = output_dir / entry["sample"]
        meta_path = output_dir / entry["meta"]
        assert sample_path.exists()
        assert meta_path.exists()

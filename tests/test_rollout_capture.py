from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pytest

from townlet.config import load_config

SCENARIO_CONFIGS = [
    Path("configs/scenarios/kitchen_breakfast.yaml"),
    Path("configs/scenarios/queue_conflict.yaml"),
    Path("configs/scenarios/employment_punctuality.yaml"),
    Path("configs/scenarios/rivalry_decay.yaml"),
    Path("configs/scenarios/observation_baseline.yaml"),
]

GOLDEN_STATS_PATH = Path("docs/samples/rollout_scenario_stats.json")
GOLDEN_STATS = (
    json.loads(GOLDEN_STATS_PATH.read_text()) if GOLDEN_STATS_PATH.exists() else {}
)


@pytest.mark.parametrize("config_path", SCENARIO_CONFIGS)
def test_capture_rollout_scenarios(tmp_path: Path, config_path: Path) -> None:
    output_dir = tmp_path / config_path.stem
    output_dir.mkdir()
    load_config(config_path)

    import subprocess

    subprocess.run(
        [
            sys.executable,
            "scripts/capture_rollout.py",
            str(config_path),
            "--output",
            str(output_dir),
            "--compress",
        ],
        check=True,
    )

    npz_files = sorted(output_dir.glob("*.npz"))
    assert npz_files, "No replay samples generated"

    for npz_path in npz_files:
        data = np.load(npz_path)
        for key in (
            "map",
            "features",
            "actions",
            "old_log_probs",
            "value_preds",
            "rewards",
            "dones",
        ):
            assert key in data, f"missing {key} in {npz_path.name}"
        assert np.isfinite(data["old_log_probs"]).all()
        assert np.isfinite(data["value_preds"]).all()
        assert data["map"].ndim == 4  # (timesteps, channels, h, w)
        assert data["features"].ndim == 2  # (timesteps, feature_dim)
        assert data["actions"].ndim == 1

    manifest = output_dir / "rollout_sample_manifest.json"
    assert manifest.exists()
    manifest_payload = json.loads(manifest.read_text())
    if isinstance(manifest_payload, dict):
        manifest_metadata = manifest_payload.get("metadata", {})
        entries = manifest_payload.get("samples", [])
    else:
        manifest_metadata = {}
        entries = manifest_payload
    assert entries, "Manifest empty"
    if manifest_metadata:
        expected_config = load_config(config_path).config_id
        assert manifest_metadata.get("config_id") == expected_config
        assert manifest_metadata.get("scenario_name") == config_path.stem
    for entry in entries:
        assert "sample" in entry and "meta" in entry
        sample_file = output_dir / entry["sample"]
        assert sample_file.exists()

    metrics_file = output_dir / "rollout_sample_metrics.json"
    assert metrics_file.exists()
    metrics_payload = json.loads(metrics_file.read_text())
    assert metrics_payload, "Metrics file empty"
    if isinstance(metrics_payload, dict) and "samples" in metrics_payload:
        metrics_data = metrics_payload.get("samples", {})
    else:
        metrics_data = metrics_payload

    golden = GOLDEN_STATS.get(config_path.stem)
    if golden:
        for npz_path in npz_files:
            name = npz_path.name
            metrics = golden.get(name)
            assert metrics is not None, f"Missing golden metrics for {name}"
            data = np.load(npz_path)
            assert int(data["rewards"].shape[0]) == metrics["timesteps"]
            assert np.isclose(float(data["rewards"].sum()), metrics["reward_sum"])
            assert np.isclose(
                float(data["old_log_probs"].mean()), metrics["log_prob_mean"]
            )
            sample_metrics = metrics_data.get(name)
            assert sample_metrics is not None
            assert np.isclose(sample_metrics["reward_sum"], metrics["reward_sum"])

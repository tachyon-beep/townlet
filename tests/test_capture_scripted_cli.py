from pathlib import Path

import json

import runpy

from townlet.policy.replay import load_replay_sample


def test_capture_scripted_idle(tmp_path: Path) -> None:
    output_dir = tmp_path / "captures"
    module = runpy.run_path("scripts/capture_scripted.py")
    main = module["main"]
    main([
        "configs/examples/poc_hybrid.yaml",
        "--scenario",
        "idle",
        "--ticks",
        "5",
        "--output",
        str(output_dir),
    ])

    npz_files = sorted(output_dir.glob("*.npz"))
    json_files = sorted(output_dir.glob("*.json"))
    assert npz_files and json_files
    for npz_path, json_path in zip(npz_files, json_files):
        sample = load_replay_sample(npz_path, json_path)
        metadata = sample.metadata
        assert metadata["scenario"] == "idle"
        assert metadata["quality_metrics"]["reward_sum"] == metadata["quality_metrics"]["reward_sum"]
        assert "feature_names" in metadata
        # ensure tags default to scenario
        assert metadata["tags"] == ["idle"]
        # basic shape sanity
        assert sample.map.shape[0] == metadata["timesteps"]

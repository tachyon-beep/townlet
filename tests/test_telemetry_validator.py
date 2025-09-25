from __future__ import annotations

from pathlib import Path

import json
import pytest

from scripts.validate_ppo_telemetry import validate_logs


VALID_RECORD = {
    "epoch": 1.0,
    "updates": 2.0,
    "transitions": 4.0,
    "loss_policy": 0.1,
    "loss_value": 0.2,
    "loss_entropy": 0.3,
    "loss_total": 0.4,
    "clip_fraction": 0.1,
    "adv_mean": 0.0,
    "adv_std": 0.1,
    "grad_norm": 1.5,
    "kl_divergence": 0.01,
    "telemetry_version": 1.0,
    "lr": 0.0003,
    "steps": 4.0,
    "baseline_sample_count": 2.0,
    "baseline_reward_mean": 0.25,
    "baseline_reward_sum": 1.0,
    "baseline_reward_sum_mean": 0.5,
    "baseline_log_prob_mean": -0.2,
    "conflict.rivalry_max_mean_avg": 0.05,
    "conflict.rivalry_max_max_avg": 0.1,
    "conflict.rivalry_avoid_count_mean_avg": 0.0,
    "conflict.rivalry_avoid_count_max_avg": 0.0,
}


def _write_ndjson(path: Path, record: dict[str, float]) -> None:
    path.write_text(json.dumps(record) + "\n")


def test_validate_ppo_telemetry_accepts_valid_log(tmp_path: Path) -> None:
    log_path = tmp_path / "ppo_log.jsonl"
    baseline_path = tmp_path / "baseline.json"

    _write_ndjson(log_path, VALID_RECORD)
    baseline_payload = {
        "baseline_reward_sum": 1.0,
        "baseline_reward_mean": 0.25,
        "baseline_sample_count": 2.0,
        "baseline_reward_sum_mean": 0.5,
        "baseline_log_prob_mean": -0.2,
    }
    baseline_path.write_text(json.dumps(baseline_payload))

    # Should not raise; include relative drift for coverage.
    validate_logs([log_path], baseline_path, drift_threshold=None, include_relative=True)


def test_validate_ppo_telemetry_raises_for_missing_conflict(tmp_path: Path) -> None:
    log_path = tmp_path / "ppo_invalid.jsonl"
    invalid_record = {key: value for key, value in VALID_RECORD.items() if not key.startswith("conflict.")}
    _write_ndjson(log_path, invalid_record)

    with pytest.raises(ValueError, match="missing conflict telemetry keys"):
        validate_logs([log_path], baseline_path=None, drift_threshold=None, include_relative=False)


def test_validate_ppo_telemetry_accepts_version_1_1(tmp_path: Path) -> None:
    log_path = tmp_path / "ppo_v1_1.jsonl"
    record_v1_1 = {
        **VALID_RECORD,
        "telemetry_version": 1.1,
        "epoch_duration_sec": 0.5,
        "data_mode": "replay",
        "cycle_id": 0.0,
        "batch_entropy_mean": 0.05,
        "batch_entropy_std": 0.01,
        "grad_norm_max": 1.6,
        "kl_divergence_max": 0.02,
        "reward_advantage_corr": 0.9,
        "rollout_ticks": 0.0,
        "log_stream_offset": 1.0,
    }
    _write_ndjson(log_path, record_v1_1)

    validate_logs([log_path], baseline_path=None, drift_threshold=None, include_relative=False)


def test_validate_ppo_telemetry_v1_1_missing_field_raises(tmp_path: Path) -> None:
    log_path = tmp_path / "ppo_v1_1_invalid.jsonl"
    record_v1_1 = {
        **VALID_RECORD,
        "telemetry_version": 1.1,
        "data_mode": "replay",
        # Missing required numeric fields such as epoch_duration_sec.
    }
    _write_ndjson(log_path, record_v1_1)

    with pytest.raises(ValueError, match="requires numeric keys"):
        validate_logs([log_path], baseline_path=None, drift_threshold=None, include_relative=False)

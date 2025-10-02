"""Validate PPO telemetry NDJSON logs and report baseline drift."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable, List

BASE_REQUIRED_KEYS = {
    "epoch",
    "updates",
    "transitions",
    "loss_policy",
    "loss_value",
    "loss_entropy",
    "loss_total",
    "clip_fraction",
    "clip_fraction_max",
    "clip_triggered_minibatches",
    "adv_mean",
    "adv_std",
    "adv_zero_std_batches",
    "adv_min_std",
    "grad_norm",
    "kl_divergence",
    "telemetry_version",
    "lr",
    "steps",
}

CONFLICT_KEYS = {
    "conflict.rivalry_max_mean_avg",
    "conflict.rivalry_max_max_avg",
    "conflict.rivalry_avoid_count_mean_avg",
    "conflict.rivalry_avoid_count_max_avg",
}

BASELINE_KEYS = {
    "baseline_sample_count",
    "baseline_reward_mean",
    "baseline_reward_sum",
    "baseline_reward_sum_mean",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate PPO telemetry NDJSON logs")
    parser.add_argument("logs", nargs="+", type=Path, help="One or more NDJSON log files")
    parser.add_argument(
        "--baseline",
        type=Path,
        help="Optional JSON file containing baseline metrics (reward_sum, reward_mean, etc.)",
    )
    parser.add_argument(
        "--drift-threshold",
        type=float,
        default=None,
        help="Fail if absolute drift between log and baseline exceeds this value",
    )
    parser.add_argument(
        "--relative",
        action="store_true",
        help="Include relative (percentage) drift when baseline values are non-zero",
    )
    return parser.parse_args()


def _ensure_numeric(key: str, value: object) -> None:
    if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ValueError(f"Field '{key}' must be a finite number, got {value!r}")


def _load_records(path: Path) -> List[dict[str, object]]:
    records: List[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as err:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {err}") from err
        if not isinstance(payload, dict):
            raise ValueError(f"{path}:{line_number}: expected JSON object, got {type(payload).__name__}")
        records.append(payload)
    if not records:
        raise ValueError(f"{path}: no telemetry records found")
    return records


REQUIRED_V1_1_NUMERIC_KEYS = {
    "epoch_duration_sec",
    "cycle_id",
    "batch_entropy_mean",
    "batch_entropy_std",
    "grad_norm_max",
    "kl_divergence_max",
    "reward_advantage_corr",
    "rollout_ticks",
    "log_stream_offset",
    "queue_conflict_events",
    "queue_conflict_intensity_sum",
}

REQUIRED_V1_1_STRING_KEYS = {"data_mode"}


def _validate_record(record: dict[str, object], source: Path) -> None:
    version_value = record.get("telemetry_version")
    _ensure_numeric("telemetry_version", version_value)
    version = float(version_value)

    missing = BASE_REQUIRED_KEYS - record.keys()
    if missing:
        raise ValueError(f"{source}: missing required telemetry keys: {sorted(missing)}")

    for key in BASE_REQUIRED_KEYS:
        _ensure_numeric(key, record[key])

    conflict_missing = CONFLICT_KEYS - record.keys()
    if conflict_missing:
        raise ValueError(f"{source}: missing conflict telemetry keys: {sorted(conflict_missing)}")
    for key in CONFLICT_KEYS:
        _ensure_numeric(key, record[key])

    if version >= 1.1:
        numeric_missing = REQUIRED_V1_1_NUMERIC_KEYS - record.keys()
        if numeric_missing:
            raise ValueError(
                f"{source}: telemetry_version 1.1 requires numeric keys: {sorted(numeric_missing)}"
            )
        for key in REQUIRED_V1_1_NUMERIC_KEYS:
            _ensure_numeric(key, record[key])
        string_missing = REQUIRED_V1_1_STRING_KEYS - record.keys()
        if string_missing:
            raise ValueError(
                f"{source}: telemetry_version 1.1 requires string keys: {sorted(string_missing)}"
            )
        for key in REQUIRED_V1_1_STRING_KEYS:
            if not isinstance(record[key], str):
                raise ValueError(f"{source}: field '{key}' must be a string")
    else:
        unexpected_v1_1 = REQUIRED_V1_1_NUMERIC_KEYS & record.keys()
        if unexpected_v1_1:
            raise ValueError(
                f"{source}: telemetry_version {version} should not include v1.1-only keys: {sorted(unexpected_v1_1)}"
            )

    baseline_present = BASELINE_KEYS <= record.keys()
    if baseline_present:
        for key in BASELINE_KEYS:
            _ensure_numeric(key, record[key])
        if "baseline_log_prob_mean" in record:
            _ensure_numeric("baseline_log_prob_mean", record["baseline_log_prob_mean"])


def _load_baseline(path: Path | None) -> dict[str, float] | None:
    if path is None:
        return None
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("Baseline file must contain a JSON object")
    baseline: dict[str, float] = {}
    for key in (*BASELINE_KEYS, "baseline_log_prob_mean"):
        if key in data:
            value = data[key]
            _ensure_numeric(key, value)
            baseline[key] = float(value)
    if not baseline:
        raise ValueError("Baseline file does not provide recognised baseline_* keys")
    return baseline


def _relative_delta(delta: float, base_value: float) -> float | None:
    if base_value == 0.0:
        return None
    return (delta / base_value) * 100.0


def _report_drift(
    records: list[dict[str, object]],
    baseline: dict[str, float],
    threshold: float | None,
    include_relative: bool,
) -> None:
    overlapping_keys = [key for key in baseline if any(key in record for record in records)]
    if not overlapping_keys:
        print("No overlapping baseline keys found; skipping drift report.")
        return

    header = ["epoch"] + overlapping_keys
    if include_relative:
        header.extend(f"{key}%" for key in overlapping_keys)
    print("\nBaseline drift summary (log - baseline):")
    print("  " + " | ".join(f"{h:>20}" for h in header))

    exceeded: dict[str, float] = {}
    max_delta: dict[str, float] = {key: 0.0 for key in overlapping_keys}

    for record in records:
        deltas = {key: float(record[key]) - float(baseline[key]) for key in overlapping_keys if key in record}
        row = [f"{int(record['epoch']):>20}"]
        for key in overlapping_keys:
            delta = deltas.get(key, 0.0)
            row.append(f"{delta:+.6f}")
            if abs(delta) > abs(max_delta[key]):
                max_delta[key] = delta
            if threshold is not None and abs(delta) > threshold:
                exceeded[key] = delta
        if include_relative:
            for key in overlapping_keys:
                delta = deltas.get(key, 0.0)
                rel = _relative_delta(delta, baseline[key])
                row.append("    n/a    " if rel is None else f"{rel:+.2f}%")
        print("  " + " | ".join(f"{value:>20}" for value in row))

    print("\n  Worst absolute drift by key:")
    for key in overlapping_keys:
        print(f"    {key}: {max_delta[key]:+.6f}")

    if threshold is not None and exceeded:
        pairs = ", ".join(f"{key}={delta:+.6f}" for key, delta in exceeded.items())
        raise ValueError(f"Baseline drift exceeds threshold {threshold}: {pairs}")


def validate_logs(
    paths: Iterable[Path],
    baseline_path: Path | None,
    drift_threshold: float | None,
    include_relative: bool,
) -> None:
    baseline = _load_baseline(baseline_path)
    for log_path in paths:
        records = _load_records(log_path)
        for record in records:
            _validate_record(record, log_path)
        print(f"{log_path}: {len(records)} record(s) validated.")
        if baseline is not None:
            _report_drift(records, baseline, drift_threshold, include_relative)


def main() -> None:
    args = parse_args()
    validate_logs(args.logs, args.baseline, args.drift_threshold, args.relative)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""Evaluate promotion gate metrics from summary artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BC_THRESHOLD_DEFAULT = 0.9
LOSS_TOLERANCE = 0.1  # +/- 10%


def _load_json(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


def evaluate(summary_path: Path, watch_path: Path | None = None) -> tuple[str, list[str]]:
    reasons: list[str] = []
    summary = _load_json(summary_path)

    bc_accuracy = float(summary.get("bc_accuracy", 0.0))
    bc_threshold = float(summary.get("bc_threshold", BC_THRESHOLD_DEFAULT))
    if bc_accuracy < bc_threshold:
        reasons.append(f"bc_accuracy {bc_accuracy:.3f} below threshold {bc_threshold:.3f}")

    ppo_loss = summary.get("ppo_loss_total")
    loss_baseline = summary.get("ppo_loss_baseline")
    if (
        isinstance(ppo_loss, (int, float))
        and isinstance(loss_baseline, (int, float))
        and loss_baseline != 0
    ):
        deviation = abs(float(ppo_loss) - float(loss_baseline)) / abs(float(loss_baseline))
        if deviation > LOSS_TOLERANCE:
            reasons.append(
                f"ppo_loss_total drift {deviation:.2%} exceeds tolerance {LOSS_TOLERANCE:.0%}"
            )

    if watch_path is not None and watch_path.exists():
        for line in watch_path.read_text().splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict) and record.get("status") == "fail":
                reasons.append("telemetry_watch reported fail status")
                break

    status = "pass" if not reasons else "fail"
    return status, reasons


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate promotion gate metrics")
    parser.add_argument("--summary", type=Path, required=True, help="Path to anneal summary JSON")
    parser.add_argument(
        "--watch",
        type=Path,
        help="Optional telemetry watch JSONL file for additional checks",
    )
    args = parser.parse_args(argv)

    summary_path: Path = args.summary.expanduser()
    if not summary_path.exists():
        print(f"Summary file not found: {summary_path}", file=sys.stderr)
        return 2

    watch_path = args.watch.expanduser() if args.watch else None
    status, reasons = evaluate(summary_path, watch_path)
    report = {"status": status, "summary": str(summary_path)}
    if watch_path is not None:
        report["watch"] = str(watch_path)
    if reasons:
        report["reasons"] = reasons
    print(json.dumps(report, indent=2))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

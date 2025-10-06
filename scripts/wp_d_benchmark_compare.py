#!/usr/bin/env python3
"""Compare a current benchmark result against a baseline and print deltas.

Usage:
  python scripts/wp_d_benchmark_compare.py --current tmp/wp-d/benchmarks/benchmark_X.json \
      --baseline tmp/wp-d/benchmarks/benchmark_baseline.json --out tmp/wp-d/benchmarks/compare.txt
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from townlet.benchmark.utils import compare_benchmarks, load_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WP-D benchmark comparer")
    parser.add_argument("--current", type=Path, required=True, help="Current benchmark JSON path")
    parser.add_argument("--baseline", type=Path, required=True, help="Baseline benchmark JSON path")
    parser.add_argument("--out", type=Path, default=None, help="Optional text file to write summary")
    return parser.parse_args()


def _format_summary(current: dict[str, Any], baseline: dict[str, Any], deltas: dict[str, Any]) -> str:
    lines: list[str] = []
    header = (
        f"current={current.get('config_id')} avg={current.get('avg_tick_seconds')} "
        f"baseline={baseline.get('config_id')} avg={baseline.get('avg_tick_seconds')}"
    )
    lines.append(header)
    keys = [
        "dropped_messages",
        "queue_length_peak",
        "worker_restart_count",
        "bytes_flushed_total",
        "payloads_flushed_total",
        "send_failures_total",
    ]
    for k in keys:
        lines.append(
            f"{k}: curr={deltas.get(k)} base={deltas.get(k + '_baseline')} delta={deltas.get(k + '_delta')}"
        )
    lines.append(f"avg_tick_seconds_delta={deltas.get('avg_tick_seconds_delta')}")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    current = load_benchmark(args.current)
    baseline = load_benchmark(args.baseline)
    deltas = compare_benchmarks(current, baseline)
    summary = _format_summary(current, baseline, deltas)
    print(summary)
    if args.out is not None:
        path = Path(args.out).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(summary + "\n" + json.dumps(deltas, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


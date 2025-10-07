#!/usr/bin/env python3
"""Record a WP-D benchmark run and write JSON to tmp/wp-d/benchmarks/.

Usage:
  python scripts/wp_d_benchmark.py --config configs/examples/poc_hybrid.yaml --ticks 500 \
      --telemetry-provider stdout --notes "baseline"
"""

from __future__ import annotations

import argparse
from pathlib import Path

from townlet.benchmark.utils import run_benchmark, write_benchmark_result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WP-D benchmark recorder")
    parser.add_argument("--config", type=Path, required=True, help="Path to config file")
    parser.add_argument("--ticks", type=int, default=500, help="Tick count to run")
    parser.add_argument("--telemetry-provider", type=str, default=None, help="Override telemetry provider (default from config)")
    parser.add_argument("--notes", type=str, default=None, help="Optional notes to embed in the result")
    parser.add_argument("--outfile", type=Path, default=None, help="Optional output path for JSON result")
    parser.add_argument(
        "--override",
        action="append",
        default=None,
        help="Override config via dotted path (e.g., telemetry.transport.type=file). Can be repeated.",
    )
    # Sweep options (optional)
    parser.add_argument("--sweep", action="store_true", help="Run a parameter sweep and write a CSV report")
    parser.add_argument("--sweep-batch", type=str, default=None, help="Comma-separated max_batch_size values (e.g., 16,32,64)")
    parser.add_argument("--sweep-flush", type=str, default=None, help="Comma-separated flush_interval_ticks values (e.g., 1,2,4)")
    parser.add_argument("--sweep-poll", type=str, default=None, help="Comma-separated worker_poll_seconds values (e.g., 0.25,0.5,1.0)")
    parser.add_argument("--sweep-out", type=Path, default=None, help="CSV output path for sweep results")
    return parser.parse_args()


def _parse_list(value: str | None, coerce):
    if not value:
        return None
    items = []
    for chunk in value.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        items.append(coerce(chunk))
    return items or None


def _sweep(args: argparse.Namespace) -> None:
    batch_list = _parse_list(args.sweep_batch, int) or [16, 32]
    flush_list = _parse_list(args.sweep_flush, int) or [1, 2]
    poll_list = _parse_list(args.sweep_poll, float) or [0.5, 1.0]
    rows = []
    for batch in batch_list:
        for flush in flush_list:
            for poll in poll_list:
                result = run_benchmark(
                    config_path=args.config,
                    ticks=args.ticks,
                    telemetry_provider=args.telemetry_provider,
                    notes=f"sweep batch={batch} flush={flush} poll={poll}",
                    overrides={
                        "telemetry.transport.buffer.max_batch_size": batch,
                        "telemetry.transport.buffer.flush_interval_ticks": flush,
                        "telemetry.transport.worker_poll_seconds": poll,
                    },
                )
                tx = result.transport
                rows.append(
                    {
                        "batch": batch,
                        "flush": flush,
                        "poll": poll,
                        "avg_tick_seconds": result.avg_tick_seconds,
                        "dropped_messages": tx.get("dropped_messages", 0),
                        "queue_length_peak": tx.get("queue_length_peak", 0),
                        "last_flush_ms": tx.get("last_flush_duration_ms"),
                        "payloads_flushed_total": tx.get("payloads_flushed_total", 0),
                        "bytes_flushed_total": tx.get("bytes_flushed_total", 0),
                        "worker_restart_count": tx.get("worker_restart_count", 0),
                        "send_failures_total": tx.get("send_failures_total", 0),
                    }
                )
    # Write CSV
    import csv, time as _t

    out = args.sweep_out
    if out is None:
        root = Path("tmp/wp-d/benchmarks").resolve()
        root.mkdir(parents=True, exist_ok=True)
        out = root / f"sweep_{int(_t.time())}.csv"
    else:
        out = Path(out).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "batch",
                "flush",
                "poll",
                "avg_tick_seconds",
                "dropped_messages",
                "queue_length_peak",
                "last_flush_ms",
                "payloads_flushed_total",
                "bytes_flushed_total",
                "worker_restart_count",
                "send_failures_total",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(out)


def main() -> None:
    args = parse_args()
    if args.sweep:
        _sweep(args)
        return
    # Build overrides mapping if provided
    overrides = None
    if args.override:
        overrides = {}
        for item in args.override:
            if not item or "=" not in item:
                continue
            key, value = item.split("=", 1)
            k = key.strip()
            v: object = value.strip()
            if k.endswith("file_path"):
                from pathlib import Path as _P
                v = _P(str(v))
            overrides[k] = v
    result = run_benchmark(
        config_path=args.config,
        ticks=args.ticks,
        telemetry_provider=args.telemetry_provider,
        notes=args.notes,
        overrides=overrides,
    )
    out = write_benchmark_result(result, args.outfile)
    print(out)


if __name__ == "__main__":
    main()

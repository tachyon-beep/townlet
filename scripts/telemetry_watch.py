"""Tail PPO telemetry logs and alert on metric thresholds."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Iterator

REQUIRED_KEYS = {
    "epoch",
    "loss_total",
    "kl_divergence",
    "grad_norm",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Watch PPO telemetry logs for regressions")
    parser.add_argument("log", type=Path, help="Path to NDJSON PPO telemetry log")
    parser.add_argument("--follow", action="store_true", help="Continuously watch for new entries")
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Polling interval in seconds when --follow is enabled (default: 2.0)",
    )
    parser.add_argument(
        "--kl-threshold",
        type=float,
        default=None,
        help="Fail if kl_divergence exceeds this value",
    )
    parser.add_argument(
        "--loss-threshold",
        type=float,
        default=None,
        help="Fail if loss_total exceeds this value",
    )
    parser.add_argument(
        "--grad-threshold",
        type=float,
        default=None,
        help="Fail if grad_norm exceeds this value",
    )
    return parser.parse_args()


def stream_records(path: Path, follow: bool, interval: float) -> Iterator[dict[str, float]]:
    while not path.exists():
        if not follow:
            raise FileNotFoundError(path)
        time.sleep(interval)

    with path.open("r", encoding="utf-8") as handle:
        while True:
            position = handle.tell()
            line = handle.readline()
            if not line:
                if follow:
                    handle.seek(position)
                    time.sleep(interval)
                    continue
                break
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"{path}: expected JSON object, got {type(payload).__name__}")
            missing = REQUIRED_KEYS - payload.keys()
            if missing:
                raise ValueError(f"{path}: telemetry record missing keys: {sorted(missing)}")
            yield {key: float(payload[key]) for key in REQUIRED_KEYS}


def check_thresholds(record: dict[str, float], args: argparse.Namespace) -> None:
    epoch = int(record["epoch"])
    if args.kl_threshold is not None and record["kl_divergence"] > args.kl_threshold:
        raise SystemExit(
            f"Epoch {epoch}: kl_divergence {record['kl_divergence']:.6f} exceeds threshold {args.kl_threshold}"
        )
    if args.loss_threshold is not None and record["loss_total"] > args.loss_threshold:
        raise SystemExit(
            f"Epoch {epoch}: loss_total {record['loss_total']:.6f} exceeds threshold {args.loss_threshold}"
        )
    if args.grad_threshold is not None and record["grad_norm"] > args.grad_threshold:
        raise SystemExit(
            f"Epoch {epoch}: grad_norm {record['grad_norm']:.6f} exceeds threshold {args.grad_threshold}"
        )


def main() -> None:
    args = parse_args()
    try:
        for record in stream_records(args.log, args.follow, args.interval):
            check_thresholds(record, args)
            print(
                f"Epoch {int(record['epoch'])}: loss_total={record['loss_total']:.6f}, "
                f"kl_divergence={record['kl_divergence']:.6f}, grad_norm={record['grad_norm']:.6f}"
            )
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

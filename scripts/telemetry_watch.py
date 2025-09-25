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
    "batch_entropy_mean",
    "reward_advantage_corr",
    "log_stream_offset",
    "data_mode",
    "queue_conflict_events",
    "queue_conflict_intensity_sum",
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
    parser.add_argument(
        "--entropy-threshold",
        type=float,
        default=None,
        help="Fail if batch_entropy_mean drops below this value",
    )
    parser.add_argument(
        "--reward-corr-threshold",
        type=float,
        default=None,
        help="Fail if reward_advantage_corr falls below this value",
    )
    parser.add_argument(
        "--queue-events-min",
        type=float,
        default=None,
        help="Fail if queue_conflict_events falls below this value",
    )
    parser.add_argument(
        "--queue-intensity-min",
        type=float,
        default=None,
        help="Fail if queue_conflict_intensity_sum falls below this value",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON lines instead of human-readable text",
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
            record = {
                key: float(payload[key])
                for key in REQUIRED_KEYS
                if key not in {"data_mode"}
            }
            record["data_mode"] = str(payload["data_mode"])
            yield record


def check_thresholds(record: dict[str, object], args: argparse.Namespace) -> None:
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
    if args.entropy_threshold is not None and record["batch_entropy_mean"] < args.entropy_threshold:
        raise SystemExit(
            f"Epoch {epoch}: batch_entropy_mean {record['batch_entropy_mean']:.6f} below threshold {args.entropy_threshold}"
        )
    if args.reward_corr_threshold is not None and record["reward_advantage_corr"] < args.reward_corr_threshold:
        raise SystemExit(
            f"Epoch {epoch}: reward_advantage_corr {record['reward_advantage_corr']:.6f} below threshold {args.reward_corr_threshold}"
        )
    is_rollout = record["data_mode"] == "rollout"
    if args.queue_events_min is not None and is_rollout:
        if record["queue_conflict_events"] < args.queue_events_min:
            raise SystemExit(
                f"Epoch {epoch}: queue_conflict_events {record['queue_conflict_events']:.1f} below threshold {args.queue_events_min}"
            )
    if args.queue_intensity_min is not None and is_rollout:
        if record["queue_conflict_intensity_sum"] < args.queue_intensity_min:
            raise SystemExit(
                f"Epoch {epoch}: queue_conflict_intensity_sum {record['queue_conflict_intensity_sum']:.2f} below threshold {args.queue_intensity_min}"
            )


def main() -> None:
    args = parse_args()
    try:
        for record in stream_records(args.log, args.follow, args.interval):
            check_thresholds(record, args)
            if args.json:
                import json

                print(json.dumps(record))
            else:
                print(
                    f"Epoch {int(record['epoch'])} ({record['data_mode']}): "
                    f"loss_total={record['loss_total']:.6f}, "
                    f"kl_divergence={record['kl_divergence']:.6f}, "
                    f"grad_norm={record['grad_norm']:.6f}, "
                    f"entropy_mean={record['batch_entropy_mean']:.6f}, "
                    f"reward_adv_corr={record['reward_advantage_corr']:.6f}, "
                    f"queue_events={record['queue_conflict_events']:.1f}, "
                    f"queue_intensity_sum={record['queue_conflict_intensity_sum']:.2f}, "
                    f"offset={record['log_stream_offset']:.0f}"
                )
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

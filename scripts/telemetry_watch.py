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
    "shared_meal_events",
    "late_help_events",
    "shift_takeover_events",
    "chat_success_events",
    "chat_failure_events",
    "chat_quality_mean",
}

OPTIONAL_NUMERIC_KEYS = {
    "anneal_cycle",
    "anneal_bc_accuracy",
    "anneal_bc_threshold",
    "anneal_loss_baseline",
    "anneal_queue_baseline",
    "anneal_intensity_baseline",
}

OPTIONAL_BOOL_KEYS = {
    "anneal_bc_passed",
    "anneal_loss_flag",
    "anneal_queue_flag",
    "anneal_intensity_flag",
}

OPTIONAL_TEXT_KEYS = {
    "anneal_stage",
    "anneal_dataset",
}


def build_parser() -> argparse.ArgumentParser:
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
        "--shared-meal-min",
        type=float,
        default=None,
        help="Fail if shared_meal_events falls below this value",
    )
    parser.add_argument(
        "--late-help-min",
        type=float,
        default=None,
        help="Fail if late_help_events falls below this value",
    )
    parser.add_argument(
        "--shift-takeover-max",
        type=float,
        default=None,
        help="Fail if shift_takeover_events exceeds this value",
    )
    parser.add_argument(
        "--chat-quality-min",
        type=float,
        default=None,
        help="Fail if chat_quality_mean falls below this value",
    )
    parser.add_argument(
        "--anneal-bc-min",
        type=float,
        default=0.9,
        help="Fail if anneal_bc_accuracy falls below this value (default: 0.9)",
    )
    parser.add_argument(
        "--anneal-loss-max",
        type=float,
        default=0.1,
        help="Fail if loss_total drifts beyond this fraction of baseline (default: 0.1 for ±10%)",
    )
    parser.add_argument(
        "--anneal-queue-min",
        type=float,
        default=None,
        help="Fail if queue_conflict_events falls below this value during anneal stages (default: baseline × (1 - queue-tolerance))",
    )
    parser.add_argument(
        "--anneal-intensity-min",
        type=float,
        default=None,
        help="Fail if queue_conflict_intensity_sum falls below this value during anneal stages (default: baseline × (1 - queue-tolerance))",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON lines instead of human-readable text",
    )
    return parser


def parse_args() -> argparse.Namespace:
    return build_parser().parse_args()


def parse_args_from_list(argv: list[str]) -> argparse.Namespace:
    return build_parser().parse_args(argv[1:])


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
            for key in OPTIONAL_NUMERIC_KEYS:
                if key in payload:
                    value = payload[key]
                    record[key] = (
                        None
                        if value is None
                        else float(value)
                    )
            for key in OPTIONAL_BOOL_KEYS:
                if key in payload:
                    record[key] = bool(payload[key])
            for key in OPTIONAL_TEXT_KEYS:
                if key in payload:
                    record[key] = str(payload[key])
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
    if args.shared_meal_min is not None and is_rollout:
        if record["shared_meal_events"] < args.shared_meal_min:
            raise SystemExit(
                f"Epoch {epoch}: shared_meal_events {record['shared_meal_events']:.1f} below threshold {args.shared_meal_min}"
            )
    if args.late_help_min is not None and is_rollout:
        if record["late_help_events"] < args.late_help_min:
            raise SystemExit(
                f"Epoch {epoch}: late_help_events {record['late_help_events']:.1f} below threshold {args.late_help_min}"
            )
    if args.shift_takeover_max is not None and is_rollout:
        if record["shift_takeover_events"] > args.shift_takeover_max:
            raise SystemExit(
                f"Epoch {epoch}: shift_takeover_events {record['shift_takeover_events']:.1f} exceeds threshold {args.shift_takeover_max}"
            )
    if args.chat_quality_min is not None and is_rollout:
        if record["chat_quality_mean"] < args.chat_quality_min:
            raise SystemExit(
                f"Epoch {epoch}: chat_quality_mean {record['chat_quality_mean']:.3f} below threshold {args.chat_quality_min}"
            )

    anneal_stage = record.get("anneal_stage")
    if anneal_stage:
        bc_accuracy = record.get("anneal_bc_accuracy")
        if args.anneal_bc_min is not None and bc_accuracy is not None:
            if bc_accuracy < args.anneal_bc_min:
                raise SystemExit(
                    f"Epoch {epoch}: anneal_bc_accuracy {bc_accuracy:.3f} below threshold {args.anneal_bc_min}"
                )
        loss_baseline = record.get("anneal_loss_baseline")
        loss_limit = args.anneal_loss_max
        if loss_baseline is not None and loss_limit is not None and loss_baseline:
            if abs(record["loss_total"] - loss_baseline) / abs(loss_baseline) > loss_limit:
                raise SystemExit(
                    f"Epoch {epoch}: loss_total {record['loss_total']:.6f} drifts beyond ±{loss_limit*100:.1f}% of baseline {loss_baseline:.6f}"
                )
        queue_min = args.anneal_queue_min
        if queue_min is None and is_rollout:
            baseline = record.get("anneal_queue_baseline") or 0.0
            queue_min = (1.0 - 0.15) * baseline if baseline else None
        if queue_min is not None and is_rollout:
            if record["queue_conflict_events"] < queue_min:
                raise SystemExit(
                    f"Epoch {epoch}: anneal queue_conflict_events {record['queue_conflict_events']:.1f} below threshold {queue_min}"
                )
        intensity_min = args.anneal_intensity_min
        if intensity_min is None and is_rollout:
            baseline = record.get("anneal_intensity_baseline") or 0.0
            intensity_min = (1.0 - 0.15) * baseline if baseline else None
        if intensity_min is not None and is_rollout:
            if record["queue_conflict_intensity_sum"] < intensity_min:
                raise SystemExit(
                    f"Epoch {epoch}: anneal queue_conflict_intensity_sum {record['queue_conflict_intensity_sum']:.2f} below threshold {intensity_min}"
                )


def main(args: list[str] | None = None) -> None:
    parsed = parse_args() if args is None else parse_args_from_list(args)
    try:
        for record in stream_records(parsed.log, parsed.follow, parsed.interval):
            check_thresholds(record, parsed)
            if parsed.json:
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
                    f"shared_meals={record['shared_meal_events']:.1f}, "
                    f"late_help={record['late_help_events']:.1f}, "
                    f"shift_takeovers={record['shift_takeover_events']:.1f}, "
                    f"chat_success={record['chat_success_events']:.1f}, "
                    f"chat_failure={record['chat_failure_events']:.1f}, "
                    f"chat_quality_mean={record['chat_quality_mean']:.3f}, "
                    f"offset={record['log_stream_offset']:.0f}"
                )
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

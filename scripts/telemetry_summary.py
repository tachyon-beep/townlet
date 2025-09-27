"""Produce summaries for PPO telemetry logs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarise PPO telemetry NDJSON logs")
    parser.add_argument("log", type=Path, help="Path to NDJSON telemetry log")
    parser.add_argument(
        "--baseline",
        type=Path,
        help="Optional baseline record (JSON object) for drift comparison",
    )
    parser.add_argument(
        "--format",
        choices={"text", "markdown", "json"},
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--last",
        type=int,
        default=None,
        help="Limit summary to the last N records",
    )
    return parser.parse_args()


def load_records(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as err:
            raise ValueError(f"{path}:{line_number}: invalid JSON – {err}") from err
        if not isinstance(payload, dict):
            raise ValueError(f"{path}:{line_number}: expected JSON object")
        records.append(payload)
    if not records:
        raise ValueError(f"{path}: no telemetry records found")
    return records


def load_baseline(path: Path | None) -> dict[str, float] | None:
    if path is None:
        return None
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("Baseline must be a JSON object")
    return {key: float(value) for key, value in data.items() if isinstance(value, (int, float))}


def summarise(records: Sequence[dict[str, object]], baseline: dict[str, float] | None) -> dict[str, object]:
    recent = records[-1]
    metrics = {
        "loss_total": [float(rec.get("loss_total", 0.0)) for rec in records],
        "kl_divergence": [float(rec.get("kl_divergence", 0.0)) for rec in records],
        "grad_norm": [float(rec.get("grad_norm", 0.0)) for rec in records],
        "batch_entropy_mean": [float(rec.get("batch_entropy_mean", 0.0)) for rec in records],
        "reward_advantage_corr": [float(rec.get("reward_advantage_corr", 0.0)) for rec in records],
        "queue_conflict_events": [float(rec.get("queue_conflict_events", 0.0)) for rec in records],
        "queue_conflict_intensity_sum": [
            float(rec.get("queue_conflict_intensity_sum", 0.0)) for rec in records
        ],
        "shared_meal_events": [float(rec.get("shared_meal_events", 0.0)) for rec in records],
        "late_help_events": [float(rec.get("late_help_events", 0.0)) for rec in records],
        "shift_takeover_events": [
            float(rec.get("shift_takeover_events", 0.0)) for rec in records
        ],
        "chat_success_events": [float(rec.get("chat_success_events", 0.0)) for rec in records],
        "chat_failure_events": [float(rec.get("chat_failure_events", 0.0)) for rec in records],
        "chat_quality_mean": [float(rec.get("chat_quality_mean", 0.0)) for rec in records],
    }
    anneal_records = [rec for rec in records if rec.get("anneal_stage")]
    summary = {
        "epochs": int(recent.get("epoch", len(records))),
        "data_mode": recent.get("data_mode", "unknown"),
        "cycle_id": recent.get("cycle_id"),
        "log_stream_offset": recent.get("log_stream_offset"),
        "latest": {
            "loss_total": metrics["loss_total"][-1],
            "kl_divergence": metrics["kl_divergence"][-1],
            "grad_norm": metrics["grad_norm"][-1],
            "batch_entropy_mean": metrics["batch_entropy_mean"][-1],
            "reward_advantage_corr": metrics["reward_advantage_corr"][-1],
            "epoch_duration_sec": float(recent.get("epoch_duration_sec", 0.0)),
            "rollout_ticks": float(recent.get("rollout_ticks", 0.0)),
            "queue_conflict_events": metrics["queue_conflict_events"][-1],
            "queue_conflict_intensity_sum": metrics["queue_conflict_intensity_sum"][-1],
            "shared_meal_events": metrics["shared_meal_events"][-1],
            "late_help_events": metrics["late_help_events"][-1],
            "shift_takeover_events": metrics["shift_takeover_events"][-1],
            "chat_success_events": metrics["chat_success_events"][-1],
            "chat_failure_events": metrics["chat_failure_events"][-1],
            "chat_quality_mean": metrics["chat_quality_mean"][-1],
        },
        "extremes": {
            "loss_total": {
                "min": min(metrics["loss_total"]),
                "max": max(metrics["loss_total"]),
            },
            "kl_divergence": {
                "min": min(metrics["kl_divergence"]),
                "max": max(metrics["kl_divergence"]),
            },
            "grad_norm": {
                "min": min(metrics["grad_norm"]),
                "max": max(metrics["grad_norm"]),
            },
            "queue_conflict_events": {
                "min": min(metrics["queue_conflict_events"]),
                "max": max(metrics["queue_conflict_events"]),
            },
            "shared_meal_events": {
                "min": min(metrics["shared_meal_events"]),
                "max": max(metrics["shared_meal_events"]),
            },
            "chat_quality_mean": {
                "min": min(metrics["chat_quality_mean"]),
                "max": max(metrics["chat_quality_mean"]),
            },
        },
    }
    if anneal_records:
        latest_anneal = anneal_records[-1]
        summary["anneal"] = {
            "stage": latest_anneal.get("anneal_stage"),
            "cycle": latest_anneal.get("anneal_cycle"),
            "dataset": latest_anneal.get("anneal_dataset"),
            "bc_accuracy": latest_anneal.get("anneal_bc_accuracy"),
            "bc_threshold": latest_anneal.get("anneal_bc_threshold"),
            "bc_passed": latest_anneal.get("anneal_bc_passed"),
            "loss_baseline": latest_anneal.get("anneal_loss_baseline"),
            "queue_baseline": latest_anneal.get("anneal_queue_baseline"),
            "intensity_baseline": latest_anneal.get("anneal_intensity_baseline"),
            "loss_flag": latest_anneal.get("anneal_loss_flag"),
            "queue_flag": latest_anneal.get("anneal_queue_flag"),
            "intensity_flag": latest_anneal.get("anneal_intensity_flag"),
        }
    if baseline:
        drift = {}
        for key, base_value in baseline.items():
            if key in recent and isinstance(recent[key], (int, float)):
                drift_val = float(recent[key]) - float(base_value)
                drift[key] = {
                    "delta": drift_val,
                    "percent": (drift_val / base_value * 100.0) if base_value else None,
                }
        summary["baseline_drift"] = drift
    return summary


def _format_optional_float(value: object, precision: int = 3) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value):.{precision}f}"
    except (TypeError, ValueError):
        return "n/a"


def render_text(summary: dict[str, object]) -> str:
    latest = summary["latest"]
    cycle = summary.get("cycle_id", "n/a")
    lines = [
        f"Epochs analysed: {summary['epochs']} (mode={summary['data_mode']}, cycle_id={cycle})",
        f"Latest metrics: loss_total={latest['loss_total']:.6f}, kl_divergence={latest['kl_divergence']:.6f}, grad_norm={latest['grad_norm']:.6f}",
        f"              entropy_mean={latest['batch_entropy_mean']:.6f}, reward_adv_corr={latest['reward_advantage_corr']:.6f}, epoch_duration={latest['epoch_duration_sec']:.4f}s",
    ]
    if latest["rollout_ticks"]:
        lines.append(f"              rollout_ticks={latest['rollout_ticks']:.0f}")
    lines.append(
        "Queue conflicts: events={events:.1f}, intensity_sum={intensity:.2f}".format(
            events=latest["queue_conflict_events"],
            intensity=latest["queue_conflict_intensity_sum"],
        )
    )
    lines.append(
        "Social interactions: shared_meals={meals:.1f}, late_help={helped:.1f}, "
        "shift_takeovers={takeovers:.1f}, chat_success={chat_s:.1f}, chat_failure={chat_f:.1f}, "
        "chat_quality_mean={chat_q:.3f}".format(
            meals=latest["shared_meal_events"],
            helped=latest["late_help_events"],
            takeovers=latest["shift_takeover_events"],
            chat_s=latest["chat_success_events"],
            chat_f=latest["chat_failure_events"],
            chat_q=latest["chat_quality_mean"],
        )
    )
    extremes = summary["extremes"]
    lines.append(
        "Extremes: "
        f"loss_total[min={extremes['loss_total']['min']:.6f}, max={extremes['loss_total']['max']:.6f}], "
        f"kl_divergence[min={extremes['kl_divergence']['min']:.6f}, max={extremes['kl_divergence']['max']:.6f}], "
        f"grad_norm[min={extremes['grad_norm']['min']:.6f}, max={extremes['grad_norm']['max']:.6f}]"
    )
    anneal = summary.get("anneal")
    if anneal:
        lines.append(
            "Anneal status: stage={stage} cycle={cycle}, dataset={dataset}, bc_accuracy={acc} (threshold={thr}), passed={passed}".format(
                stage=anneal.get("stage"),
                cycle=_format_optional_float(anneal.get("cycle"), precision=1),
                dataset=anneal.get("dataset"),
                acc=_format_optional_float(anneal.get("bc_accuracy")),
                thr=_format_optional_float(anneal.get("bc_threshold")),
                passed=anneal.get("bc_passed"),
            )
        )
        lines.append(
            "Anneal drift flags: loss={loss}, queue={queue}, intensity={intensity}".format(
                loss=anneal.get("loss_flag"),
                queue=anneal.get("queue_flag"),
                intensity=anneal.get("intensity_flag"),
            )
        )
    drift = summary.get("baseline_drift")
    if drift:
        lines.append("Baseline drift:")
        for key, payload in drift.items():
            percent = payload["percent"]
            pct_str = "n/a" if percent is None else f"{percent:+.2f}%"
            lines.append(f"  {key}: delta={payload['delta']:+.6f} ({pct_str})")
    return "\n".join(lines)


def render_markdown(summary: dict[str, object]) -> str:
    latest = summary["latest"]
    cycle = summary.get("cycle_id", "n/a")
    lines = [
        "### PPO Telemetry Summary",
        "",
        f"- Epochs analysed: **{summary['epochs']}**",
        f"- Data mode: **{summary['data_mode']}** (cycle `{cycle}`)",
        (
            "- Latest metrics: "
            f"`loss_total={latest['loss_total']:.6f}`, "
            f"`kl_divergence={latest['kl_divergence']:.6f}`, "
            f"`grad_norm={latest['grad_norm']:.6f}`, "
            f"`entropy_mean={latest['batch_entropy_mean']:.6f}`, "
            f"`reward_adv_corr={latest['reward_advantage_corr']:.6f}`"
        ),
        f"- Epoch duration: `{latest['epoch_duration_sec']:.4f}s`, roll-out ticks: `{latest['rollout_ticks']:.0f}`",
        f"- Queue conflicts: `{latest['queue_conflict_events']:.1f}` events (intensity sum `{latest['queue_conflict_intensity_sum']:.2f}`)",
    ]
    anneal = summary.get("anneal")
    if anneal:
        lines.append(
            f"- Anneal status: stage `{anneal.get('stage')}`, cycle `{_format_optional_float(anneal.get('cycle'), precision=1)}`, "
            f"dataset `{anneal.get('dataset')}`, bc_accuracy `{_format_optional_float(anneal.get('bc_accuracy'))}` "
            f"(threshold `{_format_optional_float(anneal.get('bc_threshold'))}`), passed `{anneal.get('bc_passed')}`"
        )
        lines.append(
            f"- Anneal drift flags: loss `{anneal.get('loss_flag')}`, queue `{anneal.get('queue_flag')}`, intensity `{anneal.get('intensity_flag')}`"
        )
    lines.extend(
        [
        "",
        "| Metric | Min | Max |",
        "| --- | --- | --- |",
        f"| loss_total | {summary['extremes']['loss_total']['min']:.6f} | {summary['extremes']['loss_total']['max']:.6f} |",
        f"| kl_divergence | {summary['extremes']['kl_divergence']['min']:.6f} | {summary['extremes']['kl_divergence']['max']:.6f} |",
        f"| grad_norm | {summary['extremes']['grad_norm']['min']:.6f} | {summary['extremes']['grad_norm']['max']:.6f} |",
        f"| queue_conflict_events | {summary['extremes']['queue_conflict_events']['min']:.1f} | {summary['extremes']['queue_conflict_events']['max']:.1f} |",
        f"| shared_meal_events | {summary['extremes']['shared_meal_events']['min']:.1f} | {summary['extremes']['shared_meal_events']['max']:.1f} |",
        f"| chat_quality_mean | {summary['extremes']['chat_quality_mean']['min']:.3f} | {summary['extremes']['chat_quality_mean']['max']:.3f} |",
        ]
    )
    drift = summary.get("baseline_drift")
    if drift:
        lines.append("\n#### Baseline Drift\n")
        lines.append("| Key | Delta | Percent |")
        lines.append("| --- | --- | --- |")
        for key, payload in drift.items():
            percent = payload["percent"]
            pct_str = "n/a" if percent is None else f"{percent:+.2f}%"
            lines.append(f"| {key} | {payload['delta']:+.6f} | {pct_str} |")
    return "\n".join(lines)

def render(summary: dict[str, object], fmt: str) -> str:
    if fmt == "text":
        return render_text(summary)
    if fmt == "markdown":
        return render_markdown(summary)
    return json.dumps(summary, indent=2)


def main() -> None:
    args = parse_args()
    records = load_records(args.log)
    if args.last:
        records = records[-args.last :]
    baseline = load_baseline(args.baseline)
    summary = summarise(records, baseline)
    print(render(summary, args.format))


if __name__ == "__main__":
    main()

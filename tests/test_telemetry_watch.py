import importlib.util
import sys
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "telemetry_watch",
    Path(__file__).resolve().parent.parent / "scripts" / "telemetry_watch.py",
)
assert spec and spec.loader
telemetry_watch = importlib.util.module_from_spec(spec)
sys.modules["telemetry_watch"] = telemetry_watch
spec.loader.exec_module(telemetry_watch)  # type: ignore[arg-type]


def write_log(tmp_path: Path, records: list[dict[str, object]]) -> Path:
    path = tmp_path / "log.jsonl"
    path.write_text(
        "\n".join([telemetry_watch.json.dumps(record) for record in records])
    )
    return path


@pytest.mark.parametrize("bc_accuracy", [0.95, 0.85])
def test_anneal_bc_threshold(tmp_path: Path, bc_accuracy: float) -> None:
    log = write_log(
        tmp_path,
        [
            {
                "epoch": 1,
                "loss_total": 0.2,
                "kl_divergence": 0.0,
                "grad_norm": 0.1,
                "batch_entropy_mean": 0.0,
                "reward_advantage_corr": 0.0,
                "log_stream_offset": 1,
                "data_mode": "replay",
                "queue_conflict_events": 0.0,
                "queue_conflict_intensity_sum": 0.0,
                "shared_meal_events": 0.0,
                "late_help_events": 0.0,
                "shift_takeover_events": 0.0,
                "chat_success_events": 0.0,
                "chat_failure_events": 0.0,
                "chat_quality_mean": 0.0,
                "utility_outage_events": 0.0,
                "shower_complete_events": 0.0,
                "sleep_complete_events": 0.0,
                "anneal_stage": "ppo",
                "anneal_bc_accuracy": bc_accuracy,
                "anneal_bc_threshold": 0.9,
            }
        ],
    )
    args = ["telemetry_watch.py", str(log), "--anneal-bc-min", "0.9"]
    try:
        telemetry_watch.main(args=args)
    except SystemExit as exc:
        if bc_accuracy >= 0.9:
            raise AssertionError("Unexpected exit for passing BC accuracy") from exc
    else:
        if bc_accuracy < 0.9:
            raise AssertionError("Expected exit for failing BC accuracy")


def test_new_event_thresholds(tmp_path: Path) -> None:
    log = write_log(
        tmp_path,
        [
            {
                "epoch": 3,
                "loss_total": 0.2,
                "kl_divergence": 0.0,
                "grad_norm": 0.1,
                "batch_entropy_mean": 0.0,
                "reward_advantage_corr": 0.0,
                "log_stream_offset": 3,
                "data_mode": "rollout",
                "queue_conflict_events": 10.0,
                "queue_conflict_intensity_sum": 25.0,
                "shared_meal_events": 2.0,
                "late_help_events": 1.0,
                "shift_takeover_events": 0.0,
                "chat_success_events": 4.0,
                "chat_failure_events": 1.0,
                "chat_quality_mean": 0.6,
                "utility_outage_events": 2.0,
                "shower_complete_events": 0.0,
                "sleep_complete_events": 0.0,
            }
        ],
    )
    args = [
        "telemetry_watch.py",
        str(log),
        "--utility-outage-max",
        "1",
        "--shower-complete-min",
        "1",
        "--sleep-complete-min",
        "1",
    ]
    with pytest.raises(SystemExit):
        telemetry_watch.main(args=args)

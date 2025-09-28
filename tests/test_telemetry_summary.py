from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "telemetry_summary",
    Path(__file__).resolve().parent.parent / "scripts" / "telemetry_summary.py",
)
assert spec and spec.loader
telemetry_summary = importlib.util.module_from_spec(spec)
sys.modules["telemetry_summary"] = telemetry_summary
spec.loader.exec_module(telemetry_summary)  # type: ignore[arg-type]


def test_summary_includes_new_events(tmp_path: Path) -> None:
    records = [
        {
            "epoch": 1,
            "loss_total": 0.2,
            "kl_divergence": 0.01,
            "grad_norm": 0.1,
            "batch_entropy_mean": 0.5,
            "reward_advantage_corr": 0.2,
            "queue_conflict_events": 8.0,
            "queue_conflict_intensity_sum": 21.0,
            "shared_meal_events": 3.0,
            "late_help_events": 1.0,
            "shift_takeover_events": 0.0,
            "chat_success_events": 4.0,
            "chat_failure_events": 1.0,
            "chat_quality_mean": 0.55,
            "utility_outage_events": 1.0,
            "shower_complete_events": 5.0,
            "sleep_complete_events": 6.0,
        },
        {
            "epoch": 2,
            "loss_total": 0.18,
            "kl_divergence": 0.02,
            "grad_norm": 0.12,
            "batch_entropy_mean": 0.48,
            "reward_advantage_corr": 0.21,
            "queue_conflict_events": 9.0,
            "queue_conflict_intensity_sum": 24.0,
            "shared_meal_events": 4.0,
            "late_help_events": 2.0,
            "shift_takeover_events": 1.0,
            "chat_success_events": 5.0,
            "chat_failure_events": 1.0,
            "chat_quality_mean": 0.6,
            "utility_outage_events": 0.0,
            "shower_complete_events": 6.0,
            "sleep_complete_events": 7.0,
        },
    ]
    log = tmp_path / "log.jsonl"
    log.write_text("\n".join(telemetry_summary.json.dumps(record) for record in records))
    snapshot_records = telemetry_summary.load_records(log)
    summary = telemetry_summary.summarise(snapshot_records, baseline=None)
    latest = summary["latest"]
    assert latest["utility_outage_events"] == 0.0
    assert latest["shower_complete_events"] == 6.0
    assert latest["sleep_complete_events"] == 7.0
    text_output = telemetry_summary.render_text(summary)
    assert "utility_outages" in text_output
    markdown_output = telemetry_summary.render_markdown(summary)
    assert "shower_complete_events" in markdown_output

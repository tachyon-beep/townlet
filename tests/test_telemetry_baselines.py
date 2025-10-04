from __future__ import annotations

import json
from pathlib import Path

BASELINE_DIR = Path("tests/data/baselines")


def _load(name: str) -> dict:
    path = BASELINE_DIR / name
    return json.loads(path.read_text(encoding="utf-8"))


def test_telemetry_steady_state_contains_defaults() -> None:
    payload = _load("telemetry_steady_state.json")
    employment = payload.get("employment") or payload.get("employment_metrics")
    assert employment is not None
    assert employment["pending_count"] == 0
    assert payload["queue_metrics"]["ghost_step_events"] == 0
    assert "affordance_manifest" in payload


def test_telemetry_affordance_active_contains_running_entry() -> None:
    payload = _load("telemetry_affordance_active.json")
    runtime = payload["affordance_runtime"]
    assert runtime["running_count"] >= 1
    entry = runtime["running"].get("bed_1")
    assert entry is not None
    assert entry["affordance_id"] == "rest_sleep"
    assert entry["agent_id"] == "alice"


def test_telemetry_employment_queue_has_pending_exit() -> None:
    payload = _load("telemetry_employment_queue.json")
    employment = payload.get("employment") or payload.get("employment_metrics")
    assert employment["pending_count"] >= 1
    assert "alice" in employment["pending"]


def test_console_results_employment_review_baseline() -> None:
    results = _load("console_results_employment_review.json")
    assert results
    last = results[-1]
    assert last["name"] == "employment_exit"
    assert last["status"] == "ok"
    assert last["result"].get("pending_count", 0) >= 1

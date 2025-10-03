from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path("scripts/promotion_evaluate.py").resolve()


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(SCRIPT), *args]
    return subprocess.run(cmd, text=True, capture_output=True)


def test_promotion_evaluate_promote(tmp_path: Path) -> None:
    payload = {
        "status": "PASS",
        "promotion": {
            "pass_streak": 2,
            "required_passes": 2,
            "candidate_ready": True,
            "last_result": "pass",
            "last_evaluated_tick": 2,
        },
        "results": [
            {"mode": "bc", "passed": True, "cycle": 0},
            {"mode": "ppo", "cycle": 1},
        ],
    }
    path = tmp_path / "payload.json"
    path.write_text(json.dumps(payload, indent=2))
    completed = _run("--input", str(path), "--format", "json")
    assert completed.returncode == 0
    output = json.loads(completed.stdout)
    assert output["decision"] == "PROMOTE"
    assert output["candidate_ready"] is True


def test_promotion_evaluate_hold_flags(tmp_path: Path) -> None:
    payload = {
        "status": "HOLD",
        "promotion": {
            "pass_streak": 1,
            "required_passes": 2,
            "candidate_ready": False,
            "last_result": "pass",
            "last_evaluated_tick": 1,
        },
        "results": [
            {"mode": "bc", "passed": True, "cycle": 0},
            {"mode": "ppo", "cycle": 1, "anneal_queue_flag": True},
        ],
    }
    path = tmp_path / "payload.json"
    path.write_text(json.dumps(payload, indent=2))
    completed = _run("--input", str(path), "--format", "json")
    assert completed.returncode == 1
    output = json.loads(completed.stdout)
    assert output["decision"] == "HOLD"
    assert "queue_flag_cycle_1" in output["reasons"]


def test_promotion_evaluate_dry_run(tmp_path: Path) -> None:
    payload = {
        "status": "FAIL",
        "promotion": {
            "pass_streak": 0,
            "required_passes": 2,
            "candidate_ready": False,
            "last_result": "fail",
            "last_evaluated_tick": 3,
        },
        "results": [
            {"mode": "bc", "passed": False, "cycle": 2},
        ],
    }
    path = tmp_path / "payload.json"
    path.write_text(json.dumps(payload, indent=2))
    completed = _run("--input", str(path), "--format", "json", "--dry-run")
    assert completed.returncode == 0
    output = json.loads(completed.stdout)
    assert output["decision"] == "FAIL"
    assert "bc_stage_failed_cycle_2" in output["reasons"]

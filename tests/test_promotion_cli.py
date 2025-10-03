import json
import subprocess
import sys
from pathlib import Path

import pytest

PYTHON = Path(sys.executable)
SCRIPT = Path("scripts/promotion_evaluate.py")


def write_summary(tmp_path: Path, accuracy: float, threshold: float = 0.9) -> Path:
    summary = tmp_path / "summary.json"
    summary.write_text(
        json.dumps(
            {
                "bc_accuracy": accuracy,
                "bc_threshold": threshold,
                "bc_passed": accuracy >= threshold,
            }
        )
    )
    return summary


def test_promotion_cli_pass(tmp_path: Path) -> None:
    summary = write_summary(tmp_path, 0.95)
    result = subprocess.run([PYTHON, SCRIPT, "--summary", summary], capture_output=True, text=True, check=False)
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"


def test_promotion_cli_fail(tmp_path: Path) -> None:
    summary = write_summary(tmp_path, 0.8)
    result = subprocess.run([PYTHON, SCRIPT, "--summary", summary], capture_output=True, text=True, check=False)
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"


def test_promotion_drill(tmp_path: Path) -> None:
    config = Path("configs/examples/poc_hybrid.yaml")
    if not config.exists():
        pytest.skip("example config not found")
    output = tmp_path / "drill"
    result = subprocess.run([PYTHON, Path("scripts/promotion_drill.py"), "--config", config, "--output", output, "--checkpoint", tmp_path / "chk.pt"], capture_output=True, text=True, check=False)
    assert result.returncode == 0
    summary_file = output / "promotion_drill_summary.json"
    data = json.loads(summary_file.read_text())
    assert data["promote"]["promoted"] is True
    assert data["rollback"]["rolled_back"] is True

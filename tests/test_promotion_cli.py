import json
import subprocess
import sys
from pathlib import Path

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

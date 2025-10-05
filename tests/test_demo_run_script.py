import sys
from pathlib import Path
from subprocess import CalledProcessError, run

import pytest

SCRIPT = Path("scripts/demo_run.py")


def test_demo_run_help() -> None:
    result = run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "--timeline" in result.stdout
    assert "--history-window" in result.stdout


def test_demo_run_missing_config(tmp_path: Path) -> None:
    config = tmp_path / "missing.yml"
    with pytest.raises(CalledProcessError):
        run([sys.executable, str(SCRIPT), str(config)], check=True, capture_output=True)

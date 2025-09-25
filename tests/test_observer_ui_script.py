import subprocess
import sys
from pathlib import Path


def test_observer_ui_script_runs_single_tick(tmp_path: Path) -> None:
    config = Path("configs/examples/poc_hybrid.yaml").resolve()
    result = subprocess.run(
        [sys.executable, "scripts/observer_ui.py", str(config), "--ticks", "1", "--refresh", "0"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Tick:" in result.stdout

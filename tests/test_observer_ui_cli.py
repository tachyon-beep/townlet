from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PYTHON = Path(sys.executable)
SCRIPT = Path("scripts/observer_ui.py")


@pytest.mark.skipif(not SCRIPT.exists(), reason="observer_ui.py script missing")
def test_observer_ui_cli_smoke(tmp_path: Path) -> None:
    source = Path("configs/demo/poc_demo.yaml")
    config_path = tmp_path / "poc_demo.yaml"
    payload = source.read_text().replace(
        "logs/demo_stream.jsonl",
        str((tmp_path / "observer_stream.jsonl").resolve()),
    )
    config_path.write_text(payload)

    result = subprocess.run(
        [
            str(PYTHON),
            str(SCRIPT),
            str(config_path),
            "--ticks",
            "3",
            "--refresh",
            "0.01",
            "--show-coordinates",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        pytest.fail(f"observer_ui.py failed: {result.stderr}")

    output_file = tmp_path / "observer_stream.jsonl"
    assert output_file.exists(), "telemetry file was not created"
    assert output_file.stat().st_size > 0, "telemetry file is empty"

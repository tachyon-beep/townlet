from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PYTHON = Path(sys.executable)
SCRIPT = Path("scripts/demo_run.py")


@pytest.mark.skipif(not SCRIPT.exists(), reason="demo_run.py script missing")
def test_demo_run_cli_smoke(tmp_path: Path) -> None:
    source = Path("configs/demo/poc_demo.yaml")
    config_path = tmp_path / "poc_demo.yaml"
    payload = source.read_text().replace(
        "logs/demo_stream.jsonl",
        str((tmp_path / "demo_stream.jsonl").resolve()),
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
            "--no-palette",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        pytest.fail(f"demo_run.py failed: {result.stderr}")

    output_file = tmp_path / "demo_stream.jsonl"
    assert output_file.exists(), "telemetry file was not created"
    assert output_file.stat().st_size > 0, "telemetry file is empty"

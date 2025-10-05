from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import run_simulation
from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop, SimulationLoopError, SimulationLoopHealth


def test_run_simulation_cli_iterates_ticks(monkeypatch):
    instances: list[object] = []

    class StubLoop:
        def __init__(self, config):
            self.config = config
            self.iterations = 0
            self.tick = 0
            self.telemetry = type("TelemetryStub", (), {"close": staticmethod(lambda: None)})()
            instances.append(self)

        def run(self, max_ticks=None):
            ticks = int(max_ticks or 0)
            for _ in range(ticks):
                self.iterations += 1
                self.tick += 1
                yield None

        def run_for(self, max_ticks: int) -> None:
            for _ in range(int(max_ticks)):
                self.iterations += 1
                self.tick += 1

    monkeypatch.setattr(run_simulation, "SimulationLoop", StubLoop)

    config_path = Path("configs/examples/poc_hybrid.yaml")
    monkeypatch.setattr(sys, "argv", ["run_simulation.py", str(config_path), "--ticks", "3"])

    run_simulation.main()

    assert instances, "SimulationLoop was never constructed"
    assert instances[0].iterations == 3


def test_simulation_loop_run_for_advances_ticks():
    config_path = Path("configs/demo/poc_demo.yaml")
    config = load_config(config_path)
    loop = SimulationLoop(config)
    loop.run_for(2)
    assert loop.tick == 2


def test_run_simulation_cli_smoke(tmp_path):
    config_path = Path("configs/examples/poc_hybrid.yaml")
    result = subprocess.run(
        [sys.executable, "scripts/run_simulation.py", str(config_path), "--ticks", "5"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Completed 5 ticks" in result.stdout
    assert "schema_version" not in result.stdout


def test_run_simulation_cli_streams_when_requested():
    config_path = Path("configs/examples/poc_hybrid.yaml")
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_simulation.py",
            str(config_path),
            "--ticks",
            "2",
            "--stream-telemetry",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "schema_version" in result.stdout
    assert "Completed 2 ticks" in result.stdout


def test_run_simulation_cli_writes_telemetry_file(tmp_path):
    config_path = Path("configs/examples/poc_hybrid.yaml")
    telemetry_path = tmp_path / "telemetry.jsonl"
    subprocess.run(
        [
            sys.executable,
            "scripts/run_simulation.py",
            str(config_path),
            "--ticks",
            "3",
            "--telemetry-path",
            str(telemetry_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert telemetry_path.exists()
    contents = telemetry_path.read_text()
    assert "schema_version" in contents


def test_run_simulation_cli_stream_and_path_are_mutually_exclusive():
    config_path = Path("configs/examples/poc_hybrid.yaml")
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_simulation.py",
            str(config_path),
            "--ticks",
            "1",
            "--stream-telemetry",
            "--telemetry-path",
            str(config_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "cannot be combined" in result.stderr


class _TelemetryStub:
    def __init__(self, payload: dict[str, object]):
        self._payload = payload

    def close(self) -> None:
        pass

    def latest_health_status(self) -> dict[str, object]:
        return dict(self._payload)


def test_run_simulation_cli_handles_loop_failure(monkeypatch, capsys):
    config_path = Path("configs/examples/poc_hybrid.yaml")

    class FailingLoop:
        def __init__(self, config):
            self.config = config
            self.telemetry = _TelemetryStub({"status": "error", "error": "ValueError: boom"})
            self._health = SimulationLoopHealth(
                last_tick=0,
                last_duration_ms=0.0,
                last_error="ValueError: boom",
                last_traceback=None,
                failure_count=1,
                last_failure_ts=None,
            )
            self.tick = 0

        def run_for(self, max_ticks: int) -> None:
            raise SimulationLoopError(1, "Simulation step failed", cause=ValueError("boom"))

        @property
        def health(self) -> SimulationLoopHealth:
            return self._health

    namespace = argparse.Namespace(
        config=config_path,
        ticks=5,
        stream_telemetry=False,
        telemetry_path=None,
    )
    monkeypatch.setattr(run_simulation, "parse_args", lambda: namespace)
    monkeypatch.setattr(run_simulation, "SimulationLoop", FailingLoop)

    with pytest.raises(SystemExit) as excinfo:
        run_simulation.main()

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Simulation loop aborted" in captured.err
    assert "ValueError: boom" in captured.err

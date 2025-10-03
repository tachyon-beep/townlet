from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world.affordances import DefaultAffordanceRuntime


@pytest.mark.parametrize("instrumentation", ["off", "timings"])
def test_runtime_config_factory_and_instrumentation(instrumentation: str, tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.affordances.runtime.factory = "tests.runtime_stubs:build_runtime"
    config.affordances.runtime.instrumentation = instrumentation
    loop = SimulationLoop(config)
    runtime = loop.world.affordance_runtime
    assert runtime.__class__.__name__ == "StubAffordanceRuntime"
    assert getattr(runtime, "instrumentation_level") == instrumentation
    assert loop.world.runtime_instrumentation_level == instrumentation


def test_runtime_factory_injection_via_fixture(
    stub_affordance_runtime_factory,
):
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config, affordance_runtime_factory=stub_affordance_runtime_factory)
    runtime = loop.world.affordance_runtime
    assert runtime.__class__.__name__ == "StubAffordanceRuntime"


def test_inspect_affordances_cli_snapshot(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.step()
    snapshot_path = loop.save_snapshot(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/inspect_affordances.py",
            "--snapshot",
            str(snapshot_path),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["source"] == "snapshot"
    assert payload["runtime"]["running_count"] >= 0


def test_inspect_affordances_cli_config(tmp_path: Path) -> None:
    config_path = Path("configs/examples/poc_hybrid.yaml")
    result = subprocess.run(
        [
            sys.executable,
            "scripts/inspect_affordances.py",
            "--config",
            str(config_path),
            "--ticks",
            "1",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["source"] == "config"
    assert payload["runtime"]["instrumentation"] == "off"

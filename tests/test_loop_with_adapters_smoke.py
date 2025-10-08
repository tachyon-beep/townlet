from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config.loader import load_config
from townlet.core.sim_loop import SimulationLoop


def test_loop_with_default_adapters_smoke() -> None:
    config_path = Path("configs/examples/poc_hybrid.yaml")
    if not config_path.exists():
        pytest.skip("example config not present")
    config = load_config(config_path)
    config.runtime.world.provider = "default"
    config.runtime.policy.provider = "scripted"
    config.runtime.telemetry.provider = "stdout"
    loop = SimulationLoop(config)
    loop.run_for(2)
    assert loop.tick == 2
    snapshot = loop.world.snapshot()
    assert snapshot["meta"]["tick"] == 2

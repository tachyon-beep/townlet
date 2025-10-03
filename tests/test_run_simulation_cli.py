from __future__ import annotations

import sys
from pathlib import Path

from scripts import run_simulation
from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop


def test_run_simulation_cli_iterates_ticks(monkeypatch):
    instances: list[object] = []

    class StubLoop:
        def __init__(self, config):
            self.config = config
            self.iterations = 0
            instances.append(self)

        def run(self, max_ticks=None):
            ticks = int(max_ticks or 0)
            for _ in range(ticks):
                self.iterations += 1
                yield None

        def run_for(self, max_ticks: int) -> None:
            for _ in range(int(max_ticks)):
                self.iterations += 1

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

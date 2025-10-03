from pathlib import Path

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop, TickArtifacts


def test_simulation_loop_runs_one_tick(tmp_path: Path) -> None:
    config_path = Path("configs/examples/poc_hybrid.yaml")
    loop = SimulationLoop(config=load_config(config_path))

    artifacts = next(loop.run(max_ticks=1))
    assert isinstance(artifacts, TickArtifacts)
    assert artifacts.observations == {}
    assert artifacts.rewards == {}


def test_run_for_ticks_collects_artifacts() -> None:
    config_path = Path("configs/examples/poc_hybrid.yaml")
    loop = SimulationLoop(config=load_config(config_path))
    results = loop.run_for_ticks(2, collect=True)
    assert loop.tick == 2
    assert len(results) == 2
    assert all(isinstance(item, TickArtifacts) for item in results)

from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.console.handlers import ConsoleCommand, create_console_router
from townlet.core.sim_loop import SimulationLoop
from townlet.world.grid import AgentSnapshot


def test_stability_alerts_exposed_via_telemetry_snapshot(tmp_path: Path) -> None:
    config_path = Path("configs/examples/poc_hybrid.yaml")
    if not config_path.exists():
        pytest.skip("example config not found")
    config = load_config(config_path)
    config.stability.starvation.min_duration_ticks = 1
    config.stability.starvation.max_incidents = 0
    config.stability.starvation.hunger_threshold = 0.8

    loop = SimulationLoop(config)
    loop.world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.0, "hygiene": 1.0, "energy": 1.0},
    )

    loop.step()

    alerts = loop.telemetry.latest_stability_alerts()
    metrics = loop.telemetry.latest_stability_metrics()

    assert "starvation_spike" in alerts
    assert "thresholds" in metrics
    assert metrics["thresholds"]["starvation"]["max_incidents"] == 0

    router = create_console_router(loop.telemetry, loop.world, config=config)
    snapshot = router.dispatch(ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={}))
    stability_block = snapshot["stability"]
    assert "alerts" in stability_block and "metrics" in stability_block
    assert "starvation_spike" in stability_block["alerts"]
    assert stability_block["metrics"]["thresholds"]["starvation"]["max_incidents"] == 0

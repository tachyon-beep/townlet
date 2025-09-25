from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world.grid import AgentSnapshot


def test_telemetry_captures_job_snapshot() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    publisher = loop.telemetry
    world = loop.world

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    world._assign_jobs_to_agents()  # type: ignore[attr-defined]

    # advance several steps to ensure jobs assigned and telemetry populated
    max_attempts = 10
    snapshot = {}
    for _ in range(max_attempts):
        loop.step()
        snapshot = publisher.latest_job_snapshot()
        if snapshot:
            break
    assert snapshot
    first_agent = next(iter(snapshot.values()))
    assert "job_id" in first_agent
    assert "on_shift" in first_agent
    assert "wages_earned" in first_agent


def test_stability_monitor_lateness_alert() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.stability.lateness_threshold = 0
    loop = SimulationLoop(config)

    if not loop.world.agents:
        loop.world.agents["alice"] = AgentSnapshot(
            agent_id="alice",
            position=(0, 0),
            needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
            wallet=1.0,
        )
        loop.world._assign_jobs_to_agents()  # type: ignore[attr-defined]

    agent_id = next(iter(loop.world.agents.keys()))
    loop.world.agents[agent_id].position = (999, 999)

    loop.tick = 175
    for _ in range(10):
        loop.step()

    assert loop.stability.latest_alert == "lateness_spike"

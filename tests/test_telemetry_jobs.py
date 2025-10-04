from pathlib import Path

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.stability.monitor import StabilityMonitor
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
    world.assign_jobs_to_agents()  

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
    monitor = StabilityMonitor(config)

    monitor.track(
        tick=0,
        rewards={},
        terminated={},
        job_snapshot={"alice": {"late_ticks_today": 2}},
        queue_metrics={},
        embedding_metrics={},
        events=[],
    )

    assert monitor.latest_alert == "lateness_spike"

from pathlib import Path

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.telemetry.publisher import TelemetryPublisher
from townlet.world.grid import AgentSnapshot


def make_loop() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    world = loop.world
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    world._assign_jobs_to_agents()  # type: ignore[attr-defined]
    return loop


def test_observer_payload_contains_job_and_economy() -> None:
    loop = make_loop()
    publisher: TelemetryPublisher = loop.telemetry
    for _ in range(5):
        loop.step()

    job_snapshot = publisher.latest_job_snapshot()
    economy_snapshot = publisher.latest_economy_snapshot()
    assert "alice" in job_snapshot
    assert "wages_earned" in job_snapshot["alice"]
    assert economy_snapshot
    first_obj = next(iter(economy_snapshot.values()))
    assert "stock" in first_obj


def test_planning_payload_consistency() -> None:
    loop = make_loop()
    publisher: TelemetryPublisher = loop.telemetry
    for _ in range(5):
        loop.step()
    job_snapshot = publisher.latest_job_snapshot()
    economy_snapshot = publisher.latest_economy_snapshot()

    for agent_info in job_snapshot.values():
        assert isinstance(agent_info.get("wallet"), float)
        assert isinstance(agent_info.get("lateness_counter"), int)

    for obj_info in economy_snapshot.values():
        assert isinstance(obj_info.get("type"), str)
        for value in obj_info.get("stock", {}).values():
            assert isinstance(value, int)

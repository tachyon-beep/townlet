from pathlib import Path

from townlet.config import load_config
from townlet.console.handlers import ConsoleCommand, create_console_router
from townlet.core.sim_loop import SimulationLoop
from townlet.world.grid import AgentSnapshot


def test_console_telemetry_snapshot_returns_payload() -> None:
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

    router = create_console_router(loop.telemetry)

    for _ in range(5):
        loop.step()

    result = router.dispatch(ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={}))
    assert "jobs" in result and "economy" in result
    assert "alice" in result["jobs"]
    assert isinstance(result["economy"], dict)

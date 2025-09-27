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

    router = create_console_router(loop.telemetry, world)

    for _ in range(5):
        loop.step()

    result = router.dispatch(ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={}))
    assert result["schema_version"] == loop.telemetry.schema()
    assert result["schema_warning"] is None
    assert "jobs" in result and "economy" in result and "employment" in result
    assert "conflict" in result
    assert result["conflict"].get("queues") is not None
    assert result["conflict"].get("rivalry") is not None
    assert "alice" in result["jobs"]
    assert isinstance(result["economy"], dict)
    assert isinstance(result.get("reward_breakdown"), dict)


def test_employment_console_commands_manage_queue() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.employment.enforce_job_loop = True
    loop = SimulationLoop(config)
    world = loop.world
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    world._assign_jobs_to_agents()  # type: ignore[attr-defined]
    router = create_console_router(loop.telemetry, world)

    world._employment_enqueue_exit("alice", world.tick)
    review = router.dispatch(ConsoleCommand(name="employment_exit", args=("review",), kwargs={}))
    assert review["pending_count"] == 1

    defer = router.dispatch(
        ConsoleCommand(name="employment_exit", args=("defer", "alice"), kwargs={})
    )
    assert defer["deferred"] is True
    assert world.employment_queue_snapshot()["pending_count"] == 0

    world._employment_enqueue_exit("alice", world.tick)
    approve = router.dispatch(
        ConsoleCommand(name="employment_exit", args=("approve", "alice"), kwargs={})
    )
    assert approve["approved"] is True
    assert "alice" in world._employment_manual_exits

    status = router.dispatch(ConsoleCommand(name="employment_status", args=(), kwargs={}))
    assert status["schema_version"] == loop.telemetry.schema()
    assert status["schema_warning"] is None
    assert "metrics" in status


def test_console_schema_warning_for_newer_version() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.telemetry.schema_version = "0.4.0"
    router = create_console_router(loop.telemetry, loop.world)

    snapshot = router.dispatch(ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={}))
    assert snapshot["schema_version"] == "0.4.0"
    assert isinstance(snapshot["schema_warning"], str)

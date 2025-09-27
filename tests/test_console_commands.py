from pathlib import Path

from townlet.config import (
    FloatRange,
    IntRange,
    PriceSpikeEventConfig,
    PerturbationSchedulerConfig,
    load_config,
)
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

    router = create_console_router(loop.telemetry, world, loop.perturbations)

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
    assert "stability" in result
    assert "alerts" in result["stability"]
    assert isinstance(result["stability"]["alerts"], list)
    assert "thresholds" in result["stability"]["metrics"]


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
    router = create_console_router(loop.telemetry, world, loop.perturbations)

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
    router = create_console_router(loop.telemetry, loop.world, loop.perturbations)

    snapshot = router.dispatch(ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={}))
    assert snapshot["schema_version"] == "0.4.0"
    assert isinstance(snapshot["schema_warning"], str)

def test_console_perturbation_requires_admin_mode() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    viewer_router = create_console_router(loop.telemetry, loop.world, loop.perturbations, mode="viewer")
    result = viewer_router.dispatch(
        ConsoleCommand(name="perturbation_trigger", args=("price_spike",), kwargs={})
    )
    assert result["error"] == "forbidden"



def test_console_perturbation_commands_schedule_and_cancel() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.perturbations = PerturbationSchedulerConfig(
        global_cooldown_ticks=5,
        events={
            "price_spike": PriceSpikeEventConfig(
                probability_per_day=0.0,
                duration=IntRange(min=1, max=1),
                magnitude=FloatRange(min=1.5, max=1.5),
                targets=["market"],
            )
        }
    )
    loop = SimulationLoop(config)
    router = create_console_router(loop.telemetry, loop.world, loop.perturbations, mode="admin")

    queue_before = router.dispatch(ConsoleCommand(name="perturbation_queue", args=(), kwargs={}))
    assert queue_before["active"] == {}

    trigger_pending = router.dispatch(
        ConsoleCommand(
            name="perturbation_trigger",
            args=("price_spike",),
            kwargs={"targets": "market", "starts_in": 1},
        )
    )
    pending_id = trigger_pending["event"]["event_id"]
    queue_mid = router.dispatch(ConsoleCommand(name="perturbation_queue", args=(), kwargs={}))
    assert any(evt["event_id"] == pending_id for evt in queue_mid["pending"])
    cancel_pending = router.dispatch(
        ConsoleCommand(name="perturbation_cancel", args=(pending_id,), kwargs={})
    )
    assert cancel_pending["cancelled"] is True

    trigger_active = router.dispatch(
        ConsoleCommand(
            name="perturbation_trigger",
            args=("price_spike",),
            kwargs={"targets": "market", "magnitude": 2.0},
        )
    )
    active_id = trigger_active["event"]["event_id"]

    loop.step()
    telemetry_state = loop.telemetry.latest_perturbations()

    queue_after = router.dispatch(ConsoleCommand(name="perturbation_queue", args=(), kwargs={}))
    assert active_id not in queue_after["active"]
    assert "price_spike" in telemetry_state["cooldowns"]["spec"]

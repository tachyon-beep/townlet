from dataclasses import replace
from pathlib import Path

from townlet.config import (
    ArrangedMeetEventConfig,
    FloatRange,
    IntRange,
    PerturbationSchedulerConfig,
    PriceSpikeEventConfig,
    load_config,
)
from townlet.console.handlers import ConsoleCommand, create_console_router
from townlet.core.sim_loop import SimulationLoop
from townlet.snapshots import SnapshotManager
from townlet.snapshots.migrations import clear_registry, register_migration
from townlet.snapshots.state import SnapshotState
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

    router = create_console_router(
        loop.telemetry, world, loop.perturbations, policy=loop.policy, config=config
    )

    for _ in range(5):
        loop.step()

    result = router.dispatch(
        ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={})
    )
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



def test_console_conflict_status_reports_history() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    world = loop.world
    world.agents.setdefault(
        "alice",
        AgentSnapshot(
            agent_id="alice",
            position=(0, 0),
            needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
            wallet=1.0,
        ),
    )
    world.agents.setdefault(
        "bob",
        AgentSnapshot(
            agent_id="bob",
            position=(1, 0),
            needs={"hunger": 0.6, "hygiene": 0.4, "energy": 0.5},
            wallet=1.2,
        ),
    )
    router = create_console_router(loop.telemetry, world, loop.perturbations, policy=loop.policy, config=config)
    for _ in range(3):
        loop.step()
    world.register_rivalry_conflict("alice", "bob", intensity=1.2)
    status = router.dispatch(ConsoleCommand(name="conflict_status", args=(), kwargs={}))
    assert status["schema_version"] == loop.telemetry.schema()
    assert "conflict" in status
    assert isinstance(status.get("history"), list)
    assert isinstance(status.get("rivalry_events"), list)
    assert "stability_alerts" in status


def test_console_queue_inspect_returns_queue_details() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    world = loop.world
    router = create_console_router(loop.telemetry, world, loop.perturbations, policy=loop.policy, config=config)
    queue_id = "test_object"
    world.queue_manager.request_access(queue_id, "alice", tick=0)
    world.queue_manager.request_access(queue_id, "bob", tick=1)
    world.queue_manager.record_blocked_attempt(queue_id)
    result = router.dispatch(
        ConsoleCommand(name="queue_inspect", args=(queue_id,), kwargs={})
    )
    assert result["object_id"] == queue_id
    assert result["queue"]
    assert "metrics" in result
    assert isinstance(result["cooldowns"], list)


def test_console_rivalry_dump_reports_pairs() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    world = loop.world
    world.agents.setdefault(
        "alice",
        AgentSnapshot(
            agent_id="alice",
            position=(0, 0),
            needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
            wallet=1.0,
        ),
    )
    world.agents.setdefault(
        "bob",
        AgentSnapshot(
            agent_id="bob",
            position=(1, 0),
            needs={"hunger": 0.6, "hygiene": 0.4, "energy": 0.5},
            wallet=1.2,
        ),
    )
    world.register_rivalry_conflict("alice", "bob", intensity=2.0)
    router = create_console_router(loop.telemetry, world, loop.perturbations, policy=loop.policy, config=config)
    summary = router.dispatch(ConsoleCommand(name="rivalry_dump", args=(), kwargs={}))
    assert summary["pairs"]
    alice_view = router.dispatch(
        ConsoleCommand(name="rivalry_dump", args=("alice",), kwargs={"limit": 1})
    )
    assert alice_view["rivals"]
    assert alice_view["rivals"][0]["agent_id"] == "bob"


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
    router = create_console_router(
        loop.telemetry, world, loop.perturbations, policy=loop.policy, config=config
    )

    world._employment_enqueue_exit("alice", world.tick)
    review = router.dispatch(
        ConsoleCommand(name="employment_exit", args=("review",), kwargs={})
    )
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

    status = router.dispatch(
        ConsoleCommand(name="employment_status", args=(), kwargs={})
    )
    assert status["schema_version"] == loop.telemetry.schema()
    assert status["schema_warning"] is None
    assert "metrics" in status


def test_console_schema_warning_for_newer_version() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.telemetry.schema_version = "0.4.0"
    router = create_console_router(
        loop.telemetry, loop.world, loop.perturbations, policy=loop.policy, config=config
    )

    snapshot = router.dispatch(
        ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={})
    )
    assert snapshot["schema_version"] == "0.4.0"
    assert isinstance(snapshot["schema_warning"], str)


def test_console_perturbation_requires_admin_mode() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    viewer_router = create_console_router(
        loop.telemetry,
        loop.world,
        loop.perturbations,
        policy=loop.policy,
        mode="viewer",
        config=config,
    )
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
        },
    )
    loop = SimulationLoop(config)
    router = create_console_router(
        loop.telemetry,
        loop.world,
        loop.perturbations,
        policy=loop.policy,
        mode="admin",
        config=config,
    )

    queue_before = router.dispatch(
        ConsoleCommand(name="perturbation_queue", args=(), kwargs={})
    )
    assert queue_before["active"] == {}

    trigger_pending = router.dispatch(
        ConsoleCommand(
            name="perturbation_trigger",
            args=("price_spike",),
            kwargs={"targets": "market", "starts_in": 1},
        )
    )
    pending_id = trigger_pending["event"]["event_id"]
    queue_mid = router.dispatch(
        ConsoleCommand(name="perturbation_queue", args=(), kwargs={})
    )
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

    queue_after = router.dispatch(
        ConsoleCommand(name="perturbation_queue", args=(), kwargs={})
    )
    assert active_id not in queue_after["active"]
    assert "price_spike" in telemetry_state["cooldowns"]["spec"]


def test_console_arrange_meet_schedules_event() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.perturbations.events["meetup"] = ArrangedMeetEventConfig(
        target="agents",
        location="cafe",
        max_participants=4,
    )
    loop = SimulationLoop(config)
    world = loop.world
    for idx in range(2):
        world.agents[f"agent_{idx}"] = AgentSnapshot(
            agent_id=f"agent_{idx}",
            position=(idx, 0),
            needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
            wallet=1.0,
        )
    router = create_console_router(
        loop.telemetry,
        world,
        loop.perturbations,
        policy=loop.policy,
        mode="admin",
        config=config,
    )
    command = ConsoleCommand(
        name="arrange_meet",
        args=(),
        kwargs={
            "payload": {
                "spec": "meetup",
                "agents": ["agent_0", "agent_1"],
                "starts_in": 0,
                "duration": 20,
            }
        },
    )
    result = router.dispatch(command)
    assert "event_id" in result
    state = loop.perturbations.latest_state()
    assert result["event_id"] in state.get("active", {}) or any(
        entry["event_id"] == result["event_id"] for entry in state.get("pending", [])
    )


def test_console_arrange_meet_unknown_spec_returns_error() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    router = create_console_router(
        loop.telemetry,
        loop.world,
        loop.perturbations,
        policy=loop.policy,
        mode="admin",
        config=config,
    )
    command = ConsoleCommand(
        name="arrange_meet",
        args=(),
        kwargs={"payload": {"spec": "unknown", "agents": ["alice"]}},
    )
    result = router.dispatch(command)
    assert result["error"] == "unknown_spec"


def test_console_snapshot_commands(tmp_path: Path) -> None:
    clear_registry()
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    router_viewer = create_console_router(
        loop.telemetry,
        loop.world,
        loop.perturbations,
        policy=loop.policy,
        config=config,
    )
    for _ in range(3):
        loop.step()
    snapshot_path = loop.save_snapshot(tmp_path)

    inspect = router_viewer.dispatch(
        ConsoleCommand(name="snapshot_inspect", args=(str(snapshot_path),), kwargs={})
    )
    assert inspect["config_id"] == config.config_id

    validate = router_viewer.dispatch(
        ConsoleCommand(name="snapshot_validate", args=(str(snapshot_path),), kwargs={})
    )
    assert validate["valid"] is True

    legacy_state = SnapshotState(config_id="legacy", tick=5)
    legacy_manager = SnapshotManager(tmp_path)
    legacy_path = legacy_manager.save(legacy_state)

    strict_failure = router_viewer.dispatch(
        ConsoleCommand(
            name="snapshot_validate",
            args=(str(legacy_path),),
            kwargs={"strict": True},
        )
    )
    assert strict_failure["valid"] is False

    register_migration(
        "legacy",
        config.config_id,
        lambda state, cfg: replace(state, config_id=cfg.config_id),
    )

    router_admin = create_console_router(
        loop.telemetry,
        loop.world,
        loop.perturbations,
        policy=loop.policy,
        mode="admin",
        config=config,
    )

    migrate_result = router_admin.dispatch(
        ConsoleCommand(name="snapshot_migrate", args=(str(legacy_path),), kwargs={})
    )
    assert migrate_result["migrations_applied"]
    assert loop.telemetry.latest_snapshot_migrations()

    output_dir = tmp_path / "migrated"
    migrate_output = router_admin.dispatch(
        ConsoleCommand(
            name="snapshot_migrate",
            args=(str(legacy_path),),
            kwargs={"output": str(output_dir)},
        )
    )
    assert Path(migrate_output["output_path"]).exists()

    forbidden = router_viewer.dispatch(
        ConsoleCommand(name="snapshot_migrate", args=(str(snapshot_path),), kwargs={})
    )
    assert forbidden["error"] == "forbidden"

    clear_registry()

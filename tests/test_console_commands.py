import json
import threading
from dataclasses import replace
from pathlib import Path

import pytest

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
from townlet_ui.commands import (
    CommandQueueFull,
    ConsoleCommandExecutor,
    PaletteCommandRequest,
)


def _load_palette_fixture(name: str) -> dict[str, object]:
    with Path("tests/data/palette_commands.json").open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    for group in (payload.get("viewer", []), payload.get("admin", []), payload.get("backlog", [])):
        for entry in group:
            if entry.get("name") == name:
                return entry
    raise KeyError(name)


def _load_palette_error_fixture(name: str) -> dict[str, object]:
    with Path("tests/data/palette_command_errors.json").open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    for entry in payload.get("invalid", []):
        if entry.get("name") == name:
            return entry
    raise KeyError(name)


def test_palette_command_request_from_payload_normalises() -> None:
    payload = _load_palette_fixture("queue_inspect")
    request = PaletteCommandRequest.from_payload(payload)
    assert request.name == "queue_inspect"
    assert request.args == ("coffee_shop_1",)
    assert request.kwargs == {}

    console_command = request.to_console_command()
    assert isinstance(console_command, ConsoleCommand)
    assert console_command.name == request.name
    assert console_command.args == request.args
    assert console_command.kwargs == request.kwargs


@pytest.mark.parametrize(
    "payload, message",
    [
        ({"args": []}, "name"),
        ({"name": " ", "args": []}, "name"),
        ({"name": "test", "args": "invalid"}, "args"),
        ({"name": "test", "kwargs": "invalid"}, "kwargs"),
    ],
)
def test_palette_command_request_from_payload_validation(
    payload: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ValueError) as exc:
        PaletteCommandRequest.from_payload(payload)
    assert message in str(exc.value)


def test_console_executor_submit_payload_enqueues_and_returns_command() -> None:
    class _Router:
        def __init__(self) -> None:
            self.commands: list[ConsoleCommand] = []
            self.event = threading.Event()

        def dispatch(self, command: ConsoleCommand) -> None:
            self.commands.append(command)
            self.event.set()

    router = _Router()
    executor = ConsoleCommandExecutor(router)
    payload = _load_palette_fixture("social_events")

    command = executor.submit_payload(payload)
    assert router.event.wait(timeout=0.5)
    assert router.commands == [command]

    executor.shutdown()


def test_console_executor_submit_payload_dry_run_only() -> None:
    class _Router:
        def __init__(self) -> None:
            self.commands: list[ConsoleCommand] = []
            self.event = threading.Event()

        def dispatch(self, command: ConsoleCommand) -> None:
            self.commands.append(command)
            self.event.set()

    router = _Router()
    executor = ConsoleCommandExecutor(router, autostart=False)
    payload = _load_palette_fixture("social_events")

    command = executor.submit_payload(payload, enqueue=False)
    assert command.name == "social_events"
    assert not router.event.wait(timeout=0.1)
    assert executor.pending_count() == 0

    executor.shutdown()


def test_console_executor_queue_limit_guard() -> None:
    class _Router:
        def dispatch(self, command: ConsoleCommand) -> None:
            pass

    router = _Router()
    executor = ConsoleCommandExecutor(router, autostart=False, max_pending=1)
    payload = _load_palette_fixture("social_events")

    executor.submit_payload(payload)
    assert executor.pending_count() == 1

    with pytest.raises(CommandQueueFull):
        executor.submit_payload(payload)

    executor.shutdown()


@pytest.mark.parametrize(
    "fixture_name",
    ["queue_inspect", "social_events", "set_spawn_delay", "relationship_detail"],
)
def test_console_error_fixture_alignment(fixture_name: str) -> None:
    entry = _load_palette_error_fixture(fixture_name)
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    router = create_console_router(
        loop.telemetry,
        loop.world,
        loop.perturbations,
        promotion=loop.promotion,
        policy=loop.policy,
        config=config,
        lifecycle=loop.lifecycle,
        mode=str(entry.get("mode", "viewer")),
    )

    command = ConsoleCommand(
        name=entry["name"],
        args=tuple(entry.get("args", [])),
        kwargs=entry.get("kwargs", {}),
    )
    result = router.dispatch(command)
    expected = entry["expected_error"]
    assert result["error"] == expected["code"]
    assert result["message"] == expected["message"]


def test_announce_story_command_enqueues_narration() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    router = create_console_router(
        loop.telemetry,
        loop.world,
        loop.perturbations,
        promotion=loop.promotion,
        policy=loop.policy,
        config=config,
        lifecycle=loop.lifecycle,
        mode="viewer",
    )

    command = ConsoleCommand(name="announce_story", args=(), kwargs={"message": "Welcome!"})
    result = router.dispatch(command)
    assert result["queued"] is True
    entry = result["entry"]
    assert entry["message"] == "Welcome!"

    narrations = loop.telemetry.latest_narrations()
    assert any(entry.get("message") == "Welcome!" for entry in narrations)

    loop.world.tick = 1
    loop.telemetry.emit_event(
        "loop.tick",
        {
            "tick": 1,
            "world": loop.world,
            "observations": {},
            "rewards": {},
            "events": [],
            "policy_snapshot": {},
            "kpi_history": False,
            "reward_breakdown": {},
            "stability_inputs": {},
            "perturbations": {},
            "policy_identity": {},
            "possessed_agents": [],
            "social_events": [],
        },
    )
    narrations_next = loop.telemetry.latest_narrations()
    assert any(entry.get("message") == "Welcome!" for entry in narrations_next)

    throttled = router.dispatch(command)
    assert throttled["queued"] is False
    assert throttled.get("throttled") is True


def _seed_relationship_state(loop: SimulationLoop) -> None:
    loop.telemetry.import_state(
        {
            "relationship_summary": {
                "alice": {
                    "top_friends": [
                        {"agent": "bob", "trust": 0.8, "familiarity": 0.7, "rivalry": 0.1},
                        {"agent": "carol", "trust": 0.6, "familiarity": 0.5, "rivalry": 0.05},
                    ],
                    "top_rivals": [{"agent": "dave", "rivalry": 0.4}],
                },
                "churn": {
                    "window_start": 10,
                    "window_end": 20,
                    "total_evictions": 1,
                    "per_owner": {"alice": 1},
                    "per_reason": {"conflict": 1},
                },
            },
            "relationship_snapshot": {
                "alice": {
                    "bob": {"trust": 0.8, "familiarity": 0.7, "rivalry": 0.1},
                    "carol": {"trust": 0.6, "familiarity": 0.5, "rivalry": 0.05},
                },
                "bob": {
                    "alice": {"trust": 0.75, "familiarity": 0.65, "rivalry": 0.12}
                },
            },
            "relationship_updates": [
                {
                    "owner": "alice",
                    "other": "bob",
                    "status": "updated",
                    "trust": 0.8,
                    "familiarity": 0.7,
                    "rivalry": 0.1,
                    "delta": {"trust": 0.1, "familiarity": 0.1, "rivalry": -0.05},
                },
                {
                    "owner": "bob",
                    "other": "alice",
                    "status": "updated",
                    "trust": 0.75,
                    "familiarity": 0.65,
                    "rivalry": 0.12,
                    "delta": {"trust": -0.05, "familiarity": 0.05, "rivalry": 0.02},
                },
            ],
            "relationship_overlay": {
                "alice": [
                    {
                        "owner": "alice",
                        "other": "bob",
                        "trust": 0.8,
                        "familiarity": 0.7,
                        "rivalry": 0.1,
                        "delta_trust": 0.1,
                        "delta_familiarity": 0.1,
                        "delta_rivalry": -0.05,
                    }
                ]
            },
            "social_events": [
                {"tick": 15, "type": "chat", "actors": ["alice", "bob"]},
                {"tick": 17, "type": "rivalry_avoid", "owner": "bob", "other": "alice"},
            ],
            "narrations": [
                {
                    "tick": 10,
                    "category": "relationship_friendship",
                    "message": "alice bonded with bob",
                    "priority": True,
                    "data": {"owner": "alice", "other": "bob"},
                }
            ],
        }
    )


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
    world.assign_jobs_to_agents()  

    router = create_console_router(
        loop.telemetry, world, loop.perturbations, policy=loop.policy, config=config
    )

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
    runtime_payload = result.get("affordance_runtime")
    assert isinstance(runtime_payload, dict)
    assert "running_count" in runtime_payload
    alice_job = result["jobs"]["alice"]
    assert "needs" in alice_job and isinstance(alice_job["needs"], dict)
    assert isinstance(result.get("perturbations"), dict)
    command_metadata = result.get("console_commands")
    assert isinstance(command_metadata, dict)
    assert "relationship_summary" in command_metadata
    assert "relationship_detail" in command_metadata
    assert "social_events" in command_metadata


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
    router = create_console_router(
        loop.telemetry, world, loop.perturbations, policy=loop.policy, config=config
    )
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
    router = create_console_router(
        loop.telemetry, world, loop.perturbations, policy=loop.policy, config=config
    )
    queue_id = "test_object"
    world.queue_manager.request_access(queue_id, "alice", tick=0)
    world.queue_manager.request_access(queue_id, "bob", tick=1)
    world.queue_manager.record_blocked_attempt(queue_id)
    result = router.dispatch(ConsoleCommand(name="queue_inspect", args=(queue_id,), kwargs={}))
    assert result["object_id"] == queue_id
    assert result["queue"]
    assert "metrics" in result
    assert isinstance(result["cooldowns"], list)


def test_console_set_spawn_delay_updates_lifecycle() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    router = create_console_router(
        loop.telemetry,
        loop.world,
        loop.perturbations,
        promotion=loop.promotion,
        policy=loop.policy,
        config=config,
        lifecycle=loop.lifecycle,
        mode="admin",
    )
    response = router.dispatch(
        ConsoleCommand(
            name="set_spawn_delay",
            args=("5",),
            kwargs={"cmd_id": "spawn-delay"},
        )
    )
    assert response["respawn_delay_ticks"] == 5
    assert loop.lifecycle.respawn_delay_ticks == 5


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
    router = create_console_router(
        loop.telemetry, world, loop.perturbations, policy=loop.policy, config=config
    )
    summary = router.dispatch(ConsoleCommand(name="rivalry_dump", args=(), kwargs={}))
    assert summary["pairs"]
    alice_view = router.dispatch(
        ConsoleCommand(name="rivalry_dump", args=("alice",), kwargs={"limit": 1})
    )
    assert alice_view["rivals"]
    assert alice_view["rivals"][0]["agent_id"] == "bob"


def test_console_relationship_summary_returns_payload() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    _seed_relationship_state(loop)
    router = create_console_router(
        loop.telemetry, loop.world, loop.perturbations, policy=loop.policy, config=config
    )
    result = router.dispatch(ConsoleCommand(name="relationship_summary", args=(), kwargs={}))
    assert result["schema_version"] == loop.telemetry.schema()
    summary = result["summary"]["alice"]
    assert summary["top_friends"][0]["agent"] == "bob"
    assert result["churn"]["total_evictions"] == 1


def test_console_relationship_detail_requires_admin_mode() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    _seed_relationship_state(loop)
    viewer_router = create_console_router(
        loop.telemetry, loop.world, loop.perturbations, policy=loop.policy, config=config
    )
    response = viewer_router.dispatch(
        ConsoleCommand(name="relationship_detail", args=("alice",), kwargs={})
    )
    assert response["error"] == "forbidden"


def test_console_relationship_detail_returns_payload_for_admin() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    _seed_relationship_state(loop)
    admin_router = create_console_router(
        loop.telemetry,
        loop.world,
        loop.perturbations,
        policy=loop.policy,
        config=config,
        mode="admin",
    )
    payload = admin_router.dispatch(
        ConsoleCommand(name="relationship_detail", args=("alice",), kwargs={})
    )
    assert payload["agent_id"] == "alice"
    assert any(entry["other"] == "bob" for entry in payload["ties"])
    assert payload["recent_updates"][0]["delta"]["trust"] == 0.1
    assert any(update["owner"] == "bob" for update in payload["incoming_updates"])


def test_console_relationship_detail_unknown_agent_returns_error() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    _seed_relationship_state(loop)
    admin_router = create_console_router(
        loop.telemetry,
        loop.world,
        loop.perturbations,
        policy=loop.policy,
        config=config,
        mode="admin",
    )
    result = admin_router.dispatch(
        ConsoleCommand(name="relationship_detail", args=("zoe",), kwargs={})
    )
    assert result["error"] == "not_found"


def test_console_social_events_limit_and_validation() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    _seed_relationship_state(loop)
    router = create_console_router(
        loop.telemetry, loop.world, loop.perturbations, policy=loop.policy, config=config
    )
    limited = router.dispatch(
        ConsoleCommand(name="social_events", args=(), kwargs={"limit": 1})
    )
    assert len(limited["events"]) == 1
    assert limited["events"][0]["type"] == "rivalry_avoid"
    invalid = router.dispatch(
        ConsoleCommand(name="social_events", args=(), kwargs={"limit": "bad"})
    )
    assert invalid["error"] == "invalid_args"


def test_console_narrations_and_relationship_summary_snapshot() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    _seed_relationship_state(loop)
    router = create_console_router(
        loop.telemetry, loop.world, loop.perturbations, policy=loop.policy, config=config
    )
    snapshot = router.dispatch(ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={}))
    assert snapshot["relationship_summary"]["alice"]["top_friends"][0]["agent"] == "bob"
    narrations = loop.telemetry.latest_narrations()
    assert any(entry.get("category") == "relationship_friendship" for entry in narrations)


def test_console_affordance_status_reports_runtime() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    world = loop.world
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"energy": 0.2},
        wallet=1.0,
    )
    router = create_console_router(
        loop.telemetry, world, loop.perturbations, policy=loop.policy, config=config
    )
    granted = world.queue_manager.request_access("bed_1", "alice", world.tick)
    assert granted is True
    world._sync_reservation("bed_1")
    started = world._start_affordance("alice", "bed_1", "rest_sleep")
    assert started is True

    status = router.dispatch(ConsoleCommand(name="affordance_status", args=(), kwargs={}))
    runtime = status["runtime"]
    assert runtime["running_count"] == 1
    assert "bed_1" in runtime["running"]
    assert runtime["running"]["bed_1"]["agent_id"] == "alice"


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
    world.assign_jobs_to_agents()  
    router = create_console_router(
        loop.telemetry, world, loop.perturbations, policy=loop.policy, config=config
    )

    world.employment.enqueue_exit(world, "alice", world.tick)
    review = router.dispatch(ConsoleCommand(name="employment_exit", args=("review",), kwargs={}))
    assert review["pending_count"] == 1

    defer = router.dispatch(
        ConsoleCommand(name="employment_exit", args=("defer", "alice"), kwargs={})
    )
    assert defer["deferred"] is True
    assert world.employment_queue_snapshot()["pending_count"] == 0

    world.employment.enqueue_exit(world, "alice", world.tick)
    approve = router.dispatch(
        ConsoleCommand(name="employment_exit", args=("approve", "alice"), kwargs={})
    )
    assert approve["approved"] is True
    assert "alice" in world.employment.manual_exit_agents()

    status = router.dispatch(ConsoleCommand(name="employment_status", args=(), kwargs={}))
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

    snapshot = router.dispatch(ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={}))
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
    config.snapshot.guardrails.allowed_paths.append(tmp_path)
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

    health = router_viewer.dispatch(ConsoleCommand(name="health_status", args=(), kwargs={}))
    assert "health" in health
    assert isinstance(health["health"], dict)

    clear_registry()


def test_console_snapshot_rejects_outside_roots(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    router = create_console_router(
        loop.telemetry,
        loop.world,
        loop.perturbations,
        policy=loop.policy,
        mode="admin",
        config=config,
    )
    outside = tmp_path / "forbidden.json"
    outside.write_text("{}", encoding="utf-8")
    result = router.dispatch(
        ConsoleCommand(name="snapshot_inspect", args=(str(outside),), kwargs={})
    )
    assert result["error"] == "forbidden"

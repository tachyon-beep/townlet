from __future__ import annotations

from pathlib import Path

from townlet.config import ConsoleAuthConfig, ConsoleAuthTokenConfig, load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.dto.telemetry import TelemetryEventDTO, TelemetryMetadata
from townlet.world.grid import AgentSnapshot


def _make_employment_loop(enable_console: bool = False) -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.employment.enforce_job_loop = True
    if enable_console:
        console_auth = ConsoleAuthConfig(
            enabled=True,
            require_auth_for_viewer=False,
            tokens=[
                ConsoleAuthTokenConfig(token="viewer-token", role="viewer", label="viewer"),
                ConsoleAuthTokenConfig(token="admin-token", role="admin", label="admin"),
            ],
        )
        config = config.model_copy(update={"console_auth": console_auth})
    loop = SimulationLoop(config)
    loop.world.agents.clear()
    loop.world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.4, "hygiene": 0.5, "energy": 0.6},
        wallet=2.0,
    )
    loop.world.assign_jobs_to_agents()  
    return loop


def test_employment_queue_snapshot_tracks_pending_agent() -> None:
    loop = _make_employment_loop()
    world = loop.world
    world.employment.enqueue_exit(world, "alice", loop.tick)

    snapshot = world.employment_queue_snapshot()
    assert snapshot["pending"] == ["alice"]
    assert snapshot["pending_count"] == 1

    event = TelemetryEventDTO(
        event_type="loop.tick",
        tick=loop.tick,
        payload={
            "tick": loop.tick,
            "world": world,
            "rewards": {},
            "events": world.drain_events(),
            "policy_snapshot": {},
            "kpi_history": False,
            "reward_breakdown": {},
            "stability_inputs": {},
            "perturbations": {},
            "policy_identity": {},
            "possessed_agents": [],
            "social_events": [],
        },
        metadata=TelemetryMetadata(),
    )
    loop.telemetry.emit_event(event)
    metrics = loop.telemetry.latest_employment_metrics()
    assert metrics["pending"] == ["alice"]
    assert metrics["pending_count"] == 1

    loop.close()


def test_employment_defer_exit_clears_queue_and_emits_event() -> None:
    loop = _make_employment_loop()
    world = loop.world
    world.employment.enqueue_exit(world, "alice", loop.tick)

    assert world.employment_defer_exit("alice") is True

    events = world.drain_events()
    event = TelemetryEventDTO(
        event_type="loop.tick",
        tick=loop.tick,
        payload={
            "tick": loop.tick,
            "world": world,
            "rewards": {},
            "events": events,
            "policy_snapshot": {},
            "kpi_history": False,
            "reward_breakdown": {},
            "stability_inputs": {},
            "perturbations": {},
            "policy_identity": {},
            "possessed_agents": [],
            "social_events": [],
        },
        metadata=TelemetryMetadata(),
    )
    loop.telemetry.emit_event(event)

    metrics = loop.telemetry.latest_employment_metrics()
    assert metrics["pending_count"] == 0
    assert any(event.get("event") == "employment_exit_deferred" for event in events)

    loop.close()


def test_manual_exit_request_tracked_in_state() -> None:
    loop = _make_employment_loop()
    world = loop.world
    assert world.employment_request_manual_exit("alice", tick=loop.tick) is True
    state = world.employment.export_state()
    assert "alice" in state["manual_exits"]

    loop.close()

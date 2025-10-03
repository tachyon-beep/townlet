from collections.abc import Mapping
from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.console.handlers import create_console_router
from townlet.core.sim_loop import SimulationLoop
from townlet_ui.telemetry import SchemaMismatchError, TelemetryClient


def make_simulation(enforce_job_loop: bool = True) -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.employment.enforce_job_loop = enforce_job_loop
    loop = SimulationLoop(config)
    world = loop.world
    if not world.agents:
        # Ensure at least one agent exists for snapshots.
        from townlet.world.grid import AgentSnapshot

        world.agents["alice"] = AgentSnapshot(
            agent_id="alice",
            position=(0, 0),
            needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
            wallet=1.0,
        )
        world._assign_jobs_to_agents()  # type: ignore[attr-defined]
    return loop


def test_telemetry_client_parses_console_snapshot() -> None:
    loop = make_simulation()
    router = create_console_router(loop.telemetry, loop.world, policy=loop.policy, config=loop.config)
    for _ in range(5):
        loop.step()

    client = TelemetryClient()
    snapshot = client.from_console(router)

    assert snapshot.schema_version.startswith("0.9")
    assert snapshot.schema_warning is None
    assert snapshot.employment.pending_count >= 0
    assert snapshot.conflict.queue_cooldown_events >= 0
    assert snapshot.conflict.queue_ghost_step_events >= 0
    assert snapshot.conflict.rivalry_agents >= 0
    assert snapshot.agents
    assert snapshot.conflict.queue_rotation_events >= 0
    assert isinstance(snapshot.conflict.queue_history, tuple)
    assert isinstance(snapshot.conflict.rivalry_events, tuple)
    assert snapshot.affordance_runtime.running_count >= 0
    assert isinstance(snapshot.affordance_runtime.event_counts, Mapping)
    assert isinstance(snapshot.stability.alerts, tuple)
    assert isinstance(snapshot.stability.metrics, dict)
    assert snapshot.agents[0].agent_id
    assert isinstance(snapshot.narrations, list)
    transport = snapshot.transport
    assert isinstance(transport.connected, bool)
    assert transport.dropped_messages >= 0
    assert transport.last_success_tick is None or transport.last_success_tick >= 0
    assert snapshot.economy_settings
    assert "meal_cost" in snapshot.economy_settings
    assert "power" in snapshot.utilities
    assert isinstance(snapshot.price_spikes, tuple)


def test_telemetry_client_warns_on_newer_schema(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    loop = make_simulation()
    router = create_console_router(loop.telemetry, loop.world, policy=loop.policy, config=loop.config)
    for _ in range(2):
        loop.step()

    # Monkeypatch schema version to simulate newer shard.
    loop.telemetry.schema_version = "0.4.0"
    client = TelemetryClient()
    snapshot = client.from_console(router)
    assert snapshot.schema_warning is not None


def test_telemetry_client_raises_on_major_mismatch() -> None:
    client = TelemetryClient(expected_schema_prefix="0.7")
    payload = {"schema_version": "1.0.0", "employment": {}, "jobs": {}, "conflict": {}}
    with pytest.raises(SchemaMismatchError):
        client.parse_snapshot(payload)

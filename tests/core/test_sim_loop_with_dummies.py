from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers.dummy_loop import build_dummy_loop
from townlet.config import SimulationConfig, load_config
from townlet.core.sim_loop import TickArtifacts
from townlet.world.dto.observation import DTO_SCHEMA_VERSION


@pytest.fixture()
def simulation_config() -> SimulationConfig:
    return load_config(Path("configs/examples/poc_hybrid.yaml"))


def test_dummy_loop_ticks_and_emits_artifacts(simulation_config) -> None:
    harness = build_dummy_loop(simulation_config, agent_ids=("alice", "bob"))
    loop = harness.loop

    first = loop.step()
    second = loop.step()

    assert isinstance(first, TickArtifacts)
    assert isinstance(second, TickArtifacts)
    assert first.envelope.schema_version == DTO_SCHEMA_VERSION
    assert second.envelope.schema_version == DTO_SCHEMA_VERSION
    assert loop.tick == 2
    assert isinstance(first.rewards, dict)
    assert isinstance(second.rewards, dict)


def test_dummy_loop_routes_console_commands(simulation_config) -> None:
    harness = build_dummy_loop(simulation_config, agent_ids=("alice",))
    loop = harness.loop
    telemetry_sink = harness.telemetry_sink

    loop.telemetry.queue_console_command({"name": "snapshot", "cmd_id": "snap-1"})
    loop.step()

    console_events = [entry for entry in telemetry_sink.events if entry[0] == "console.result"]
    assert console_events, "expected console.result event"
    command_payload = console_events[-1][1]
    assert command_payload["result"]["status"] == "ok"
    assert command_payload["result"]["cmd_id"] == "snap-1"
    assert isinstance(command_payload["result"]["result"], dict)


def test_dummy_loop_emits_health_event(simulation_config) -> None:
    harness = build_dummy_loop(simulation_config, agent_ids=("alice",))
    loop = harness.loop
    telemetry_sink = harness.telemetry_sink

    loop.step()

    health_events = [entry for entry in telemetry_sink.events if entry[0] == "loop.health"]
    assert health_events, "loop.health event not emitted"
    payload = health_events[-1][1]
    assert payload["tick"] == loop.tick
    assert "global_context" in payload
    assert isinstance(payload["global_context"], dict)

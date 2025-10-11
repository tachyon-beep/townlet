from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import SimulationConfig, load_config

from tests.helpers.dummy_loop import build_dummy_loop


@pytest.fixture()
def simulation_config() -> SimulationConfig:
    return load_config(Path("configs/examples/poc_hybrid.yaml"))


def test_console_router_smoke(simulation_config: SimulationConfig) -> None:
    harness = build_dummy_loop(simulation_config, agent_ids=("alice",))
    loop = harness.loop
    telemetry_sink = harness.telemetry_sink

    assert harness.console_router is not None, "Console router should be initialised"

    loop.telemetry.queue_console_command({"name": "snapshot", "cmd_id": "snap-1"})
    loop.telemetry.queue_console_command({"name": "unknown", "cmd_id": "oops"})

    loop.step()

    console_events = [payload for name, payload in telemetry_sink.events if name == "console.result"]
    assert len(console_events) >= 2, "Expected console.result events for queued commands"
    status_by_cmd = {payload["result"].get("cmd_id"): payload["result"]["status"] for payload in console_events}
    assert status_by_cmd.get("snap-1") == "ok"
    assert status_by_cmd.get("oops") == "error"
    assert all(
        isinstance(payload["result"]["result"], dict) for payload in console_events if payload["result"]["status"] == "ok"
    )


def test_health_monitor_emits_metrics(simulation_config: SimulationConfig) -> None:
    harness = build_dummy_loop(simulation_config, agent_ids=("alice", "bob"))
    loop = harness.loop
    telemetry_sink = harness.telemetry_sink

    assert harness.health_monitor is not None, "Health monitor should be initialised"

    loop.step()
    loop.step()

    metric_names = [name for name, _value, _tags in telemetry_sink.metrics]
    assert "world.events.count" in metric_names
    assert "world.events.avg" in metric_names
    assert "queue.length.latest" in metric_names
    assert "queue.length.avg" in metric_names

    latest_counts = [value for name, value, _ in telemetry_sink.metrics if name == "world.events.count"]
    assert latest_counts, "Expected at least one world.events.count metric"
    assert all(value >= 0 for value in latest_counts)

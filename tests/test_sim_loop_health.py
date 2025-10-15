from __future__ import annotations

import types
from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop, SimulationLoopError
from townlet.dto.observations import ObservationEnvelope


@pytest.fixture()
def simulation_loop() -> SimulationLoop:
    config_path = Path("configs/examples/poc_hybrid.yaml")
    return SimulationLoop(config=load_config(config_path))


def test_simulation_loop_failure_records_health(simulation_loop: SimulationLoop, tmp_path: Path) -> None:
    loop = simulation_loop
    loop.config.snapshot.capture_on_failure = True
    loop.config.snapshot.storage.root = tmp_path / "snapshots"

    def failing_tick(self, *args, **kwargs):  # type: ignore[override]
        raise ValueError("boom")

    loop.runtime.tick = types.MethodType(failing_tick, loop.runtime)
    invoked: list[tuple[int, BaseException]] = []
    loop.register_failure_handler(lambda _loop, tick, exc: invoked.append((tick, exc)))

    with pytest.raises(SimulationLoopError):
        loop.step()

    health = loop.health
    error = health.last_error or ""
    assert "boom" in error and "ValueError" in error
    assert health.failure_count == 1
    snapshot_path = Path(health.last_snapshot_path or "")
    assert snapshot_path.exists()
    latest_health = loop.telemetry.latest_health_status()
    assert latest_health.get("status") == "error"
    assert latest_health.get("snapshot_path") == str(snapshot_path)
    transport = latest_health.get("transport")
    assert isinstance(transport, dict)
    summary = latest_health.get("summary")
    assert isinstance(summary, dict)
    assert transport.get("queue_length") == summary.get("queue_length")
    assert transport.get("dropped_messages") == summary.get("dropped_messages")
    assert "telemetry_queue" not in latest_health
    assert "aliases" not in latest_health
    assert snapshot_path.parent.parent.name == "failures"
    assert loop.tick == 0
    assert invoked and invoked[0][0] == 1


def test_simulation_loop_success_clears_error(simulation_loop: SimulationLoop) -> None:
    loop = simulation_loop
    # Ensure there is at least one successful step
    artifacts = loop.step()
    assert isinstance(artifacts.envelope, ObservationEnvelope)
    health = loop.health
    assert health.last_error is None
    assert health.last_snapshot_path is None
    latest_health = loop.telemetry.latest_health_status()
    assert latest_health.get("status") == "ok"
    transport = latest_health.get("transport")
    assert isinstance(transport, dict)
    summary = latest_health.get("summary")
    assert isinstance(summary, dict)
    assert transport.get("queue_length") == summary.get("queue_length")
    assert transport.get("dropped_messages") == summary.get("dropped_messages")
    assert "global_context" in latest_health
    assert isinstance(latest_health["global_context"], dict)
    assert "telemetry_queue" not in latest_health
    assert "aliases" not in latest_health
    duration_ms = latest_health.get("duration_ms")
    assert duration_ms is not None
    assert pytest.approx(duration_ms, rel=1e-6) == summary.get("duration_ms")

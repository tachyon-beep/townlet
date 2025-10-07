from __future__ import annotations

import json
import time
import types
from pathlib import Path

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet_ui.telemetry import TelemetryClient


def _ensure_agents(loop: SimulationLoop) -> None:
    world = loop.world
    if world.agents:
        return
    from townlet.world.grid import AgentSnapshot

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    world.assign_jobs_to_agents()  


def test_file_transport_stream_smoke(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.telemetry.transport.type = "file"
    config.telemetry.transport.file_path = tmp_path / "telemetry.jsonl"
    config.telemetry.transport.buffer.max_batch_size = 1
    config.telemetry.transport.buffer.flush_interval_ticks = 1
    config.telemetry.diff_enabled = False

    loop = SimulationLoop(config)
    _ensure_agents(loop)

    for _ in range(3):
        loop.step()

    loop.close()

    stream_path = config.telemetry.transport.file_path
    assert stream_path.exists()
    lines = [line for line in stream_path.read_text().splitlines() if line.strip()]
    assert lines, "telemetry stream should contain at least one payload"

    payload = json.loads(lines[-1])
    snapshot = TelemetryClient().parse_payload(payload)

    assert snapshot.schema_version.startswith("0.9")
    assert snapshot.transport.last_success_tick is None or snapshot.transport.last_success_tick >= 1
    assert snapshot.transport.dropped_messages == 0


def test_file_transport_diff_stream(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.telemetry.transport.type = "file"
    config.telemetry.transport.file_path = tmp_path / "telemetry_diff.jsonl"
    config.telemetry.transport.buffer.max_batch_size = 1
    config.telemetry.transport.buffer.flush_interval_ticks = 1
    config.telemetry.diff_enabled = True

    loop = SimulationLoop(config)
    _ensure_agents(loop)

    for _ in range(3):
        loop.step()

    loop.close()

    stream_path = config.telemetry.transport.file_path
    lines = [json.loads(line) for line in stream_path.read_text().splitlines() if line.strip()]
    assert len(lines) >= 2
    assert lines[0].get("payload_type") == "snapshot"
    assert any(line.get("payload_type") == "diff" for line in lines[1:])

    client = TelemetryClient()
    for payload in lines:
        snapshot = client.parse_payload(payload)

    assert snapshot.schema_version.startswith("0.9")
    assert snapshot.transport.dropped_messages >= 0


def test_flush_worker_restarts_on_failure(monkeypatch, tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.telemetry.transport.type = "file"
    config.telemetry.transport.file_path = tmp_path / "telemetry_restart.jsonl"
    config.telemetry.transport.buffer.max_batch_size = 1
    config.telemetry.transport.buffer.flush_interval_ticks = 1
    loop = SimulationLoop(config)
    _ensure_agents(loop)
    publisher = loop.telemetry

    manager = publisher._worker_manager
    original = manager._flush_pending
    state = {"calls": 0}

    def failing(self):  # pragma: no cover - executed in worker thread
        state["calls"] += 1
        if state["calls"] == 1:
            raise RuntimeError("flush boom")
        return original()

    monkeypatch.setattr(manager, "_flush_pending", types.MethodType(failing, manager))

    loop.step()

    for _ in range(60):
        status = dict(publisher._transport_status)
        if status.get("worker_restart_count", 0) >= 1:
            break
        time.sleep(0.05)
    else:
        raise AssertionError("flush worker did not increment restart count")

    for _ in range(60):
        thread = manager._thread
        if thread is not None and thread.is_alive():
            break
        time.sleep(0.05)
    else:
        raise AssertionError("flush worker did not restart")

    status = publisher._transport_status
    assert status["worker_restart_count"] >= 1
    thread = manager._thread
    assert thread is not None and thread.is_alive()
    assert status["worker_error"] is None
    assert status["last_worker_error"].startswith("RuntimeError")

    # restore original behaviour and ensure clean shutdown
    loop.step()
    publisher.close()


def test_flush_worker_halts_after_restart_limit(monkeypatch, tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.telemetry.transport.type = "file"
    config.telemetry.transport.file_path = tmp_path / "telemetry_limit.jsonl"
    config.telemetry.transport.buffer.max_batch_size = 1
    config.telemetry.transport.buffer.flush_interval_ticks = 1
    config.telemetry.worker.restart_limit = 1
    loop = SimulationLoop(config)
    _ensure_agents(loop)
    publisher = loop.telemetry
    manager = publisher._worker_manager

    def always_fail(self):  # pragma: no cover - executed in worker thread
        raise RuntimeError("persistent failure")

    monkeypatch.setattr(manager, "_flush_pending", types.MethodType(always_fail, manager))

    loop.step()

    for _ in range(60):
        status = dict(publisher._transport_status)
        if status.get("worker_restart_count", 0) >= config.telemetry.worker.restart_limit:
            if not status.get("worker_alive"):
                break
        time.sleep(0.05)
    else:
        raise AssertionError("flush worker did not stop after reaching restart limit")

    status = publisher._transport_status
    assert status["worker_restart_count"] == config.telemetry.worker.restart_limit
    assert status["worker_alive"] is False
    assert status["worker_error"] is not None
    publisher.close()

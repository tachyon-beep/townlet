from __future__ import annotations

import logging
import time
from pathlib import Path

from townlet.config import ConsoleAuthConfig, ConsoleAuthTokenConfig, load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.telemetry.publisher import TelemetryPublisher


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
    loop.world.assign_jobs_to_agents()


def test_flush_worker_failure_sets_status(monkeypatch, caplog) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.telemetry.transport.type = "stdout"
    config.telemetry.transport.buffer.max_batch_size = 1
    config.telemetry.transport.buffer.flush_interval_ticks = 1

    publisher = TelemetryPublisher(config)
    caplog.set_level(logging.CRITICAL, "townlet.telemetry.publisher")
    try:
        original_flush = publisher._flush_transport_buffer

        def fail_once(tick: int) -> None:  # pragma: no cover - executed in worker thread
            monkeypatch.setattr(publisher, "_flush_transport_buffer", original_flush)
            raise RuntimeError("flush worker crash")

        monkeypatch.setattr(publisher, "_flush_transport_buffer", fail_once)
        with publisher._buffer_lock:
            publisher._transport_buffer.append(b"payload")
            publisher._latest_enqueue_tick = 1
        publisher._flush_event.set()

        for _ in range(60):
            status = publisher.latest_transport_status()
            if status.get("worker_restart_count", 0) >= 1:
                break
            time.sleep(0.05)
        else:
            raise AssertionError("flush worker did not report restart")

        status = publisher.latest_transport_status()
        assert status["worker_alive"] is True
        assert status["worker_error"] is None
        assert status["last_worker_error"].startswith("RuntimeError")
        assert status["worker_restart_count"] == 1
        assert any(
            "Telemetry flush worker failed" in record.getMessage()
            for record in caplog.records
        )
    finally:
        monkeypatch.setattr(publisher, "_flush_transport_buffer", original_flush)
        publisher.stop_worker(wait=True)
        publisher.close()


def test_health_metrics_include_worker_status(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.telemetry.transport.type = "file"
    config.telemetry.transport.file_path = tmp_path / "telemetry_health.jsonl"
    config.telemetry.transport.buffer.max_batch_size = 1
    config.telemetry.transport.buffer.flush_interval_ticks = 1
    config.telemetry.diff_enabled = False

    loop = SimulationLoop(config)
    try:
        _ensure_agents(loop)
        loop.step()
        metrics = loop.telemetry.latest_health_status()

        assert metrics["telemetry_worker_alive"] is True
        assert metrics["telemetry_worker_error"] is None
        assert metrics["telemetry_worker_restart_count"] == 0
        assert metrics["telemetry_console_auth_enabled"] is False
    finally:
        loop.telemetry.close()

def test_health_metrics_reflect_auth_enabled(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    console_auth = ConsoleAuthConfig(enabled=True, tokens=[ConsoleAuthTokenConfig(token="secret", role="admin")])
    config = config.model_copy(update={"console_auth": console_auth})
    config.telemetry.transport.type = "file"
    config.telemetry.transport.file_path = tmp_path / "telemetry_auth.jsonl"
    config.telemetry.transport.buffer.max_batch_size = 1
    config.telemetry.transport.buffer.flush_interval_ticks = 1
    loop = SimulationLoop(config)
    try:
        _ensure_agents(loop)
        loop.step()
        metrics = loop.telemetry.latest_health_status()
        assert metrics["telemetry_console_auth_enabled"] is True
    finally:
        loop.telemetry.close()

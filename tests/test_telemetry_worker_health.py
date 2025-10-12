from __future__ import annotations

import logging
import time
import types
from collections.abc import Mapping
from pathlib import Path

from townlet.config import ConsoleAuthConfig, ConsoleAuthTokenConfig, load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.telemetry.publisher import TelemetryPublisher


def _failure_payload(tick: int, error: str = "boom") -> dict[str, object]:
    return {
        "tick": tick,
        "status": "error",
        "error": error,
        "duration_ms": 0.0,
        "snapshot_path": None,
        "transport": {
            "provider": "port",
            "queue_length": 0,
            "dropped_messages": 0,
            "last_flush_duration_ms": None,
            "payloads_flushed_total": 0,
            "bytes_flushed_total": 0,
            "auth_enabled": False,
            "worker": {"alive": True, "error": None, "restart_count": 0},
        },
        "global_context": {},
        "summary": {
            "duration_ms": 0.0,
            "queue_length": 0,
            "dropped_messages": 0,
        },
    }


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
        manager = publisher._worker_manager
        original_flush = manager._flush_pending
        state = {"calls": 0}

        def failing(self):  # pragma: no cover - executed in worker thread
            state["calls"] += 1
            if state["calls"] == 1:
                raise RuntimeError("flush worker crash")
            return original_flush()

        monkeypatch.setattr(
            manager,
            "_flush_pending",
            types.MethodType(failing, manager),
        )
        manager.enqueue(b"payload", tick=1)

        for _ in range(60):
            status = publisher.latest_transport_status()
            if status.get("worker_restart_count", 0) >= 1:
                break
            time.sleep(0.05)
        else:
            raise AssertionError("flush worker did not report restart")

        for _ in range(60):
            thread = manager._thread
            if thread is not None and thread.is_alive():
                break
            time.sleep(0.05)
        else:
            raise AssertionError("flush worker thread did not restart")

        status = publisher.latest_transport_status()
        assert status["worker_restart_count"] >= 1
        thread = manager._thread
        assert thread is not None and thread.is_alive()
        assert status["worker_error"] is None
        assert status["last_worker_error"].startswith("RuntimeError")
        assert status["worker_restart_count"] == 1
        assert any(
            "Telemetry flush worker failed" in record.getMessage()
            for record in caplog.records
        )
    finally:
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
        summary = metrics.get("summary")
        assert isinstance(summary, dict)
        assert summary["worker_alive"] is True
        assert summary["worker_error"] is None
        assert summary["worker_restart_count"] == 0
        assert summary["auth_enabled"] is False
    finally:
        loop.close()

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
        summary = metrics.get("summary")
        assert isinstance(summary, dict)
        assert summary["auth_enabled"] is True
    finally:
        loop.close()


def test_record_loop_failure_emits_pipeline_events(monkeypatch) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.telemetry.transport.type = "stdout"
    publisher = TelemetryPublisher(config)
    emitted: list[tuple[dict[str, object], int]] = []

    def capture(payload: Mapping[str, object], *, tick: int) -> None:
        emitted.append((dict(payload), int(tick)))

    monkeypatch.setattr(publisher, "_enqueue_stream_payload", capture)
    try:
        publisher.emit_event("loop.failure", _failure_payload(7))
        assert emitted, "loop failure did not emit telemetry payload"
        payload, tick = emitted[0]
        assert tick == 7
        assert payload["error"] == "boom"
        assert "tick" in payload
    finally:
        publisher.close()

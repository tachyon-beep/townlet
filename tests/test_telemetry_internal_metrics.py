from __future__ import annotations

import time
from pathlib import Path

from townlet.config import load_config
from townlet.telemetry.publisher import TelemetryPublisher


def _failure_payload(tick: int, error: str = "simulated") -> dict[str, object]:
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
        "aliases": {
            "tick_duration_ms": 0.0,
            "telemetry_queue": 0,
            "telemetry_dropped": 0,
        },
    }


def _sleep_brief() -> None:
    # Allow the worker thread to process a flush
    time.sleep(0.2)


def test_worker_flush_counters_increment() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    pub = TelemetryPublisher(config)
    try:
        # Trigger a few small payloads via loop failure events
        for i in range(3):
            pub.emit_event("loop.failure", _failure_payload(i + 1))
        _sleep_brief()
    finally:
        pub.stop_worker(wait=True)
    status = pub.latest_transport_status()
    assert status.get("payloads_flushed_total", 0) >= 1
    assert status.get("bytes_flushed_total", 0) >= 1
    assert status.get("last_batch_count", 0) >= 1
    # Duration may be 0 in extremely fast environments but key should exist
    assert "last_flush_duration_ms" in status


def test_backpressure_drop_increments_dropped_messages() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    # Force extremely small buffer to trigger drop_oldest on enqueue
    config.telemetry.transport.buffer.max_buffer_bytes = 8
    pub = TelemetryPublisher(config)
    try:
        pub.emit_event("loop.failure", _failure_payload(1, error="overflow"))
        _sleep_brief()
    finally:
        pub.stop_worker(wait=True)
    status = pub.latest_transport_status()
    assert status.get("dropped_messages", 0) >= 1

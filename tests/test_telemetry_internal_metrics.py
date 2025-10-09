from __future__ import annotations

import time
from pathlib import Path

from townlet.config import load_config
from townlet.telemetry.publisher import TelemetryPublisher


def _sleep_brief() -> None:
    # Allow the worker thread to process a flush
    time.sleep(0.2)


def test_worker_flush_counters_increment() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    pub = TelemetryPublisher(config)
    try:
        # Trigger a few small payloads via loop failure events
        for i in range(3):
            pub.emit_event("loop.failure", {"tick": i + 1, "error": "simulated"})
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
        pub.emit_event("loop.failure", {"tick": 1, "error": "overflow"})
        _sleep_brief()
    finally:
        pub.stop_worker(wait=True)
    status = pub.latest_transport_status()
    assert status.get("dropped_messages", 0) >= 1

from __future__ import annotations

import threading
import time
import types

from townlet.config.loader import TelemetryRetryPolicy
from townlet.telemetry.transport import TransportBuffer
from townlet.telemetry.worker import TelemetryWorkerManager


def _status_template() -> dict[str, object]:
    return {
        "connected": False,
        "dropped_messages": 0,
        "last_error": None,
        "last_failure_tick": None,
        "last_success_tick": None,
        "queue_length": 0,
        "last_flush_duration_ms": None,
        "worker_alive": False,
        "worker_error": None,
        "worker_restart_count": 0,
        "last_worker_error": None,
        "auth_enabled": False,
    }


def test_worker_manager_fan_out_handles_overflow() -> None:
    status = _status_template()
    send_calls: list[tuple[str, bytes]] = []

    def send_payload(payload: bytes) -> None:
        send_calls.append((threading.current_thread().name, payload))

    manager = TelemetryWorkerManager(
        buffer=TransportBuffer(max_batch_size=4, max_buffer_bytes=12),
        retry_policy=TelemetryRetryPolicy(),
        status=status,
        send_callable=send_payload,
        reset_callable=lambda: None,
        poll_interval_seconds=0.05,
        flush_interval_ticks=1,
        backpressure_strategy="fan_out",
    )

    manager.start()
    manager.enqueue(b"aaaaa", tick=1)
    manager.enqueue(b"bbbbb", tick=2)
    manager.enqueue(b"ccccc", tick=3)
    time.sleep(0.1)
    manager.close()

    assert any(name != "telemetry-flush" for name, _ in send_calls)
    assert status["dropped_messages"] == 0


def test_worker_manager_block_strategy_drops_when_stalled(monkeypatch) -> None:
    status = _status_template()
    send_calls: list[bytes] = []

    def send_payload(payload: bytes) -> None:
        send_calls.append(payload)

    manager = TelemetryWorkerManager(
        buffer=TransportBuffer(max_batch_size=2, max_buffer_bytes=10),
        retry_policy=TelemetryRetryPolicy(),
        status=status,
        send_callable=send_payload,
        reset_callable=lambda: None,
        poll_interval_seconds=0.05,
        flush_interval_ticks=1,
        backpressure_strategy="block",
        block_timeout_seconds=0.05,
    )

    manager.start()

    monkeypatch.setattr(
        manager,
        "_flush_pending",
        types.MethodType(lambda self: None, manager),
    )

    manager.enqueue(b"111111", tick=1)
    start = time.perf_counter()
    manager.enqueue(b"222222", tick=2)
    duration = time.perf_counter() - start
    manager.close()

    assert status["dropped_messages"] >= 1
    assert duration >= 0.05
    assert not send_calls  # no payloads flushed while stalled

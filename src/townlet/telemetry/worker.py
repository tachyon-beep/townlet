"""Worker management for telemetry transport flushing."""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from collections.abc import Callable
from typing import Any, Literal

from townlet.config.loader import TelemetryRetryPolicy
from townlet.telemetry.transport import TransportBuffer

logger = logging.getLogger(__name__)

BackpressureStrategy = Literal["drop_oldest", "block", "fan_out"]


class TelemetryWorkerManager:
    """Coordinate background flushing of telemetry payloads to transports."""

    def __init__(
        self,
        *,
        buffer: TransportBuffer,
        retry_policy: TelemetryRetryPolicy,
        status: dict[str, Any],
        send_callable: Callable[[bytes], None],
        reset_callable: Callable[[], None],
        poll_interval_seconds: float,
        flush_interval_ticks: int,
        backpressure_strategy: BackpressureStrategy = "drop_oldest",
        block_timeout_seconds: float = 0.5,
        restart_limit: int = 3,
    ) -> None:
        self._buffer = buffer
        self._retry_policy = retry_policy
        self._status = status
        self._send_callable = send_callable
        self._reset_callable = reset_callable
        self._poll_interval_seconds = max(0.01, float(poll_interval_seconds))
        self._flush_interval_ticks = max(1, int(flush_interval_ticks))
        self._backpressure_strategy = backpressure_strategy
        self._block_timeout_seconds = max(0.01, float(block_timeout_seconds))
        self._restart_limit = max(1, int(restart_limit))

        self._buffer_lock = threading.Lock()
        self._buffer_not_full = threading.Condition(self._buffer_lock)
        self._flush_event = threading.Event()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

        self._latest_enqueue_tick = 0
        self._last_flush_tick = 0
        self._shutdown = False
        self._restart_attempts = 0
        self._pending_restart = False
        self._restart_lock = threading.Lock()

    # Lifecycle -----------------------------------------------------------------
    def start(self) -> None:
        with self._restart_lock:
            if self._shutdown:
                self._shutdown = False
            if self._thread and self._thread.is_alive():
                return
            self._flush_event.clear()
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._run,
                name="telemetry-flush",
                daemon=True,
            )
            self._status["worker_alive"] = True
            self._status["worker_error"] = None
            self._thread.start()
            self._pending_restart = False

    def stop(self, *, wait: bool = True, timeout: float = 2.0) -> None:
        self._shutdown = True
        self._pending_restart = False
        if not self._stop_event.is_set():
            self._stop_event.set()
            self._flush_event.set()
        thread = self._thread
        if wait and thread is not None and thread.is_alive():
            thread.join(timeout=timeout)

    def close(self) -> None:
        self.stop(wait=True)
        self._drain_on_close()

    # Queue management -----------------------------------------------------------
    def enqueue(self, payload: bytes, *, tick: int) -> None:
        tick = int(tick)
        overflow_payloads: deque[bytes] = deque()
        with self._buffer_not_full:
            self._buffer.append(payload)
            self._latest_enqueue_tick = max(self._latest_enqueue_tick, tick)
            self._status["queue_length"] = len(self._buffer)
            # Track peak queue length and total buffered bytes
            try:
                peak = int(self._status.get("queue_length_peak", 0))
            except Exception:
                peak = 0
            if len(self._buffer) > peak:
                self._status["queue_length_peak"] = len(self._buffer)
            self._apply_backpressure_locked(overflow_payloads)
        if overflow_payloads:
            for overflow in overflow_payloads:
                self._send_in_caller(overflow, tick)
        self._flush_event.set()

    # Worker loop ----------------------------------------------------------------
    def _run(self) -> None:
        had_failure = False
        try:
            while not self._stop_event.is_set():
                triggered = self._flush_event.wait(timeout=self._poll_interval_seconds)
                self._flush_event.clear()
                if self._stop_event.is_set():
                    break
                if triggered or self._ready_to_flush():
                    self._flush_pending()
        except Exception as exc:  # pragma: no cover - defensive
            had_failure = True
            self._handle_failure(exc)
        finally:
            if not had_failure:
                try:
                    self._flush_pending()
                except Exception as exc:  # pragma: no cover - defensive
                    had_failure = True
                    self._handle_failure(exc)
            with self._buffer_not_full:
                self._status["queue_length"] = len(self._buffer)
                self._buffer_not_full.notify_all()
            self._status["worker_alive"] = False
            if not had_failure:
                self._status["worker_error"] = None
            self._thread = None
            self._maybe_restart()

    # Internal helpers -----------------------------------------------------------
    def _apply_backpressure_locked(self, overflow: deque[bytes]) -> None:
        if not self._buffer.is_over_capacity():
            return
        strategy = self._backpressure_strategy
        if strategy == "drop_oldest":
            dropped = self._buffer.drop_until_within_capacity()
            if dropped:
                self._status["dropped_messages"] += dropped
                logger.warning(
                    "Telemetry buffer exceeded %s bytes; dropped %s payloads",
                    self._buffer.max_buffer_bytes,
                    dropped,
                )
            self._status["queue_length"] = len(self._buffer)
            self._buffer_not_full.notify_all()
        elif strategy == "block":
            deadline = time.perf_counter() + (self._block_timeout_seconds * 3)
            while self._buffer.is_over_capacity() and not self._stop_event.is_set():
                remaining = deadline - time.perf_counter()
                if remaining <= 0:
                    dropped = self._buffer.drop_until_within_capacity()
                    if dropped:
                        self._status["dropped_messages"] += dropped
                        logger.warning(
                            "Telemetry buffer drop fallback; dropped %s payloads",
                            dropped,
                        )
                    self._status["queue_length"] = len(self._buffer)
                    self._buffer_not_full.notify_all()
                    break
                wait_time = min(self._block_timeout_seconds, max(0.01, remaining))
                self._flush_event.set()
                self._buffer_not_full.wait(timeout=wait_time)
            if not self._buffer.is_over_capacity():
                self._status["queue_length"] = len(self._buffer)
                self._buffer_not_full.notify_all()
        elif strategy == "fan_out":
            while self._buffer.is_over_capacity():
                overflow.append(self._buffer.popleft())
                self._status["queue_length"] = len(self._buffer)
                self._buffer_not_full.notify_all()
        else:  # pragma: no cover - defensive
            dropped = self._buffer.drop_until_within_capacity()
            if dropped:
                self._status["dropped_messages"] += dropped
            self._status["queue_length"] = len(self._buffer)
            self._buffer_not_full.notify_all()

    def _send_in_caller(self, payload: bytes, tick: int) -> None:
        if not self._send_with_retry(payload, tick):
            self._status["dropped_messages"] += 1
            logger.error("Dropping telemetry payload after fan-out send failures")

    def _ready_to_flush(self) -> bool:
        if self._flush_interval_ticks <= 1:
            return len(self._buffer) > 0
        if len(self._buffer) == 0:
            return False
        return (self._latest_enqueue_tick - self._last_flush_tick) >= self._flush_interval_ticks

    def _flush_pending(self) -> None:
        start = time.perf_counter()
        flushed_any = False
        flushed_count = 0
        flushed_bytes = 0
        tick_hint = self._latest_enqueue_tick
        while True:
            with self._buffer_not_full:
                if not len(self._buffer):
                    break
                payload = self._buffer.popleft()
                self._status["queue_length"] = len(self._buffer)
                self._buffer_not_full.notify_all()
            flushed_any = True
            flushed_count += 1
            flushed_bytes += len(payload)
            if not self._send_with_retry(payload, tick_hint):
                self._status["dropped_messages"] += 1
                logger.error("Dropping telemetry payload after repeated send failures")
                with self._buffer_not_full:
                    if len(self._buffer):
                        dropped = len(self._buffer)
                        self._status["dropped_messages"] += dropped
                        self._buffer.clear()
                        self._status["queue_length"] = 0
                        self._buffer_not_full.notify_all()
                break
        if flushed_any:
            duration_ms = (time.perf_counter() - start) * 1_000.0
            self._status["last_flush_duration_ms"] = duration_ms
            self._status["last_batch_count"] = flushed_count
            self._status["last_flush_payload_bytes"] = flushed_bytes
            # Totals
            try:
                self._status["payloads_flushed_total"] += flushed_count
                self._status["bytes_flushed_total"] += flushed_bytes
            except Exception:
                # Initialize if missing
                self._status["payloads_flushed_total"] = int(flushed_count)
                self._status["bytes_flushed_total"] = int(flushed_bytes)
            self._last_flush_tick = tick_hint

    def _send_with_retry(self, payload: bytes, tick: int) -> bool:
        attempts = 0
        max_attempts = max(0, int(self._retry_policy.max_attempts))
        backoff = max(0.0, float(self._retry_policy.backoff_seconds))
        while True:
            try:
                self._send_callable(payload)
                self._status["connected"] = True
                self._status["last_success_tick"] = int(tick)
                # Reset failure streak on success
                self._status["consecutive_send_failures"] = 0
                return True
            except Exception as exc:  # pragma: no cover - transport failure path
                message = str(exc)
                self._status["connected"] = False
                self._status["last_error"] = message
                self._status["last_failure_tick"] = int(tick)
                # Count failures
                try:
                    self._status["consecutive_send_failures"] += 1
                    self._status["send_failures_total"] += 1
                except Exception:
                    self._status["consecutive_send_failures"] = 1
                    self._status["send_failures_total"] = 1
                logger.warning(
                    "Telemetry transport send failed (attempt %s/%s): %s",
                    attempts + 1,
                    max_attempts + 1,
                    message,
                )
                if attempts >= max_attempts:
                    return False
                attempts += 1
                try:
                    self._reset_callable()
                except Exception as reset_exc:  # pragma: no cover - defensive
                    reset_msg = str(reset_exc)
                    self._status["last_error"] = reset_msg
                    logger.error("Telemetry transport reconnect failed: %s", reset_msg)
                    return False
                if backoff > 0:
                    time.sleep(backoff)

    def _handle_failure(self, exc: Exception) -> None:
        message = f"{exc.__class__.__name__}: {exc}"
        self._status["worker_error"] = message
        self._status["worker_alive"] = False
        self._status["last_failure_tick"] = int(self._latest_enqueue_tick)
        self._status["connected"] = False
        self._status["last_worker_error"] = message
        logger.critical("Telemetry flush worker failed: %s", message, exc_info=True)
        with self._restart_lock:
            if self._shutdown:
                return
            if self._restart_attempts >= self._restart_limit:
                logger.critical(
                    "Telemetry flush worker restart limit reached (%s attempts)",
                    self._restart_limit,
                )
                self._pending_restart = False
                self._stop_event.set()
                return
            self._restart_attempts += 1
            self._pending_restart = True
            self._status["worker_restart_count"] = self._restart_attempts
        logger.warning(
            "Telemetry flush worker restarting (attempt %s/%s)",
            self._restart_attempts,
            self._restart_limit,
        )
        self._flush_event.set()

    def _maybe_restart(self) -> None:
        with self._restart_lock:
            should_restart = self._pending_restart and not self._shutdown
            if should_restart:
                self._pending_restart = False
        if should_restart:
            self.start()

    def _drain_on_close(self) -> None:
        with self._buffer_not_full:
            pending = len(self._buffer)
        if pending:
            try:
                self._flush_pending()
            except Exception:  # pragma: no cover - shutdown path
                logger.debug("Telemetry worker drain failed during close", exc_info=True)

    # Inspection helpers --------------------------------------------------------
    def latest_enqueue_tick(self) -> int:
        return int(self._latest_enqueue_tick)

    def queue_length(self) -> int:
        with self._buffer_not_full:
            return len(self._buffer)

    def clear_buffer(self) -> None:
        """Clear buffered payloads while keeping status in sync."""

        with self._buffer_not_full:
            self._buffer.clear()
            self._status["queue_length"] = 0
            self._buffer_not_full.notify_all()

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.telemetry.transport import TransportBuffer


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
    world._assign_jobs_to_agents()  # type: ignore[attr-defined]


def test_transport_buffer_drop_until_capacity() -> None:
    buffer = TransportBuffer(max_batch_size=10, max_buffer_bytes=8)
    buffer.append(b"aaaaa")
    buffer.append(b"bbbbb")
    assert buffer.is_over_capacity()
    dropped = buffer.drop_until_within_capacity()
    assert dropped == 1
    assert len(buffer) == 1
    assert buffer.total_bytes <= buffer.max_buffer_bytes


def test_telemetry_publisher_flushes_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    sent: list[bytes] = []

    class CaptureTransport:
        def send(self, payload: bytes) -> None:
            sent.append(payload)

        def close(self) -> None:  # pragma: no cover - nothing to close in stub
            pass

    monkeypatch.setattr(
        "townlet.telemetry.publisher.create_transport",
        lambda **_: CaptureTransport(),
    )

    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.telemetry.transport.buffer.max_batch_size = 1
    config.telemetry.transport.buffer.flush_interval_ticks = 1

    loop = SimulationLoop(config)
    _ensure_agents(loop)

    loop.step()
    loop.telemetry.close()

    assert sent, "expected payload to be flushed via capture transport"
    payload = json.loads(sent[-1].decode("utf-8"))
    assert payload.get("schema_version", "").startswith("0.9")
    assert payload.get("tick") == loop.tick


def test_telemetry_publisher_retries_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    transports: list[object] = []
    sent: list[bytes] = []

    class FlakyTransport:
        def __init__(self, fail_first: bool) -> None:
            self.fail_first = fail_first
            self.calls = 0

        def send(self, payload: bytes) -> None:
            self.calls += 1
            if self.fail_first and self.calls == 1:
                raise RuntimeError("simulated send failure")
            sent.append(payload)

        def close(self) -> None:  # pragma: no cover - nothing to close for stub
            pass

    transports.extend([FlakyTransport(fail_first=True), FlakyTransport(fail_first=False)])

    def factory(**_: object) -> object:
        return transports.pop(0)

    monkeypatch.setattr(
        "townlet.telemetry.publisher.create_transport",
        factory,
    )

    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.telemetry.transport.buffer.max_batch_size = 1
    config.telemetry.transport.buffer.flush_interval_ticks = 1
    config.telemetry.transport.retry.max_attempts = 1
    config.telemetry.transport.retry.backoff_seconds = 0.0

    loop = SimulationLoop(config)
    _ensure_agents(loop)

    loop.step()
    loop.telemetry.close()

    assert not transports, "expected transport factory to be consumed"
    assert sent, "expected retry to succeed and emit payload"
    status = loop.telemetry.latest_transport_status()
    assert status["dropped_messages"] == 0
    assert status["last_failure_tick"] == loop.tick
    assert status["last_success_tick"] == loop.tick
    assert status["connected"] is True


def test_telemetry_worker_metrics_and_stop(monkeypatch: pytest.MonkeyPatch) -> None:
    class NoopTransport:
        def send(self, payload: bytes) -> None:  # pragma: no cover - noop
            pass

        def close(self) -> None:  # pragma: no cover - noop
            pass

    monkeypatch.setattr(
        "townlet.telemetry.publisher.create_transport",
        lambda **_: NoopTransport(),
    )

    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.telemetry.transport.buffer.max_batch_size = 4
    config.telemetry.transport.worker_poll_seconds = 0.05

    loop = SimulationLoop(config)
    _ensure_agents(loop)

    loop.step()
    time.sleep(0.1)

    status = loop.telemetry.latest_transport_status()
    assert status["queue_length"] == 0
    assert status["last_flush_duration_ms"] is None or status["last_flush_duration_ms"] >= 0.0
    assert loop.telemetry._flush_poll_interval == pytest.approx(0.05, rel=0.1)

    health = loop.telemetry.latest_health_status()
    assert health.get("tick") == loop.tick
    assert "tick_duration_ms" in health

    loop.telemetry.stop_worker(wait=True)
    loop.telemetry.stop_worker(wait=True)
    loop.telemetry.close()

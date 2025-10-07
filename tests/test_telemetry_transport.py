from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.config.loader import TelemetryTransportConfig
from townlet.core.sim_loop import SimulationLoop
from townlet.telemetry.transport import (
    TelemetryTransportError,
    TransportBuffer,
    create_transport,
)


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
    loop.close()

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
    loop.close()

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
    loop.close()


def test_tcp_transport_wraps_socket_with_tls(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, object] = {}

    class DummySocket:
        def __init__(self) -> None:
            self.timeout = None
            self.sent: list[bytes] = []
            self.closed = False

        def settimeout(self, timeout: float | None) -> None:
            self.timeout = timeout

        def sendall(self, payload: bytes) -> None:
            self.sent.append(payload)

        def close(self) -> None:
            self.closed = True

    class StubContext:
        def __init__(self) -> None:
            self.check_hostname = True
            self.loaded_cafile: str | None = None
            self.loaded_chain: tuple[str | None, str | None] | None = None
            self.wrap_calls: list[str | None] = []

        def load_verify_locations(
            self,
            cafile=None,
            capath=None,
            cadata=None,
        ):  # pragma: no cover - compatibility
            self.loaded_cafile = cafile

        def load_cert_chain(self, certfile, keyfile=None):  # pragma: no cover - optional chain
            self.loaded_chain = (certfile, keyfile)

        def wrap_socket(self, sock, server_hostname=None):
            self.wrap_calls.append(server_hostname)
            calls["wrapped_socket"] = sock
            return sock

    dummy_socket = DummySocket()

    def fake_create_connection(endpoint, timeout=None):
        calls["endpoint"] = endpoint
        calls["timeout"] = timeout
        return dummy_socket

    context = StubContext()

    monkeypatch.setattr(
        "townlet.telemetry.transport.socket.create_connection",
        fake_create_connection,
    )
    monkeypatch.setattr(
        "townlet.telemetry.transport.ssl.create_default_context",
        lambda: context,
    )

    transport = create_transport(
        transport_type="tcp",
        file_path=None,
        endpoint="demo.local:8765",
        connect_timeout=3.0,
        send_timeout=1.5,
        enable_tls=True,
        verify_hostname=True,
        ca_file=Path("certs/demo_ca.pem"),
        cert_file=None,
        key_file=None,
        allow_plaintext=False,
    )

    assert context.loaded_cafile == str(Path("certs/demo_ca.pem").expanduser())
    assert context.wrap_calls == ["demo.local"]
    transport.send(b"payload")
    assert dummy_socket.sent == [b"payload"]
    transport.close()
    assert dummy_socket.closed is True


def test_create_transport_plaintext_warning(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    calls = {}

    class DummySocket:
        def settimeout(self, timeout):
            calls["timeout"] = timeout

        def sendall(self, payload: bytes) -> None:
            calls.setdefault("payloads", []).append(payload)

        def close(self) -> None:
            calls["closed"] = True

    monkeypatch.setattr(
        "townlet.telemetry.transport.socket.create_connection",
        lambda *args, **kwargs: DummySocket(),
    )

    caplog.set_level("WARNING")
    transport = create_transport(
        transport_type="tcp",
        file_path=None,
        endpoint="plaintext.host:9000",
        connect_timeout=1.0,
        send_timeout=1.0,
        enable_tls=False,
        verify_hostname=True,
        ca_file=None,
        cert_file=None,
        key_file=None,
        allow_plaintext=True,
    )
    assert any("telemetry_tcp_plaintext_enabled" in record.message for record in caplog.records)
    transport.send(b"hello")
    transport.close()
    assert calls.get("closed") is True


def test_create_transport_plaintext_disallowed() -> None:
    with pytest.raises(TelemetryTransportError, match="Plaintext TCP transport is disabled"):
        create_transport(
            transport_type="tcp",
            file_path=None,
            endpoint="secure.host:9000",
            connect_timeout=1.0,
            send_timeout=1.0,
            enable_tls=False,
            verify_hostname=True,
            ca_file=None,
            cert_file=None,
            key_file=None,
            allow_plaintext=False,
        )


def test_tcp_transport_defaults_to_tls() -> None:
    cfg = TelemetryTransportConfig(type="tcp", endpoint="localhost:9000")
    assert cfg.enable_tls is True
    assert cfg.allow_plaintext is False


def test_tcp_transport_plaintext_requires_dev_flags() -> None:
    with pytest.raises(ValueError):
        TelemetryTransportConfig(type="tcp", endpoint="localhost:9000", allow_plaintext=True, dev_allow_plaintext=False, enable_tls=False)
    with pytest.raises(ValueError):
        TelemetryTransportConfig(type="tcp", endpoint="example.com:9000", allow_plaintext=True, dev_allow_plaintext=True, enable_tls=False)


def test_tcp_transport_plaintext_valid_for_localhost() -> None:
    cfg = TelemetryTransportConfig(type="tcp", endpoint="127.0.0.1:5000", allow_plaintext=True, dev_allow_plaintext=True, enable_tls=False)
    assert cfg.enable_tls is False
    assert cfg.allow_plaintext is True


def test_tcp_transport_ignores_plaintext_flags_when_tls_enabled() -> None:
    cfg = TelemetryTransportConfig(type="tcp", endpoint="localhost:9000", allow_plaintext=True, dev_allow_plaintext=True, enable_tls=True)
    assert cfg.enable_tls is True
    assert cfg.allow_plaintext is False
    assert cfg.dev_allow_plaintext is False

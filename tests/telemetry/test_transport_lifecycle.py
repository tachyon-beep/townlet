from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

from townlet.telemetry.transport import (
    FileTransport,
    StdoutTransport,
    TelemetryTransportError,
    TransportBuffer,
    WebsocketTransport,
)


def test_stdout_transport_start_stop(monkeypatch: pytest.MonkeyPatch) -> None:
    buffer = io.BytesIO()
    fake_stdout = io.TextIOWrapper(buffer, encoding="utf-8")
    monkeypatch.setattr(sys, "stdout", fake_stdout)

    transport = StdoutTransport()
    transport.start()
    transport.send(b"hello\n")
    transport.stop()

    assert buffer.getvalue() == b"hello\n"


def test_file_transport_writes(tmp_path: Path) -> None:
    file_path = tmp_path / "telemetry.jsonl"
    transport = FileTransport(file_path)
    transport.start()
    transport.send(b"payload-1\n")
    transport.send(b"payload-2\n")
    transport.stop()

    assert file_path.read_bytes() == b"payload-1\npayload-2\n"


def test_websocket_transport_stub() -> None:
    transport = WebsocketTransport("wss://example.local/telemetry")
    transport.start()
    with pytest.raises(TelemetryTransportError):
        transport.send(b"payload")
    transport.stop()


def test_transport_buffer_drop_until_capacity() -> None:
    buffer = TransportBuffer(max_batch_size=10, max_buffer_bytes=8)
    buffer.append(b"1234")
    buffer.append(b"5678")
    assert buffer.is_over_capacity() is False
    buffer.append(b"91011")
    assert buffer.is_over_capacity() is True
    dropped = buffer.drop_until_within_capacity()
    assert dropped >= 1
    assert buffer.total_bytes <= 8

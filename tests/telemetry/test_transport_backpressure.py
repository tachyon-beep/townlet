from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from townlet.telemetry.transport import FileTransport, TransportBuffer


def test_file_transport_concurrent_writes(tmp_path: Path) -> None:
    path = tmp_path / "buffered.jsonl"
    transport = FileTransport(path)
    transport.start()

    def writer(payload: bytes) -> None:
        for _ in range(20):
            transport.send(payload)

    threads = [threading.Thread(target=writer, args=(f"payload-{i}\n".encode(),)) for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    transport.stop()
    contents = path.read_bytes()
    assert contents.count(b"\n") == 60


def test_transport_buffer_backpressure_drop() -> None:
    buffer = TransportBuffer(max_batch_size=4, max_buffer_bytes=16)
    for i in range(6):
        buffer.append(f"payload-{i}".encode())
    assert len(buffer) == 6
    dropped = buffer.drop_until_within_capacity()
    # With 16 byte limit and >= 8 byte payloads, expect at least 4 drops
    assert dropped >= 4
    assert buffer.total_bytes <= 16


@pytest.mark.timeout(2)
def test_transport_buffer_does_not_deadlock_on_drop() -> None:
    buffer = TransportBuffer(max_batch_size=2, max_buffer_bytes=10)

    def producer() -> None:
        for i in range(100):
            buffer.append(f"x{i}".encode())
            buffer.drop_until_within_capacity()
            time.sleep(0.001)

    thread = threading.Thread(target=producer)
    thread.start()
    thread.join()
    assert buffer.total_bytes <= 10

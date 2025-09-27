"""Transport primitives for telemetry publishing."""

from __future__ import annotations

import socket
import sys
from collections import deque
from pathlib import Path
from typing import Protocol


class TelemetryTransportError(RuntimeError):
    """Raised when telemetry messages cannot be delivered."""


class TransportClient(Protocol):
    """Common interface for transport implementations."""

    def send(self, payload: bytes) -> None:  # pragma: no cover - Protocol stub
        raise NotImplementedError

    def close(self) -> None:  # pragma: no cover - Protocol stub
        raise NotImplementedError


class StdoutTransport:
    """Writes telemetry payloads to stdout (for development/debug)."""

    def __init__(self) -> None:
        self._stream = sys.stdout.buffer

    def send(self, payload: bytes) -> None:
        self._stream.write(payload)
        self._stream.flush()

    def close(self) -> None:
        self._stream.flush()


class FileTransport:
    """Appends newline-delimited payloads to a local file."""

    def __init__(self, path: Path) -> None:
        self._path = path.expanduser()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self._path.open("ab", buffering=0)

    def send(self, payload: bytes) -> None:
        self._handle.write(payload)
        self._handle.flush()

    def close(self) -> None:
        self._handle.close()


class TcpTransport:
    """Sends telemetry payloads to a TCP endpoint."""

    def __init__(
        self,
        endpoint: str,
        *,
        connect_timeout: float,
        send_timeout: float,
    ) -> None:
        host, sep, port_str = endpoint.partition(":")
        if not host or sep != ":" or not port_str:
            raise TelemetryTransportError(
                "telemetry.transport.endpoint must use host:port format"
            )
        try:
            port = int(port_str)
        except ValueError as exc:  # pragma: no cover - defensive
            raise TelemetryTransportError(
                "telemetry.transport.endpoint port must be an integer"
            ) from exc
        self._endpoint = (host.strip(), port)
        self._connect_timeout = connect_timeout
        self._send_timeout = send_timeout
        self._socket = None
        self._connect()

    def _connect(self) -> None:
        try:
            sock = socket.create_connection(
                self._endpoint, timeout=self._connect_timeout or None
            )
        except OSError as exc:  # pragma: no cover - network failure path
            host, port = self._endpoint
            raise TelemetryTransportError(
                f"Failed to connect to telemetry endpoint {host}:{port}: {exc}"
            ) from exc
        sock.settimeout(self._send_timeout or None)
        self._socket = sock

    def send(self, payload: bytes) -> None:
        if self._socket is None:
            self._connect()
        assert self._socket is not None
        try:
            self._socket.sendall(payload)
        except OSError as exc:  # pragma: no cover - socket error
            raise TelemetryTransportError(str(exc)) from exc

    def close(self) -> None:
        if self._socket is not None:
            try:
                self._socket.close()
            finally:
                self._socket = None


class TransportBuffer:
    """Accumulates payloads prior to flushing to the transport."""

    def __init__(self, *, max_batch_size: int, max_buffer_bytes: int) -> None:
        self._queue: deque[bytes] = deque()
        self._total_bytes = 0
        self.max_batch_size = max_batch_size
        self.max_buffer_bytes = max_buffer_bytes

    def append(self, payload: bytes) -> None:
        self._queue.append(payload)
        self._total_bytes += len(payload)

    def popleft(self) -> bytes:
        payload = self._queue.popleft()
        self._total_bytes -= len(payload)
        return payload

    def clear(self) -> None:
        self._queue.clear()
        self._total_bytes = 0

    def __len__(self) -> int:
        return len(self._queue)

    @property
    def total_bytes(self) -> int:
        return self._total_bytes

    def is_over_capacity(self) -> bool:
        return self._total_bytes > self.max_buffer_bytes

    def drop_until_within_capacity(self) -> int:
        """Drop oldest payloads until buffer fits limits; returns drop count."""

        dropped = 0
        while self._queue and self._total_bytes > self.max_buffer_bytes:
            payload = self._queue.popleft()
            self._total_bytes -= len(payload)
            dropped += 1
        return dropped


def create_transport(
    *,
    transport_type: str,
    file_path: Path | None,
    endpoint: str | None,
    connect_timeout: float,
    send_timeout: float,
) -> TransportClient:
    """Factory helper for `TelemetryPublisher`."""

    if transport_type == "stdout":
        return StdoutTransport()
    if transport_type == "file":
        if file_path is None:
            raise TelemetryTransportError(
                "telemetry.transport.file_path is required when using file transport"
            )
        return FileTransport(file_path)
    if transport_type == "tcp":
        if endpoint is None:
            raise TelemetryTransportError(
                "telemetry.transport.endpoint is required when using tcp transport"
            )
        return TcpTransport(
            endpoint,
            connect_timeout=connect_timeout,
            send_timeout=send_timeout,
        )
    raise TelemetryTransportError(
        f"Unsupported telemetry transport type: {transport_type}"
    )

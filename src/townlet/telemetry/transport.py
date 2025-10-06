"""Transport primitives for telemetry publishing."""

from __future__ import annotations

import logging
import socket
import ssl
import sys
from collections import deque
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)


class TelemetryTransportError(RuntimeError):
    """Raised when telemetry messages cannot be delivered."""


class BaseTransport(AbstractContextManager):
    """Common lifecycle helpers for telemetry transports."""

    def start(self) -> None:
        """Initialise resources (default no-op)."""

    def stop(self) -> None:
        """Tear down resources (default no-op)."""

    def send(self, payload: bytes) -> None:  # pragma: no cover - interface stub
        raise NotImplementedError

    # Context manager helpers -------------------------------------------------
    def __enter__(self):  # pragma: no cover - rarely used
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):  # pragma: no cover - rarely used
        self.stop()
        return False


class StdoutTransport(BaseTransport):
    """Writes telemetry payloads to stdout (for development/debug)."""

    def __init__(self) -> None:
        self._stream = None

    def start(self) -> None:
        self._stream = sys.stdout.buffer

    def stop(self) -> None:
        if self._stream is not None:
            self._stream.flush()
        self._stream = None

    def send(self, payload: bytes) -> None:
        if self._stream is None:
            raise TelemetryTransportError("StdoutTransport used before start()")
        self._stream.write(payload)
        self._stream.flush()


class FileTransport(BaseTransport):
    """Appends newline-delimited payloads to a local file."""

    def __init__(self, path: Path) -> None:
        self._path = path.expanduser()
        self._handle = None

    def start(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self._path.open("ab", buffering=0)

    def stop(self) -> None:
        if self._handle is not None:
            self._handle.close()
        self._handle = None

    def send(self, payload: bytes) -> None:
        if self._handle is None:
            raise TelemetryTransportError("FileTransport used before start()")
        self._handle.write(payload)
        self._handle.flush()


class TcpTransport(BaseTransport):
    """Sends telemetry payloads to a TCP endpoint."""

    def __init__(
        self,
        endpoint: str,
        *,
        connect_timeout: float,
        send_timeout: float,
        enable_tls: bool,
        verify_hostname: bool,
        ca_file: Path | None,
        cert_file: Path | None,
        key_file: Path | None,
        allow_plaintext: bool,
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
        self._enable_tls = enable_tls
        self._verify_hostname = verify_hostname
        self._ca_file = Path(ca_file).expanduser() if ca_file else None
        self._cert_file = Path(cert_file).expanduser() if cert_file else None
        self._key_file = Path(key_file).expanduser() if key_file else None
        self._allow_plaintext = allow_plaintext
        if not self._enable_tls and not self._allow_plaintext:
            raise TelemetryTransportError(
                "Plaintext TCP transport is disabled; enable TLS or allow plaintext explicitly"
            )
        self._ssl_context: ssl.SSLContext | None = None
        self._socket = None

    def start(self) -> None:
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
        if self._enable_tls:
            context = self._ssl_context or self._build_ssl_context()
            server_hostname = self._endpoint[0] if self._verify_hostname else None
            try:
                wrapped = context.wrap_socket(sock, server_hostname=server_hostname)
            except ssl.SSLError as exc:  # pragma: no cover - handshake failure path
                sock.close()
                raise TelemetryTransportError(str(exc)) from exc
            sock = wrapped
        self._socket = sock

    def _build_ssl_context(self) -> ssl.SSLContext:
        context = ssl.create_default_context()
        if self._ca_file is not None:
            context.load_verify_locations(cafile=str(self._ca_file))
        if not self._verify_hostname:
            context.check_hostname = False
        if self._cert_file is not None:
            context.load_cert_chain(
                certfile=str(self._cert_file),
                keyfile=str(self._key_file) if self._key_file is not None else None,
            )
        self._ssl_context = context
        return context

    def send(self, payload: bytes) -> None:
        if self._socket is None:
            self._connect()
        assert self._socket is not None
        try:
            self._socket.sendall(payload)
        except OSError as exc:  # pragma: no cover - socket error
            raise TelemetryTransportError(str(exc)) from exc

    def stop(self) -> None:
        if self._socket is not None:
            try:
                self._socket.close()
            finally:
                self._socket = None


class WebsocketTransport(BaseTransport):
    """Stub implementation for future WebSocket streaming."""

    def __init__(self, url: str) -> None:
        self._url = url
        self._started = False

    def start(self) -> None:
        logger.info("WebsocketTransport start requested url=%s (stub)", self._url)
        self._started = True

    def stop(self) -> None:
        if self._started:
            logger.info("WebsocketTransport stop requested url=%s (stub)", self._url)
        self._started = False

    def send(self, payload: bytes) -> None:
        raise TelemetryTransportError("WebsocketTransport is not implemented yet")


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
    enable_tls: bool,
    verify_hostname: bool,
    ca_file: Path | None,
    cert_file: Path | None,
    key_file: Path | None,
    allow_plaintext: bool,
    websocket_url: str | None = None,
) -> BaseTransport:
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
        if not enable_tls and allow_plaintext:
            logger.warning(
                "telemetry_tcp_plaintext_enabled endpoint=%s", endpoint
            )
        return TcpTransport(
            endpoint,
            connect_timeout=connect_timeout,
            send_timeout=send_timeout,
            enable_tls=enable_tls,
            verify_hostname=verify_hostname,
            ca_file=ca_file,
            cert_file=cert_file,
            key_file=key_file,
            allow_plaintext=allow_plaintext,
        )
    if transport_type == "websocket":
        if websocket_url is None:
            raise TelemetryTransportError(
                "telemetry.transport.websocket_url required for websocket transport"
            )
        return WebsocketTransport(websocket_url)
    raise TelemetryTransportError(
        f"Unsupported telemetry transport type: {transport_type}"
    )

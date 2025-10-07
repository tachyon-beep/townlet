from __future__ import annotations

from pathlib import Path

from townlet.telemetry.transport import (
    PrometheusTextfileTransport,
    TelemetryTransportError,
    create_transport,
)


def test_prometheus_textfile_transport_writes(tmp_path: Path) -> None:
    metrics_path = tmp_path / "telemetry.prom"
    t = PrometheusTextfileTransport(metrics_path)
    t.start()
    t.send(b"{\"tick\":1}\n")
    t.send(b"{\"tick\":2}\n")
    t.stop()
    content = metrics_path.read_text()
    assert "townlet_telemetry_messages_total" in content
    assert "townlet_telemetry_bytes_total" in content


def test_create_transport_prometheus(tmp_path: Path) -> None:
    metrics_path = tmp_path / "file.prom"
    t = create_transport(
        transport_type="prometheus",
        file_path=metrics_path,
        endpoint=None,
        connect_timeout=5.0,
        send_timeout=1.0,
        enable_tls=False,
        verify_hostname=False,
        ca_file=None,
        cert_file=None,
        key_file=None,
        allow_plaintext=False,
        websocket_url=None,
    )
    # Should be able to send payloads without raising
    t.send(b"{\"tick\":3}\n")
    t.stop()
    assert metrics_path.exists()


from __future__ import annotations

import logging
from pathlib import Path

from townlet.config import ConsoleAuthConfig, ConsoleAuthTokenConfig, load_config
from townlet.telemetry.publisher import TelemetryPublisher


def _config_with_auth() -> TelemetryPublisher:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    console_auth = ConsoleAuthConfig(
        enabled=True,
        tokens=[
            ConsoleAuthTokenConfig(token="viewer-token", role="viewer", label="viewer"),
            ConsoleAuthTokenConfig(token="admin-token", role="admin", label="admin"),
        ],
    )
    config = config.model_copy(update={"console_auth": console_auth})
    return TelemetryPublisher(config)


def test_console_command_requires_token_when_enabled() -> None:
    publisher = _config_with_auth()
    try:
        publisher.queue_console_command({"name": "telemetry_snapshot"})
        results = publisher.latest_console_results()
        assert results, "Expected an unauthorized console result"
        error = results[0]["error"]
        assert error["code"] == "unauthorized"
        assert publisher.export_console_buffer() == []
    finally:
        publisher.close()


def test_console_command_accepts_valid_viewer_token() -> None:
    publisher = _config_with_auth()
    try:
        publisher.queue_console_command(
            {"name": "telemetry_snapshot", "auth": {"token": "viewer-token"}}
        )
        queued = list(publisher.drain_console_buffer())
        assert len(queued) == 1
        payload = queued[0]
        assert payload["mode"] == "viewer"
        assert "auth" not in payload
        assert payload["issuer"] == "viewer"
    finally:
        publisher.close()


def test_console_command_assigns_admin_role() -> None:
    publisher = _config_with_auth()
    try:
        publisher.queue_console_command(
            {
                "name": "telemetry_snapshot",
                "mode": "viewer",
                "auth": {"token": "admin-token"},
            }
        )
        queued = list(publisher.drain_console_buffer())
        assert len(queued) == 1
        payload = queued[0]
        assert payload["mode"] == "admin"
        assert payload["issuer"] == "admin"
    finally:
        publisher.close()


def test_console_command_forces_viewer_when_auth_disabled() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    publisher = TelemetryPublisher(config)
    try:
        publisher.queue_console_command({"name": "telemetry_snapshot", "mode": "admin"})
        queued = list(publisher.drain_console_buffer())
        assert len(queued) == 1
        payload = queued[0]
        assert payload["mode"] == "viewer"
        assert "auth" not in payload
    finally:
        publisher.close()


def test_console_command_rejects_invalid_token() -> None:
    publisher = _config_with_auth()
    try:
        publisher.queue_console_command(
            {
                "name": "telemetry_snapshot",
                "auth": {"token": "not-the-right-token"},
            }
        )
        results = publisher.latest_console_results()
        assert results and results[0]["error"]["code"] == "unauthorized"
        assert publisher.export_console_buffer() == []
    finally:
        publisher.close()


def test_console_command_warns_when_admin_requested_with_auth_disabled(caplog) -> None:
    caplog.set_level(logging.WARNING, "townlet.console.auth")
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    publisher = TelemetryPublisher(config)
    try:
        publisher.queue_console_command({"name": "telemetry_snapshot", "mode": "admin"})
        queued = list(publisher.drain_console_buffer())
        assert len(queued) == 1
        payload = queued[0]
        assert payload["mode"] == "viewer"
        assert any(
            "console_admin_request_blocked" in record.getMessage()
            for record in caplog.records
            if record.name == "townlet.console.auth"
        )
    finally:
        publisher.close()

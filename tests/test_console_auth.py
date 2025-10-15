from __future__ import annotations

import logging

import pytest

from townlet.config import ConsoleAuthConfig, ConsoleAuthTokenConfig
from townlet.console.auth import ConsoleAuthenticationError, ConsoleAuthenticator


def test_console_authenticator_rejects_command_without_token_when_enabled() -> None:
    config = ConsoleAuthConfig(
        enabled=True,
        tokens=[
            ConsoleAuthTokenConfig(token="viewer-token", role="viewer", label="viewer"),
            ConsoleAuthTokenConfig(token="admin-token", role="admin", label="admin"),
        ],
    )
    authenticator = ConsoleAuthenticator(config)

    with pytest.raises(ConsoleAuthenticationError) as exc_info:
        authenticator.authorise({"name": "telemetry_snapshot"})

    assert exc_info.value.identity["name"] == "telemetry_snapshot"
    assert "authentication token" in exc_info.value.message.lower()


def test_console_authenticator_accepts_valid_viewer_token() -> None:
    config = ConsoleAuthConfig(
        enabled=True,
        tokens=[
            ConsoleAuthTokenConfig(token="viewer-token", role="viewer", label="viewer"),
            ConsoleAuthTokenConfig(token="admin-token", role="admin", label="admin"),
        ],
    )
    authenticator = ConsoleAuthenticator(config)

    payload, principal = authenticator.authorise(
        {"name": "telemetry_snapshot", "auth": {"token": "viewer-token"}}
    )

    assert principal is not None
    assert principal.role == "viewer"
    assert principal.label == "viewer"
    assert payload["mode"] == "viewer"
    assert "auth" not in payload
    assert payload["issuer"] == "viewer"


def test_console_authenticator_assigns_admin_role() -> None:
    config = ConsoleAuthConfig(
        enabled=True,
        tokens=[
            ConsoleAuthTokenConfig(token="viewer-token", role="viewer", label="viewer"),
            ConsoleAuthTokenConfig(token="admin-token", role="admin", label="admin"),
        ],
    )
    authenticator = ConsoleAuthenticator(config)

    payload, principal = authenticator.authorise(
        {
            "name": "telemetry_snapshot",
            "mode": "viewer",  # Should be overridden by token role
            "auth": {"token": "admin-token"},
        }
    )

    assert principal is not None
    assert principal.role == "admin"
    assert principal.label == "admin"
    assert payload["mode"] == "admin"
    assert payload["issuer"] == "admin"


def test_console_authenticator_rejects_admin_when_auth_disabled(caplog) -> None:
    caplog.set_level(logging.WARNING, "townlet.console.auth")
    config = ConsoleAuthConfig(enabled=False, tokens=[])
    authenticator = ConsoleAuthenticator(config)

    with pytest.raises(ConsoleAuthenticationError) as exc_info:
        authenticator.authorise({"name": "telemetry_snapshot", "mode": "admin"})

    assert "admin" in exc_info.value.message.lower()
    assert any(
        "console_admin_request_rejected" in record.getMessage()
        for record in caplog.records
        if record.name == "townlet.console.auth"
    )


def test_console_authenticator_rejects_invalid_token() -> None:
    config = ConsoleAuthConfig(
        enabled=True,
        tokens=[
            ConsoleAuthTokenConfig(token="viewer-token", role="viewer", label="viewer"),
            ConsoleAuthTokenConfig(token="admin-token", role="admin", label="admin"),
        ],
    )
    authenticator = ConsoleAuthenticator(config)

    with pytest.raises(ConsoleAuthenticationError) as exc_info:
        authenticator.authorise(
            {
                "name": "telemetry_snapshot",
                "auth": {"token": "not-the-right-token"},
            }
        )

    assert "invalid" in exc_info.value.message.lower()


def test_console_authenticator_warns_when_admin_requested_with_auth_disabled(caplog) -> None:
    caplog.set_level(logging.WARNING, "townlet.console.auth")
    config = ConsoleAuthConfig(enabled=False, tokens=[])
    authenticator = ConsoleAuthenticator(config)

    with pytest.raises(ConsoleAuthenticationError):
        authenticator.authorise({"name": "telemetry_snapshot", "mode": "admin"})

    assert any(
        "console_admin_request_rejected" in record.getMessage()
        for record in caplog.records
        if record.name == "townlet.console.auth"
    )


def test_console_authenticator_allows_viewer_when_disabled() -> None:
    """When auth is disabled, viewer commands should be allowed."""
    config = ConsoleAuthConfig(enabled=False, tokens=[])
    authenticator = ConsoleAuthenticator(config)

    payload, principal = authenticator.authorise(
        {"name": "telemetry_snapshot", "mode": "viewer"}
    )

    assert principal is not None
    assert principal.role == "viewer"
    assert payload["mode"] == "viewer"


def test_console_authenticator_sanitizes_auth_section() -> None:
    """Auth section should be removed from sanitized payload."""
    config = ConsoleAuthConfig(
        enabled=True,
        tokens=[ConsoleAuthTokenConfig(token="secret", role="admin", label="test")],
    )
    authenticator = ConsoleAuthenticator(config)

    payload, _ = authenticator.authorise(
        {"name": "snapshot", "auth": {"token": "secret", "extra": "data"}}
    )

    assert "auth" not in payload
    assert "extra" not in payload

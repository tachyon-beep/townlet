"""Authentication helpers for console and telemetry command ingress."""

from __future__ import annotations

import logging
import os
import secrets
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from townlet.config import ConsoleAuthConfig, ConsoleAuthTokenConfig, ConsoleMode

__all__ = ["AuthPrincipal", "ConsoleAuthenticationError", "ConsoleAuthenticator"]

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuthPrincipal:
    """Represents an authenticated caller."""

    role: ConsoleMode
    label: str | None = None


class ConsoleAuthenticationError(Exception):
    """Raised when authentication of a console command fails."""

    def __init__(self, message: str, identity: dict[str, str | None]) -> None:
        super().__init__(message)
        self.identity = identity
        self.message = message


class ConsoleAuthenticator:
    """Authenticates console command payloads using configured tokens."""

    _warned_disabled: bool = False

    def __init__(self, config: ConsoleAuthConfig) -> None:
        self._config = config
        self.enabled = bool(config.enabled)
        self.require_auth_for_viewer = bool(config.require_auth_for_viewer)
        self._token_table: dict[str, AuthPrincipal] = {}
        if not self.enabled and not ConsoleAuthenticator._warned_disabled:
            logger.warning(
                "console_auth_disabled role=viewer "
                "message='Admin commands require tokens; console auth is disabled.'"
            )
            ConsoleAuthenticator._warned_disabled = True
        if self.enabled:
            self._load_tokens(config.tokens)

    def _load_tokens(self, entries: list[ConsoleAuthTokenConfig]) -> None:
        for entry in entries:
            token_value = entry.token
            if token_value is None:
                env_name = entry.token_env or ""
                token_value = os.getenv(env_name, "")
                if not token_value:
                    raise ValueError(
                        f"console.auth token_env '{env_name}' is not set or is empty"
                    )
            if token_value in self._token_table:
                raise ValueError("Duplicate console auth token detected")
            label = entry.label or entry.token_env or None
            self._token_table[token_value] = AuthPrincipal(role=entry.role, label=label)

    @staticmethod
    def _to_mapping(command: object) -> dict[str, Any]:
        if isinstance(command, Mapping):
            return dict(command)
        if hasattr(command, "__dict__"):
            attrs = {
                key: getattr(command, key)
                for key in dir(command)
                if not key.startswith("_")
            }
            return {
                key: value
                for key, value in attrs.items()
                if key
                in {
                    "name",
                    "cmd",
                    "args",
                    "kwargs",
                    "cmd_id",
                    "issuer",
                    "mode",
                    "auth",
                    "metadata",
                }
            }
        raise TypeError("Console command payload must be a mapping or attribute-based object")

    @staticmethod
    def _identity(payload: Mapping[str, Any]) -> dict[str, str | None]:
        name = payload.get("name") or payload.get("cmd") or "unknown"
        cmd_id = payload.get("cmd_id")
        issuer = payload.get("issuer")
        return {
            "name": str(name) if name is not None else "unknown",
            "cmd_id": str(cmd_id) if isinstance(cmd_id, str) else None,
            "issuer": str(issuer) if isinstance(issuer, str) else None,
        }

    @staticmethod
    def _normalise_role(value: object, *, default: ConsoleMode = "viewer") -> ConsoleMode:
        if isinstance(value, str):
            lowered = value.lower()
            if lowered in {"viewer", "admin"}:
                return lowered  # type: ignore[return-value]
        return default

    def authorise(self, command: object) -> tuple[dict[str, Any], AuthPrincipal | None]:
        """Validate a console payload and return the sanitised mapping + principal."""

        payload = self._to_mapping(command)
        identity = self._identity(payload)
        if not self.enabled:
            requested = self._normalise_role(payload.get("mode"))
            if requested == "admin":
                logger.warning(
                    "console_admin_request_rejected name=%s issuer=%s reason=auth_disabled",
                    identity.get("name"),
                    identity.get("issuer"),
                )
                raise ConsoleAuthenticationError(
                    "Console admin commands require authentication", identity
                )
            safe_payload = dict(payload)
            safe_payload.pop("auth", None)
            safe_payload["mode"] = "viewer"
            return safe_payload, AuthPrincipal(role="viewer", label=None)

        auth_section = payload.get("auth")
        token_value: str | None = None
        if isinstance(auth_section, Mapping):
            raw = auth_section.get("token")
            if isinstance(raw, str):
                token_value = raw.strip()
        if not token_value:
            if not self.require_auth_for_viewer and self._normalise_role(payload.get("mode")) == "viewer":
                safe_payload = dict(payload)
                safe_payload.pop("auth", None)
                safe_payload["mode"] = "viewer"
                return safe_payload, AuthPrincipal(role="viewer", label=None)
            raise ConsoleAuthenticationError("Missing authentication token", identity)

        principal = None
        for candidate, stored in self._token_table.items():
            if secrets.compare_digest(candidate, token_value):
                principal = stored
                break
        if principal is None:
            raise ConsoleAuthenticationError("Invalid authentication token", identity)

        safe_payload = dict(payload)
        safe_payload.pop("auth", None)
        safe_payload["mode"] = principal.role
        if principal.label:
            safe_payload["issuer"] = principal.label
        return safe_payload, principal

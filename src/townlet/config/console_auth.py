"""Console authentication configuration models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

ConsoleMode = Literal["viewer", "admin"]


class ConsoleAuthTokenConfig(BaseModel):
    """Configuration entry for a single console authentication token."""

    label: str | None = None
    role: ConsoleMode = "viewer"
    token: str | None = None
    token_env: str | None = None

    @model_validator(mode="after")
    def _validate_token_source(self) -> ConsoleAuthTokenConfig:
        provided = [value for value in (self.token, self.token_env) if value]
        if len(provided) != 1:
            raise ValueError("console.auth.tokens entries must define exactly one of 'token' or 'token_env'")
        if self.token is not None and not self.token.strip():
            raise ValueError("console.auth.tokens.token must not be blank")
        if self.token_env is not None and not self.token_env.strip():
            raise ValueError("console.auth.tokens.token_env must not be blank")
        return self


class ConsoleAuthConfig(BaseModel):
    """Authentication settings for console and telemetry command ingress."""

    enabled: bool = False
    require_auth_for_viewer: bool = True
    tokens: list[ConsoleAuthTokenConfig] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_tokens(self) -> ConsoleAuthConfig:
        if self.enabled and not self.tokens:
            raise ValueError("console.auth.tokens must be provided when auth is enabled")
        return self


__all__ = ["ConsoleAuthConfig", "ConsoleAuthTokenConfig", "ConsoleMode"]


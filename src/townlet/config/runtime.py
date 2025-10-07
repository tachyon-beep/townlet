"""Runtime provider configuration models.

Contains provider descriptors consumed by factory registries. Kept separate
from the loader orchestration to avoid cycles and centralize validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RuntimeProviderConfig(BaseModel):
    """Selects a runtime provider registered in the factory registry."""

    provider: str = "default"
    options: dict[str, object] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def _coerce_mapping(cls, value: object) -> object:
        if isinstance(value, str):
            return {"provider": value}
        return value

    @model_validator(mode="after")
    def _validate_provider(self) -> RuntimeProviderConfig:
        provider = str(self.provider).strip()
        if not provider:
            raise ValueError("runtime provider must not be blank")
        self.provider = provider
        if not isinstance(self.options, dict):
            raise TypeError("runtime.options must be a mapping")
        return self


class RuntimeProviders(BaseModel):
    """Grouping of runtime provider descriptors."""

    world: RuntimeProviderConfig = Field(default_factory=lambda: RuntimeProviderConfig(provider="default"))
    policy: RuntimeProviderConfig = Field(default_factory=lambda: RuntimeProviderConfig(provider="scripted"))
    telemetry: RuntimeProviderConfig = Field(default_factory=lambda: RuntimeProviderConfig(provider="stdout"))

    model_config = ConfigDict(extra="allow")


__all__ = ["RuntimeProviderConfig", "RuntimeProviders"]


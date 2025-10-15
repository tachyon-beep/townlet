"""Helper utilities for working with resolved runtime providers."""

from __future__ import annotations

from typing import Protocol


class _ProviderCarrier(Protocol):
    @property
    def provider_info(self) -> dict[str, str]: ...


def _provider_lookup(loop: object, key: str, fallback_attr: str) -> str:
    info = getattr(loop, "provider_info", None)
    if isinstance(info, dict):
        return str(info.get(key, "unknown") or "unknown")
    if info is not None:
        getter = getattr(info, "get", None)
        if callable(getter):
            value = getter(key, "unknown")
            if value:
                return str(value)
    attr_value = getattr(loop, fallback_attr, None)
    if attr_value:
        return str(attr_value)
    return "unknown"


def policy_provider_name(loop: _ProviderCarrier) -> str:
    return _provider_lookup(loop, "policy", "_policy_provider")


def telemetry_provider_name(loop: _ProviderCarrier) -> str:
    return _provider_lookup(loop, "telemetry", "_telemetry_provider")

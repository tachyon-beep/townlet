"""Helper utilities for working with resolved runtime providers."""

from __future__ import annotations

from typing import Protocol

from townlet.core.interfaces import PolicyBackendProtocol, TelemetrySinkProtocol
from townlet.policy.fallback import StubPolicyBackend
from townlet.telemetry.fallback import StubTelemetrySink


class _ProviderCarrier(Protocol):
    @property
    def provider_info(self) -> dict[str, str]: ...


def _provider_lookup(loop: object, key: str, fallback_attr: str) -> str:
    info = getattr(loop, "provider_info", None)
    if isinstance(info, dict):
        return str(info.get(key, "unknown") or "unknown")
    if info is not None:
        try:
            value = info.get(key, "unknown")  # type: ignore[attr-defined]
            if value:
                return str(value)
        except AttributeError:
            pass
    attr_value = getattr(loop, fallback_attr, None)
    if attr_value:
        return str(attr_value)
    return "unknown"


def policy_provider_name(loop: _ProviderCarrier) -> str:
    return _provider_lookup(loop, "policy", "_policy_provider")


def telemetry_provider_name(loop: _ProviderCarrier) -> str:
    return _provider_lookup(loop, "telemetry", "_telemetry_provider")


def is_stub_policy(policy: PolicyBackendProtocol, provider: str | None = None) -> bool:
    if provider is not None and provider != "stub":
        return False
    return isinstance(policy, StubPolicyBackend)


def is_stub_telemetry(telemetry: TelemetrySinkProtocol, provider: str | None = None) -> bool:
    if provider is not None and provider != "stub":
        return False
    return isinstance(telemetry, StubTelemetrySink)

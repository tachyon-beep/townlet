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


def is_stub_policy(policy: PolicyBackendProtocol, provider: str | None = None) -> bool:
    # Check if policy is directly a stub
    if isinstance(policy, StubPolicyBackend):
        return True
    # Check if policy is an adapter wrapping a stub backend
    backend = getattr(policy, "_backend", None)
    if backend is not None and isinstance(backend, StubPolicyBackend):
        return True
    # Check if provider name indicates stub
    if provider is None:
        return False
    return provider == "stub"


def is_stub_telemetry(telemetry: TelemetrySinkProtocol, provider: str | None = None) -> bool:
    if isinstance(telemetry, StubTelemetrySink):
        return True
    if provider is None:
        return False
    return provider == "stub"

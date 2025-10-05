"""Helper utilities for working with resolved runtime providers."""

from __future__ import annotations

from typing import Protocol

from townlet.core.interfaces import PolicyBackendProtocol, TelemetrySinkProtocol
from townlet.policy.fallback import StubPolicyBackend
from townlet.telemetry.fallback import StubTelemetrySink


class _ProviderCarrier(Protocol):
    @property
    def provider_info(self) -> dict[str, str]: ...


def policy_provider_name(loop: _ProviderCarrier) -> str:
    return loop.provider_info.get("policy", "unknown")


def telemetry_provider_name(loop: _ProviderCarrier) -> str:
    return loop.provider_info.get("telemetry", "unknown")


def is_stub_policy(policy: PolicyBackendProtocol, provider: str | None = None) -> bool:
    if provider is not None and provider != "stub":
        return False
    return isinstance(policy, StubPolicyBackend)


def is_stub_telemetry(telemetry: TelemetrySinkProtocol, provider: str | None = None) -> bool:
    if provider is not None and provider != "stub":
        return False
    return isinstance(telemetry, StubTelemetrySink)

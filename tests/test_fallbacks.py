from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from townlet.config import RuntimeProviderConfig, RuntimeProviders, load_config
from townlet.core import (
    SimulationLoop,
    is_stub_policy,
    is_stub_telemetry,
    policy_provider_name,
    telemetry_provider_name,
)
from townlet.core import factory_registry as registry
from townlet.factories import policy_factory
from townlet.policy.fallback import StubPolicyBackend
from townlet.telemetry.fallback import StubTelemetrySink


@pytest.fixture(scope="module")
def sample_config() -> Any:
    return load_config(Path("configs/examples/poc_hybrid.yaml"))


def test_policy_stub_resolution(sample_config: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    # Monkeypatch torch_available in the policy_factory module where it's actually used
    monkeypatch.setattr(policy_factory, "torch_available", lambda: False)
    runtime_overrides = RuntimeProviders(
        policy=RuntimeProviderConfig(provider="pytorch"),
    )
    config = sample_config.model_copy(update={"runtime": runtime_overrides})

    loop = SimulationLoop(config)
    try:
        # Note: loop.policy is PolicyRuntime, not StubPolicyBackend directly
        # The stub fallback is wrapped by the policy port adapter (ScriptedPolicyAdapter)
        # which wraps a StubPolicyBackend when torch is unavailable
        provider = policy_provider_name(loop)
        assert provider == "pytorch"
        # Verify the stub flag is set correctly by checking the port adapter
        assert is_stub_policy(loop._policy_port, provider)
    finally:
        if hasattr(loop, "close"):
            loop.close()


def test_telemetry_stub_resolution(sample_config: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(registry, "_httpx_available", lambda: False)
    runtime_overrides = RuntimeProviders(
        telemetry=RuntimeProviderConfig(provider="http"),
    )
    config = sample_config.model_copy(update={"runtime": runtime_overrides})

    loop = SimulationLoop(config)
    try:
        assert isinstance(loop.telemetry, StubTelemetrySink)
        provider = telemetry_provider_name(loop)
        assert provider == "http"
        assert is_stub_telemetry(loop.telemetry, provider)
    finally:
        if hasattr(loop.telemetry, "close"):
            loop.close()

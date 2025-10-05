from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from townlet.config import RuntimeProviderConfig, RuntimeProviders, load_config
from townlet.core import SimulationLoop
from townlet.core import factory_registry as registry
from townlet.policy.fallback import StubPolicyBackend
from townlet.telemetry.fallback import StubTelemetrySink


@pytest.fixture(scope="module")
def sample_config() -> Any:
    return load_config(Path("configs/examples/poc_hybrid.yaml"))


def test_policy_stub_resolution(sample_config: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(registry, "torch_available", lambda: False)
    runtime_overrides = RuntimeProviders(
        policy=RuntimeProviderConfig(provider="pytorch"),
    )
    config = sample_config.model_copy(update={"runtime": runtime_overrides})

    loop = SimulationLoop(config)
    try:
        assert isinstance(loop.policy, StubPolicyBackend)
    finally:
        if hasattr(loop.telemetry, "close"):
            loop.telemetry.close()


def test_telemetry_stub_resolution(sample_config: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(registry, "_httpx_available", lambda: False)
    runtime_overrides = RuntimeProviders(
        telemetry=RuntimeProviderConfig(provider="http"),
    )
    config = sample_config.model_copy(update={"runtime": runtime_overrides})

    loop = SimulationLoop(config)
    try:
        assert isinstance(loop.telemetry, StubTelemetrySink)
    finally:
        if hasattr(loop.telemetry, "close"):
            loop.telemetry.close()

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import pytest

from townlet.adapters.policy_scripted import ScriptedPolicyAdapter
from townlet.config import RuntimeProviderConfig, RuntimeProviders, load_config
from townlet.console.command import ConsoleCommandEnvelope, ConsoleCommandResult
from townlet.core import (
    SimulationLoop,
    policy_registry,
    resolve_policy,
    resolve_telemetry,
    resolve_world,
    telemetry_registry,
)
from townlet.core.interfaces import PolicyBackendProtocol, TelemetrySinkProtocol
from townlet.core.utils import (
    is_stub_policy,
    is_stub_telemetry,
    policy_provider_name,
    telemetry_provider_name,
)
from townlet.factories import registry as port_registry_module
from townlet.factories.registry import available as factory_available
from townlet.factories.registry import register as factory_register
from townlet.lifecycle.manager import LifecycleManager
from townlet.policy import DEFAULT_POLICY_PROVIDER, resolve_policy_backend
from townlet.ports.world import WorldRuntime
from townlet.scheduler.perturbations import PerturbationScheduler


class _StubWorld:
    def __init__(self) -> None:
        self.tick = 0
        self._console_results: list[ConsoleCommandResult] = []
        self._events: list[dict[str, object]] = []

    def apply_console(self, operations: Iterable[ConsoleCommandEnvelope]) -> None:
        _ = list(operations)

    def consume_console_results(self) -> list[ConsoleCommandResult]:
        return list(self._console_results)

    def apply_actions(self, actions: Mapping[str, object]) -> None:
        _ = dict(actions)

    def resolve_affordances(self, *, current_tick: int) -> None:
        _ = current_tick

    def apply_nightly_reset(self) -> None:
        return None

    def drain_events(self) -> list[dict[str, object]]:
        return list(self._events)


class _StubLifecycle(LifecycleManager):
    def __init__(self) -> None:  # pragma: no cover - minimal params
        pass

    def process_respawns(self, world: _StubWorld, *, tick: int) -> None:  # type: ignore[override]
        _ = world, tick

    def evaluate(self, world: _StubWorld, *, tick: int) -> dict[str, bool]:  # type: ignore[override]
        _ = world, tick
        return {}

    def termination_reasons(self) -> dict[str, str]:  # type: ignore[override]
        return {}


class _StubPerturbations(PerturbationScheduler):
    def __init__(self) -> None:  # pragma: no cover - minimal params
        pass

    def tick(self, world: _StubWorld, *, current_tick: int) -> None:  # type: ignore[override]
        _ = world, current_tick


class _StubPolicy(PolicyBackendProtocol):  # type: ignore[misc]
    def __init__(self, config: Any | None = None, backend: Any | None = None) -> None:
        self.config = config
        self.backend = backend
        self.reset_callback: Any | None = None

    def register_ctx_reset_callback(self, callback: Any | None) -> None:
        self.reset_callback = callback

    def enable_anneal_blend(self, enabled: bool) -> None:
        _ = enabled

    def set_anneal_ratio(self, ratio: float | None) -> None:
        _ = ratio

    def reset_state(self) -> None:
        return None

    def seed_anneal_rng(self, seed: int) -> None:
        _ = seed

    def set_policy_action_provider(self, provider: Any) -> None:
        _ = provider

    def decide(
        self,
        world: Any,
        tick: int,
        *,
        envelope: Any | None = None,
        observations: Mapping[str, object] | None = None,
    ) -> Mapping[str, object]:
        _ = world, tick, envelope, observations
        return {}

    def post_step(self, rewards: Mapping[str, float], terminated: Mapping[str, bool]) -> None:
        _ = rewards, terminated

    def flush_transitions(self, observations: Mapping[str, object]) -> None:
        _ = observations

    def latest_policy_snapshot(self) -> Mapping[str, Mapping[str, object]]:
        return {}

    def possessed_agents(self) -> list[str]:
        return []

    def consume_option_switch_counts(self) -> Mapping[str, int]:
        return {}

    def active_policy_hash(self) -> str | None:
        return None

    def current_anneal_ratio(self) -> float | None:
        return None

    def supports_observation_envelope(self) -> bool:
        return True


@pytest.fixture(autouse=True)
def restore_factory_registries() -> None:
    registry = policy_registry()
    telemetry_reg = telemetry_registry()
    original_policy = dict(registry._providers)  # type: ignore[attr-defined]
    original_telemetry = dict(telemetry_reg._providers)  # type: ignore[attr-defined]
    original_ports = {
        kind: dict(providers)
        for kind, providers in port_registry_module._REGISTRY.items()
    }
    yield
    registry._providers = dict(original_policy)  # type: ignore[attr-defined]
    telemetry_reg._providers = dict(original_telemetry)  # type: ignore[attr-defined]
    port_registry_module._REGISTRY.clear()
    for kind, providers in original_ports.items():
        port_registry_module._REGISTRY[kind] = dict(providers)


class _StubTelemetry(TelemetrySinkProtocol):  # type: ignore[misc]
    def __init__(self, config: Any, publisher: Any | None = None) -> None:
        self.config = config
        self.publisher = publisher
        self.console: list[object] = []

    def set_runtime_variant(self, variant: str | None) -> None:
        _ = variant

    def update_policy_identity(self, identity: Mapping[str, object] | None) -> None:
        _ = identity

    def emit_event(self, name: str, payload: Mapping[str, object] | None = None) -> None:
        _ = (name, payload)

    def drain_console_buffer(self) -> Iterable[object]:
        buffer = list(self.console)
        self.console.clear()
        return buffer

    def latest_queue_metrics(self) -> Mapping[str, int] | None:
        return {}

    def latest_embedding_metrics(self) -> Mapping[str, object] | None:
        return {}

    def latest_job_snapshot(self) -> Mapping[str, Mapping[str, object]]:
        return {}

    def latest_events(self) -> Iterable[Mapping[str, object]]:
        return []

    def latest_employment_metrics(self) -> Mapping[str, object] | None:
        return {}

    def latest_rivalry_events(self) -> Iterable[Mapping[str, object]]:
        return []

    def latest_transport_status(self) -> Mapping[str, object]:
        return {}

    def import_state(self, payload: Mapping[str, object]) -> None:
        _ = payload

    def import_console_buffer(self, payload: Iterable[object]) -> None:
        self.console.extend(payload)

    def update_relationship_metrics(self, metrics: Mapping[str, object]) -> None:
        _ = metrics


    def close(self) -> None:
        return None


def _register_port_policy(name: str) -> None:
    factory_register("policy", name)(
        lambda **kwargs: ScriptedPolicyAdapter(
            _StubPolicy(
                kwargs.get("config") or getattr(kwargs.get("backend"), "config", None),
                backend=kwargs.get("backend"),
            )
        )
    )


def _register_port_telemetry(name: str) -> None:
    factory_register("telemetry", name)(
        lambda **kwargs: _StubTelemetry(
            kwargs.get("config") or getattr(kwargs.get("publisher"), "config", None),
            publisher=kwargs.get("publisher"),
        )
    )


@pytest.fixture(scope="module")
def sample_config() -> Any:
    project_root = Path(__file__).resolve().parents[1]
    return load_config(project_root / "configs" / "examples" / "poc_hybrid.yaml")


def test_registry_resolves_default_world(sample_config: Any) -> None:
    world = resolve_world(
        "default",
        config=sample_config,
    )
    assert isinstance(world, WorldRuntime)

    policy = resolve_policy("scripted", config=sample_config)
    assert isinstance(policy, PolicyBackendProtocol)

    telemetry = resolve_telemetry("stdout", config=sample_config)
    assert isinstance(telemetry, TelemetrySinkProtocol)
    if hasattr(telemetry, "close"):
        telemetry.close()


def test_registry_unknown_provider_raises(sample_config: Any) -> None:
    with pytest.raises(KeyError):
        resolve_policy("missing", config=sample_config)


def test_registry_type_enforcement(sample_config: Any) -> None:
    policy_registry().register("bad", lambda **_: object())
    with pytest.raises(TypeError):
        resolve_policy("bad", config=sample_config)


def test_simulation_loop_uses_registered_providers(sample_config: Any) -> None:
    policy_registry().register("stub", lambda **kwargs: _StubPolicy(kwargs.get("config")))
    _register_port_policy("stub")
    telemetry_registry().register("stub", lambda **kwargs: _StubTelemetry(kwargs.get("config")))
    _register_port_telemetry("stub")

    loop = SimulationLoop(
        sample_config,
        policy_provider="stub",
        telemetry_provider="stub",
    )
    try:
        assert isinstance(loop.policy, _StubPolicy)
        assert isinstance(loop._telemetry_port, _StubTelemetry)
        info = loop.provider_info
        assert info["policy"] == "stub"
        assert info["telemetry"] == "stub"
        assert policy_provider_name(loop) == "stub"
        assert telemetry_provider_name(loop) == "stub"
        assert is_stub_policy(loop.policy, info["policy"])
        assert is_stub_telemetry(loop._telemetry_port, info["telemetry"])
    finally:
        loop.close()


def test_simulation_loop_provider_metadata(sample_config: Any) -> None:
    policy_registry().register("stub_meta", lambda **kwargs: _StubPolicy(kwargs.get("config")))
    _register_port_policy("stub_meta")
    telemetry_registry().register("stub_meta", lambda **kwargs: _StubTelemetry(kwargs.get("config")))
    _register_port_telemetry("stub_meta")

    loop = SimulationLoop(
        sample_config,
        policy_provider="stub_meta",
        telemetry_provider="stub_meta",
    )
    try:
        info = loop.provider_info
        assert info["policy"] == "stub_meta"
        assert info["telemetry"] == "stub_meta"
        expected_world = sample_config.runtime.world.provider or "default"
        assert info["world"] == expected_world

        assert policy_provider_name(loop) == "stub_meta"
        assert telemetry_provider_name(loop) == "stub_meta"

        assert "stub_meta" in factory_available("policy")
        assert "stub_meta" in factory_available("telemetry")
    finally:
        loop.close()


def test_simulation_loop_reads_runtime_from_config(sample_config: Any) -> None:
    policy_registry().register("config_stub", lambda **kwargs: _StubPolicy(kwargs.get("config")))
    _register_port_policy("config_stub")
    telemetry_registry().register("config_stub", lambda **kwargs: _StubTelemetry(kwargs.get("config")))
    _register_port_telemetry("config_stub")

    runtime_overrides = RuntimeProviders(
        policy=RuntimeProviderConfig(provider="config_stub"),
        telemetry=RuntimeProviderConfig(provider="config_stub"),
    )
    config = sample_config.model_copy(update={"runtime": runtime_overrides})

    loop = SimulationLoop(config)
    try:
        assert isinstance(loop.policy, _StubPolicy)
        assert isinstance(loop._telemetry_port, _StubTelemetry)
    finally:
        loop.close()


def test_policy_module_helper_returns_backend(sample_config: Any) -> None:
    backend = resolve_policy_backend(DEFAULT_POLICY_PROVIDER, config=sample_config)
    assert isinstance(backend, PolicyBackendProtocol)

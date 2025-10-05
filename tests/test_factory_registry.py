from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

import pytest

from townlet.config import RuntimeProviderConfig, RuntimeProviders, load_config
from townlet.console.command import ConsoleCommandEnvelope, ConsoleCommandResult
from townlet.core import (
    SimulationLoop,
    policy_registry,
    resolve_policy,
    resolve_telemetry,
    resolve_world,
    telemetry_registry,
    world_registry,
)
from townlet.core.interfaces import (
    PolicyBackendProtocol,
    TelemetrySinkProtocol,
    WorldRuntimeProtocol,
)
from townlet.policy import DEFAULT_POLICY_PROVIDER, resolve_policy_backend
from townlet.lifecycle.manager import LifecycleManager
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
    def __init__(self, config: Any) -> None:
        self.config = config
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

    def decide(self, world: Any, tick: int) -> Mapping[str, object]:
        _ = world, tick
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


class _StubTelemetry(TelemetrySinkProtocol):  # type: ignore[misc]
    def __init__(self, config: Any) -> None:
        self.config = config
        self.console: list[object] = []

    def set_runtime_variant(self, variant: str | None) -> None:
        _ = variant

    def update_policy_identity(self, identity: Mapping[str, object] | None) -> None:
        _ = identity

    def drain_console_buffer(self) -> Iterable[object]:
        buffer = list(self.console)
        self.console.clear()
        return buffer

    def record_console_results(self, results: Iterable[ConsoleCommandResult]) -> None:
        _ = list(results)

    def publish_tick(
        self,
        *,
        tick: int,
        world: Any,
        observations: Mapping[str, object],
        rewards: Mapping[str, float],
        events: Iterable[Mapping[str, object]] | None = None,
        policy_snapshot: Mapping[str, Mapping[str, object]] | None = None,
        kpi_history: bool = False,
        reward_breakdown: Mapping[str, Mapping[str, float]] | None = None,
        stability_inputs: Mapping[str, object] | None = None,
        perturbations: Mapping[str, object] | None = None,
        policy_identity: Mapping[str, object] | None = None,
        possessed_agents: Iterable[str] | None = None,
        social_events: Iterable[Mapping[str, object]] | None = None,
        runtime_variant: str | None = None,
    ) -> None:
        _ = (
            tick,
            world,
            observations,
            rewards,
            events,
            policy_snapshot,
            kpi_history,
            reward_breakdown,
            stability_inputs,
            perturbations,
            policy_identity,
            possessed_agents,
            social_events,
            runtime_variant,
        )

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

    def record_stability_metrics(self, metrics: Mapping[str, object]) -> None:
        _ = metrics

    def latest_transport_status(self) -> Mapping[str, object]:
        return {}

    def record_health_metrics(self, metrics: Mapping[str, object]) -> None:
        _ = metrics

    def record_loop_failure(self, payload: Mapping[str, object]) -> None:
        _ = payload

    def import_state(self, payload: Mapping[str, object]) -> None:
        _ = payload

    def import_console_buffer(self, payload: Iterable[object]) -> None:
        self.console.extend(payload)

    def update_relationship_metrics(self, metrics: Mapping[str, object]) -> None:
        _ = metrics

    def record_snapshot_migrations(self, applied: Iterable[str]) -> None:
        _ = list(applied)

    def close(self) -> None:
        return None


@pytest.fixture(scope="module")
def sample_config() -> Any:
    project_root = Path(__file__).resolve().parents[1]
    return load_config(project_root / "configs" / "examples" / "poc_hybrid.yaml")


def test_registry_resolves_default_world(sample_config: Any) -> None:
    world = resolve_world(
        "default",
        world=_StubWorld(),
        lifecycle=_StubLifecycle(),
        perturbations=_StubPerturbations(),
        ticks_per_day=1,
    )
    assert isinstance(world, WorldRuntimeProtocol)

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
    telemetry_registry().register("stub", lambda **kwargs: _StubTelemetry(kwargs.get("config")))

    loop = SimulationLoop(
        sample_config,
        policy_provider="stub",
        telemetry_provider="stub",
    )
    try:
        assert isinstance(loop.policy, _StubPolicy)
        assert isinstance(loop.telemetry, _StubTelemetry)
    finally:
        if hasattr(loop.telemetry, "close"):
            loop.telemetry.close()


def test_simulation_loop_reads_runtime_from_config(sample_config: Any) -> None:
    policy_registry().register("config_stub", lambda **kwargs: _StubPolicy(kwargs.get("config")))
    telemetry_registry().register("config_stub", lambda **kwargs: _StubTelemetry(kwargs.get("config")))

    runtime_overrides = RuntimeProviders(
        policy=RuntimeProviderConfig(provider="config_stub"),
        telemetry=RuntimeProviderConfig(provider="config_stub"),
    )
    config = sample_config.model_copy(update={"runtime": runtime_overrides})

    loop = SimulationLoop(config)
    try:
        assert isinstance(loop.policy, _StubPolicy)
        assert isinstance(loop.telemetry, _StubTelemetry)
    finally:
        if hasattr(loop.telemetry, "close"):
            loop.telemetry.close()


def test_policy_module_helper_returns_backend(sample_config: Any) -> None:
    backend = resolve_policy_backend(DEFAULT_POLICY_PROVIDER, config=sample_config)
    assert isinstance(backend, PolicyBackendProtocol)

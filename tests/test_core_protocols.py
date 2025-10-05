from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

import pytest

from townlet.config import load_config
from townlet.console.command import ConsoleCommandEnvelope, ConsoleCommandResult
from townlet.core.interfaces import (
    PolicyBackendProtocol,
    TelemetrySinkProtocol,
    WorldRuntimeProtocol,
)
from townlet.policy.runner import PolicyRuntime
from townlet.telemetry.publisher import TelemetryPublisher
from townlet.world.runtime import WorldRuntime


class _StubWorld:
    def __init__(self) -> None:
        self.tick = 0
        self.console_calls: list[Iterable[ConsoleCommandEnvelope]] = []
        self._console_results: list[ConsoleCommandResult] = []
        self._events: list[dict[str, object]] = []

    def apply_console(self, operations: Iterable[ConsoleCommandEnvelope]) -> None:
        self.console_calls.append(list(operations))

    def consume_console_results(self) -> list[ConsoleCommandResult]:
        return list(self._console_results)

    def apply_actions(self, actions: Mapping[str, object]) -> None:
        _ = actions

    def resolve_affordances(self, *, current_tick: int) -> None:
        _ = current_tick

    def apply_nightly_reset(self) -> None:
        return None

    def drain_events(self) -> list[dict[str, object]]:
        return list(self._events)


class _StubLifecycle:
    def process_respawns(self, world: _StubWorld, *, tick: int) -> None:
        _ = world, tick

    def evaluate(self, world: _StubWorld, *, tick: int) -> dict[str, bool]:
        _ = world, tick
        return {}

    def termination_reasons(self) -> dict[str, str]:
        return {}


class _StubPerturbations:
    def tick(self, world: _StubWorld, *, current_tick: int) -> None:
        _ = world, current_tick


@pytest.fixture(scope="module")
def sample_config() -> Any:
    project_root = Path(__file__).resolve().parents[1]
    return load_config(project_root / "configs" / "examples" / "poc_hybrid.yaml")


def test_world_runtime_satisfies_protocol() -> None:
    runtime = WorldRuntime(
        world=_StubWorld(),
        lifecycle=_StubLifecycle(),
        perturbations=_StubPerturbations(),
        ticks_per_day=1,
    )
    assert isinstance(runtime, WorldRuntimeProtocol)


def test_policy_runtime_satisfies_protocol(sample_config: Any) -> None:
    policy = PolicyRuntime(sample_config)
    assert isinstance(policy, PolicyBackendProtocol)


def test_telemetry_publisher_satisfies_protocol(sample_config: Any) -> None:
    telemetry = TelemetryPublisher(sample_config)
    try:
        assert isinstance(telemetry, TelemetrySinkProtocol)
    finally:
        telemetry.close()

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import pytest

from townlet.console.command import ConsoleCommandEnvelope, ConsoleCommandResult
from townlet.lifecycle.manager import LifecycleManager
from townlet.scheduler.perturbations import PerturbationScheduler
from townlet.world.runtime import RuntimeStepResult, WorldRuntime


class _StubWorld:
    def __init__(self) -> None:
        self.tick = 0
        self.calls: list[tuple[str, Any]] = []
        self._events: list[dict[str, object]] = []

    def apply_console(self, operations: Iterable[ConsoleCommandEnvelope]) -> list[ConsoleCommandResult]:
        self.calls.append(("apply_console", list(operations)))
        return []

    def apply_actions(self, actions: Mapping[str, object]) -> None:
        self.calls.append(("apply_actions", dict(actions)))

    def resolve_affordances(self, *, current_tick: int) -> None:
        self.calls.append(("resolve_affordances", current_tick))

    def apply_nightly_reset(self) -> list[str]:
        self.calls.append(("apply_nightly_reset", None))
        return []

    def drain_events(self) -> list[dict[str, object]]:
        self.calls.append(("drain_events", None))
        return list(self._events)


class _StubLifecycle(LifecycleManager):
    def __init__(self) -> None:  # pragma: no cover - minimal params
        self.calls: list[tuple[str, Any]] = []

    def process_respawns(self, world: _StubWorld, *, tick: int) -> None:  # type: ignore[override]
        self.calls.append(("process_respawns", tick))

    def evaluate(self, world: _StubWorld, *, tick: int) -> dict[str, bool]:  # type: ignore[override]
        self.calls.append(("evaluate", tick))
        return {"alice": False}

    def termination_reasons(self) -> dict[str, str]:  # type: ignore[override]
        self.calls.append(("termination_reasons", None))
        return {"alice": "ok"}


class _StubPerturbations(PerturbationScheduler):
    def __init__(self) -> None:  # pragma: no cover - minimal params
        self.calls: list[tuple[str, Any]] = []

    def tick(self, world: _StubWorld, *, current_tick: int) -> None:  # type: ignore[override]
        self.calls.append(("tick", current_tick))


def _make_runtime(
    ticks_per_day: int,
) -> tuple[WorldRuntime, _StubWorld, _StubLifecycle, _StubPerturbations]:
    world = _StubWorld()
    lifecycle = _StubLifecycle()
    perturbations = _StubPerturbations()
    runtime = WorldRuntime(
        world=world,
        lifecycle=lifecycle,
        perturbations=perturbations,
        ticks_per_day=ticks_per_day,
    )
    return runtime, world, lifecycle, perturbations


def test_runtime_tick_invokes_dependencies_in_order() -> None:
    runtime, world, lifecycle, perturbations = _make_runtime(ticks_per_day=24)

    console_ops = [ConsoleCommandEnvelope(name="noop", metadata={})]

    def decide_actions(_: _StubWorld, __: int) -> Mapping[str, object]:
        return {"alice": {"action": "wait"}}

    result = runtime.tick(tick=1, console_operations=console_ops, action_provider=decide_actions)

    assert isinstance(result, RuntimeStepResult)
    assert result.console_results == []
    assert result.events == []
    assert result.actions == {"alice": {"action": "wait"}}
    assert result.terminated == {"alice": False}
    assert result.termination_reasons == {"alice": "ok"}

    call_sequence = [name for name, _ in world.calls]
    assert call_sequence == [
        "apply_console",
        "apply_actions",
        "resolve_affordances",
        "drain_events",
    ]
    lifecycle_sequence = [name for name, _ in lifecycle.calls]
    assert lifecycle_sequence == ["process_respawns", "evaluate", "termination_reasons"]
    perturbation_sequence = [name for name, _ in perturbations.calls]
    assert perturbation_sequence == ["tick"]


@pytest.mark.parametrize("tick", [1, 4])
def test_runtime_handles_buffered_inputs_and_nightly_reset(tick: int) -> None:
    runtime, world, _lifecycle, _perturbations = _make_runtime(ticks_per_day=4)

    buffered_ops = [ConsoleCommandEnvelope(name="noop", metadata={"source": "buffer"})]
    runtime.apply_actions({"bob": {"action": "move"}})

    runtime.tick(tick=tick, action_provider=None, console_operations=buffered_ops)

    console_call = next((args for name, args in world.calls if name == "apply_console"), None)
    assert console_call is not None
    assert console_call[0].metadata["source"] == "buffer"

    actions_call = next((args for name, args in world.calls if name == "apply_actions"), None)
    assert actions_call == {"bob": {"action": "move"}}

    nightly_calls = [name for name, _ in world.calls if name == "apply_nightly_reset"]
    if tick % 4 == 0:
        assert nightly_calls == ["apply_nightly_reset"]
    else:
        assert nightly_calls == []

    # Subsequent tick with empty console operations still succeeds.
    assert runtime.tick(tick=tick + 1, action_provider=lambda w, t: {}, console_operations=())

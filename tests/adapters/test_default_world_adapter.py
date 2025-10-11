from __future__ import annotations

from types import SimpleNamespace

import pytest

from townlet.adapters.world_default import DefaultWorldAdapter
from townlet.console.command import ConsoleCommandEnvelope
from townlet.world.runtime import RuntimeStepResult
from townlet.snapshots.state import SnapshotState


class _StubObservationBuilder:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def build_batch(self, adapter, terminated):  # type: ignore[override]
        self.calls.append({
            "adapter": adapter,
            "terminated": dict(terminated),
        })
        return {
            "alice": {"terminated": terminated.get("alice", False)},
            "bob": {"terminated": terminated.get("bob", False)},
        }


class _StubContext:
    def __init__(self) -> None:
        self.state = SimpleNamespace(tick=0, agents={"alice": {}, "bob": {}})
        self.config = object()
        self.observation_service = None
        self.reset_calls: list[int | None] = []
        self.tick_calls: list[dict[str, object]] = []
        self.snapshot_calls = 0

    def reset(self, *, seed: int | None = None) -> None:
        self.reset_calls.append(seed)
        self.state.tick = 0

    def tick(
        self,
        *,
        tick: int,
        console_operations,
        prepared_actions,
        lifecycle,
        perturbations,
        ticks_per_day: int,
    ) -> RuntimeStepResult:
        self.tick_calls.append(
            {
                "tick": tick,
                "console": list(console_operations),
                "actions": dict(prepared_actions),
                "lifecycle": lifecycle,
                "perturbations": perturbations,
                "ticks_per_day": ticks_per_day,
            }
        )
        self.state.tick = tick
        return RuntimeStepResult(
            console_results=[],
            events=[{"tick": tick}],
            actions=dict(prepared_actions),
            terminated={"alice": tick % 2 == 0},
            termination_reasons={"alice": "even" if tick % 2 == 0 else ""},
        )

    def snapshot(self) -> dict[str, object]:
        self.snapshot_calls += 1
        return {"state": "ok"}


@pytest.fixture()
def stub_builder() -> _StubObservationBuilder:
    return _StubObservationBuilder()


@pytest.fixture()
def stub_context() -> _StubContext:
    return _StubContext()


@pytest.fixture()
def stub_world_adapter(monkeypatch):
    sentinel = object()

    def _ensure(world):  # type: ignore[override]
        return sentinel

    monkeypatch.setattr("townlet.adapters.world_default.ensure_world_adapter", _ensure)
    monkeypatch.setattr("townlet.snapshots.state.ensure_world_adapter", _ensure)
    def _snapshot_from_world(config, world, **kwargs):  # type: ignore[override]
        tick = getattr(world, "tick", 0)
        return SnapshotState(config_id="test", tick=tick)

    monkeypatch.setattr("townlet.adapters.world_default.snapshot_from_world", _snapshot_from_world)
    return sentinel


def _make_adapter(stub_context: _StubContext, stub_builder: _StubObservationBuilder) -> DefaultWorldAdapter:
    return DefaultWorldAdapter(
        context=stub_context,
        lifecycle=object(),
        perturbations=object(),
        ticks_per_day=1440,
        observation_builder=stub_builder,
    )


def test_default_world_adapter_tick_and_reset_clears_buffers(
    stub_context: _StubContext,
    stub_builder: _StubObservationBuilder,
    stub_world_adapter,
) -> None:
    adapter = _make_adapter(stub_context, stub_builder)

    adapter.queue_console([ConsoleCommandEnvelope(name="snapshot")])
    adapter.apply_actions({"alice": {"intent": "rest"}})

    adapter.tick(tick=1, console_operations=None, action_provider=None, policy_actions=None)

    first_call = stub_context.tick_calls[-1]
    assert first_call["console"], "queued console operations should be forwarded"
    assert "alice" in first_call["actions"], "pending actions should be merged into tick"

    adapter.reset(seed=99)
    assert stub_context.reset_calls == [99]

    adapter.tick(tick=2, console_operations=None, action_provider=None, policy_actions=None)

    second_call = stub_context.tick_calls[-1]
    assert second_call["console"] == [], "reset should clear queued console commands"
    assert second_call["actions"] == {}, "reset should clear pending actions"


def test_default_world_adapter_observe_uses_builder_and_filters_agents(
    stub_context: _StubContext,
    stub_builder: _StubObservationBuilder,
    stub_world_adapter,
) -> None:
    adapter = _make_adapter(stub_context, stub_builder)

    adapter.tick(tick=2, console_operations=None, action_provider=None, policy_actions=None)

    batch = adapter.observe()
    assert set(batch.keys()) == {"alice", "bob"}
    assert stub_builder.calls[-1]["terminated"] == {"alice": True}

    filtered = adapter.observe(["bob"])
    assert set(filtered.keys()) == {"bob"}


def test_default_world_adapter_snapshot_includes_tick_and_events(
    stub_context: _StubContext,
    stub_builder: _StubObservationBuilder,
    stub_world_adapter,
) -> None:
    adapter = _make_adapter(stub_context, stub_builder)

    adapter.tick(tick=3, console_operations=None, action_provider=None, policy_actions=None)

    snapshot = adapter.snapshot()
    assert isinstance(snapshot, SnapshotState)
    assert snapshot.tick == 3
    assert snapshot.promotion == {}
    assert adapter._last_events == []  # type: ignore[attr-defined]

    # Subsequent snapshot should not alter cached events
    follow_up = adapter.snapshot()
    assert isinstance(follow_up, SnapshotState)
    assert adapter._last_events == []  # type: ignore[attr-defined]

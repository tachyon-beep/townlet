from __future__ import annotations

from collections.abc import Mapping
from types import SimpleNamespace

import pytest

from townlet.adapters.world_default import DefaultWorldAdapter
from townlet.console.command import ConsoleCommandEnvelope
from townlet.world.runtime import RuntimeStepResult
from townlet.snapshots.state import SnapshotState
from townlet.world.dto.observation import (
    AgentObservationDTO,
    GlobalObservationDTO,
    ObservationEnvelope,
)


class _StubContext:
    def __init__(self) -> None:
        self.state = SimpleNamespace(tick=0, agents={"alice": {}, "bob": {}})
        self.config = object()
        self.observation_service = object()
        self.reset_calls: list[int | None] = []
        self.tick_calls: list[dict[str, object]] = []
        self.snapshot_calls = 0
        self.observe_calls: list[dict[str, object]] = []
        self.apply_actions_calls: list[Mapping[str, object]] = []
        self.pending_actions: dict[str, object] = {}

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
        combined = dict(self.pending_actions)
        combined.update(prepared_actions or {})
        self.pending_actions.clear()
        self.tick_calls.append(
            {
                "tick": tick,
                "console": list(console_operations),
                "actions": dict(combined),
                "lifecycle": lifecycle,
                "perturbations": perturbations,
                "ticks_per_day": ticks_per_day,
            }
        )
        self.state.tick = tick
        return RuntimeStepResult(
            console_results=[],
            events=[{"tick": tick}],
            actions=combined,
            terminated={"alice": tick % 2 == 0},
            termination_reasons={"alice": "even" if tick % 2 == 0 else ""},
        )

    def observe(self, agent_ids=None, **kwargs):
        self.observe_calls.append({"agent_ids": tuple(agent_ids) if agent_ids is not None else None, "kwargs": kwargs})
        selected = ("alice", "bob") if agent_ids is None else tuple(agent_ids)
        agents = [
            AgentObservationDTO(
                agent_id=agent_id,
                map=None,
                features=None,
                metadata={"agent_id": agent_id},
                needs={"hunger": 0.5},
                wallet=1.0,
                inventory={},
                job={"role": "test"},
                personality=None,
                queue_state=None,
                pending_intent=None,
                position=None,
            )
            for agent_id in selected
        ]
        return ObservationEnvelope(
            tick=self.state.tick,
            agents=agents,
            global_context=GlobalObservationDTO(),
            actions=kwargs.get("actions", {}),
            terminated=kwargs.get("terminated", {}),
            termination_reasons=kwargs.get("termination_reasons", {}),
        )

    def apply_actions(self, actions: Mapping[str, object]) -> None:
        self.apply_actions_calls.append(dict(actions))
        self.pending_actions.update(actions)

    def snapshot(self) -> dict[str, object]:
        self.snapshot_calls += 1
        return {"state": "ok"}


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


def _make_adapter(stub_context: _StubContext) -> DefaultWorldAdapter:
    return DefaultWorldAdapter(
        context=stub_context,
        lifecycle=object(),
        perturbations=object(),
        ticks_per_day=1440,
    )


def test_default_world_adapter_tick_and_reset_clears_buffers(
    stub_context: _StubContext,
    stub_world_adapter,
) -> None:
    adapter = _make_adapter(stub_context)

    adapter.apply_actions({"alice": {"intent": "rest"}})

    ops = [ConsoleCommandEnvelope(name="snapshot")]
    adapter.tick(tick=1, console_operations=ops, action_provider=None, policy_actions=None)

    first_call = stub_context.tick_calls[-1]
    assert first_call["console"], "queued console operations should be forwarded"
    assert "alice" in first_call["actions"], "pending actions should be merged into tick"

    adapter.reset(seed=99)
    assert stub_context.reset_calls == [99]

    adapter.tick(tick=2, console_operations=(), action_provider=None, policy_actions=None)

    second_call = stub_context.tick_calls[-1]
    assert second_call["console"] == [], "reset should clear queued console commands"
    assert second_call["actions"] == {}, "reset should clear pending actions"


def test_default_world_adapter_observe_uses_context_and_filters_agents(
    stub_context: _StubContext,
    stub_world_adapter,
) -> None:
    adapter = _make_adapter(stub_context)

    adapter.tick(tick=2, console_operations=None, action_provider=None, policy_actions=None)

    envelope = adapter.observe()
    assert isinstance(envelope, ObservationEnvelope)
    assert {agent.agent_id for agent in envelope.agents} == {"alice", "bob"}
    assert stub_context.observe_calls[-1]["kwargs"]["terminated"] == {"alice": True}
    alice = next(agent for agent in envelope.agents if agent.agent_id == "alice")
    assert alice.metadata["agent_id"] == "alice"
    assert alice.needs["hunger"] == 0.5

    filtered = adapter.observe(["bob"])
    assert isinstance(filtered, ObservationEnvelope)
    assert [agent.agent_id for agent in filtered.agents] == ["bob"]
    assert stub_context.observe_calls[-1]["agent_ids"] == ("bob",)


def test_default_world_adapter_snapshot_includes_tick_and_events(
    stub_context: _StubContext,
    stub_world_adapter,
) -> None:
    adapter = _make_adapter(stub_context)

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

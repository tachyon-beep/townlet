from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from townlet.policy.behavior import AgentIntent, BehaviorController
from townlet.policy.dto_view import DTOWorldView
from townlet.policy.scenario_utils import ScenarioBehavior


@dataclass
class _StubBehavior(BehaviorController):  # type: ignore[misc]
    calls: list[tuple[object, str, DTOWorldView | None]]

    def decide(
        self,
        world: object,
        agent_id: str,
        *,
        dto_world: DTOWorldView | None = None,
    ) -> AgentIntent:
        self.calls.append((world, agent_id, dto_world))
        return AgentIntent(kind="base", target_agent=agent_id)


def test_scenario_behavior_returns_scripted_intent() -> None:
    base = _StubBehavior(calls=[])
    schedule = {"alice": [AgentIntent(kind="walk", position=(1, 2))]}
    wrapper = ScenarioBehavior(base, schedule)

    first = wrapper.decide(world=object(), agent_id="alice", dto_world=None)
    assert first.kind == "walk"
    assert first.position == (1, 2)
    assert base.calls == []

    second = wrapper.decide(world=object(), agent_id="alice", dto_world=None)
    assert second.kind == "walk"
    assert base.calls == []


def test_scenario_behavior_forwards_to_base_with_dto() -> None:
    base = _StubBehavior(calls=[])
    wrapper = ScenarioBehavior(base, schedules={})
    sentinel_world = object()
    dto_view = cast(DTOWorldView, object())

    intent = wrapper.decide(world=sentinel_world, agent_id="bob", dto_world=dto_view)

    assert intent.kind == "base"
    assert base.calls == [(sentinel_world, "bob", dto_view)]

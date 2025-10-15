"""Regression tests ensuring scripted behaviour prefers DTO data paths."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from townlet.config import SimulationConfig, load_config
from townlet.dto.observations import (
    AgentObservationDTO,
    GlobalObservationDTO,
    ObservationEnvelope,
)
from townlet.policy.behavior import AgentIntent, ScriptedBehavior
from townlet.policy.dto_view import DTOWorldView

CONFIG_PATH = Path("configs/examples/poc_hybrid.yaml")


class RaisingAgents(dict):
    """Container that raises if legacy agent access is attempted."""

    def get(self, key, default=None):  # pragma: no cover - helper guard
        raise AssertionError(f"legacy agent lookup for {key!r} not expected")

    def items(self):  # pragma: no cover - helper guard
        raise AssertionError("legacy agent iteration not expected")

    def values(self):  # pragma: no cover - helper guard
        raise AssertionError("legacy agent iteration not expected")


class QueueFallbackGuard:
    """Queue manager that fails if DTO data is not used."""

    def active_agent(self, object_id: str) -> str:  # pragma: no cover - guard hook
        raise AssertionError(f"legacy queue active_agent called for {object_id}")

    def queue_snapshot(self, object_id: str) -> tuple[str, ...]:  # pragma: no cover
        raise AssertionError(f"legacy queue snapshot requested for {object_id}")


class WorldStub:
    """Minimal world facade used to detect legacy fallbacks."""

    def __init__(
        self,
        *,
        tick: int = 0,
        queue_manager: object | None = None,
        agents: object | None = None,
        objects: dict[str, SimpleNamespace] | None = None,
        rivalry_should_avoid: bool = False,
        rivalry_value: float = 0.0,
    ) -> None:
        self.tick = tick
        self.queue_manager = queue_manager or QueueFallbackGuard()
        self.affordance_runtime = SimpleNamespace(running_affordances={})
        self.agents = agents or RaisingAgents()
        self.objects = objects or {}
        self._rivalry_should_avoid = bool(rivalry_should_avoid)
        self._rivalry_value = float(rivalry_value)

    def rivalry_should_avoid(self, *_args, **_kwargs) -> bool:
        return self._rivalry_should_avoid

    def rivalry_value(self, *_args, **_kwargs) -> float:
        return self._rivalry_value


@pytest.fixture(scope="module")
def simulation_config() -> SimulationConfig:
    return load_config(CONFIG_PATH)


def _agent(
    agent_id: str,
    *,
    needs: dict[str, float] | None = None,
    position: tuple[int, int] | None = None,
    personality: dict[str, float] | None = None,
    metadata: dict[str, object] | None = None,
    job: dict[str, object] | None = None,
) -> AgentObservationDTO:
    return AgentObservationDTO(
        agent_id=agent_id,
        needs=needs or {},
        position=position,
        wallet=10.0,
        inventory={},
        job=job or {},
        personality=personality or {},
        metadata=metadata or {},
        queue_state={},
    )


def _envelope(
    *,
    tick: int,
    agents: list[AgentObservationDTO],
    queues: dict[str, object] | None = None,
    running: dict[str, object] | None = None,
    relationship_snapshot: dict[str, object] | None = None,
    relationship_metrics: dict[str, object] | None = None,
) -> ObservationEnvelope:
    global_ctx = GlobalObservationDTO(
        queues=queues or {},
        running_affordances=running or {},
        relationship_snapshot=relationship_snapshot or {},
        relationship_metrics=relationship_metrics or {},
    )
    return ObservationEnvelope(
        tick=tick,
        agents=agents,
        global_context=global_ctx,
        actions={},
        terminated={},
        termination_reasons={},
    )


def test_pending_promotes_start_via_dto_queue(simulation_config: SimulationConfig) -> None:
    behavior = ScriptedBehavior(simulation_config)
    agent_id = "agent_1"
    behavior.pending[agent_id] = {
        "object_id": "coffee_machine",
        "affordance_id": "brew_coffee",
    }

    agent = _agent(agent_id, needs={"hunger": 0.5}, position=(4, 4))
    envelope = _envelope(
        tick=5,
        agents=[agent],
        queues={
            "active": {"coffee_machine": agent_id},
            "queues": {"coffee_machine": [{"agent_id": agent_id}]},
        },
    )
    world = WorldStub(tick=5)
    dto_world = DTOWorldView(envelope=envelope, world=world)

    intent = behavior.decide(world, agent_id, dto_world=dto_world)
    assert intent == AgentIntent(
        kind="start",
        object_id="coffee_machine",
        affordance_id="brew_coffee",
    )


def test_chat_selection_uses_dto_snapshots(simulation_config: SimulationConfig) -> None:
    behavior = ScriptedBehavior(simulation_config)
    agent_id = "agent_1"
    other_id = "agent_2"

    agent = _agent(
        agent_id,
        needs={"hunger": 0.9, "hygiene": 0.9, "energy": 0.9},
        position=(3, 3),
        personality={"extroversion": 0.9},
        metadata={"personality_profile": "socialite"},
    )
    other = _agent(
        other_id,
        needs={"hunger": 0.8, "hygiene": 0.8, "energy": 0.8},
        position=(3, 3),
        personality={"extroversion": 0.4},
        metadata={"personality_profile": "balanced"},
    )
    relationship_snapshot = {
        agent_id: {other_id: {"trust": 0.8, "familiarity": 0.7}},
        other_id: {agent_id: {"trust": 0.5, "familiarity": 0.4}},
    }
    relationship_metrics = {
        agent_id: {
            "rivalry": {other_id: 0.0},
            "should_avoid": {other_id: False},
        },
        other_id: {
            "rivalry": {agent_id: 0.0},
            "should_avoid": {agent_id: False},
        },
    }
    envelope = _envelope(
        tick=10,
        agents=[agent, other],
        relationship_snapshot=relationship_snapshot,
        relationship_metrics=relationship_metrics,
    )
    world = WorldStub(tick=10)
    dto_world = DTOWorldView(envelope=envelope, world=world)

    intent = behavior.decide(world, agent_id, dto_world=dto_world)
    assert intent.kind == "chat"
    assert intent.target_agent == other_id


def test_should_avoid_prefers_dto_relationships(simulation_config: SimulationConfig) -> None:
    behavior = ScriptedBehavior(simulation_config)
    agent_id = "agent_a"
    rival_id = "agent_b"

    agent = _agent(
        agent_id,
        needs={"hunger": 0.6, "hygiene": 0.6, "energy": 0.6},
        position=(1, 1),
        personality={"extroversion": 0.2},
        metadata={"personality_profile": "stoic"},
    )
    envelope = _envelope(
        tick=7,
        agents=[agent],
        relationship_metrics={
            agent_id: {
                "rivalry": {rival_id: 1.0},
                "should_avoid": {rival_id: True},
            }
        },
    )
    world = WorldStub(
        tick=7,
        rivalry_should_avoid=False,
        rivalry_value=0.0,
    )
    dto_world = DTOWorldView(envelope=envelope, world=world)

    assert behavior.should_avoid(
        world,
        agent_id,
        rival_id,
        dto_world=dto_world,
        relationship_view=dto_world,
    )

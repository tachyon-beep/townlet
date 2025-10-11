from __future__ import annotations

import itertools

import pytest

from pathlib import Path

from townlet.config import load_config
from townlet.world.grid import WorldState
from townlet.world.core import WorldContext
from townlet.world.dto.observation import ObservationEnvelope


@pytest.fixture()
def world_context() -> WorldContext:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    return world.context


def _spawn_agents(context: WorldContext, count: int = 2) -> None:
    world = context.state
    for idx in range(count):
        agent_id = f"agent_{idx}"
        world.lifecycle_service.spawn_agent(
            agent_id,
            (idx, idx),
            needs={"hunger": 0.5},
            wallet=0.0,
            home_position=(0, 0),
        )


def test_observe_returns_envelope(world_context: WorldContext) -> None:
    _spawn_agents(world_context, count=2)
    envelope = world_context.observe()
    assert isinstance(envelope, ObservationEnvelope)
    assert envelope.tick == world_context.state.tick
    assert isinstance(envelope.global_context.queue_metrics, dict)

    agent_ids = [agent.agent_id for agent in envelope.agents]
    assert agent_ids == sorted(agent_ids)
    for agent in envelope.agents:
        assert agent.needs is not None
        assert "hunger" in agent.needs
        assert agent.wallet is not None


def test_observe_agent_filter(world_context: WorldContext) -> None:
    _spawn_agents(world_context, count=2)

    agent_ids = ["agent_0"]
    envelope = world_context.observe(agent_ids=agent_ids)
    returned_ids = [agent.agent_id for agent in envelope.agents]
    assert returned_ids == agent_ids


def test_observe_includes_global_snapshots(world_context: WorldContext) -> None:
    _spawn_agents(world_context, count=1)
    envelope = world_context.observe()

    global_ctx = envelope.global_context
    assert isinstance(global_ctx.queue_metrics, dict)
    assert isinstance(global_ctx.relationship_snapshot, dict)
    assert isinstance(global_ctx.economy_snapshot, dict)
    assert isinstance(global_ctx.employment_snapshot, dict)

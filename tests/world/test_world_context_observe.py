from __future__ import annotations

import itertools

import pytest

from pathlib import Path

from townlet.config import load_config
from townlet.observations import ObservationBuilder
from townlet.world.grid import WorldState
from townlet.world.core import WorldContext
from townlet.world.dto.observation import ObservationEnvelope


@pytest.fixture()
def world_context() -> WorldContext:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.context.observation_service = ObservationBuilder(config=config)
    return world.context


def test_observe_returns_envelope(world_context: WorldContext) -> None:
    envelope = world_context.observe()
    assert isinstance(envelope, ObservationEnvelope)
    assert envelope.tick == world_context.state.tick
    assert isinstance(envelope.global_context.queue_metrics, dict)


def test_observe_agent_filter(world_context: WorldContext) -> None:
    world = world_context.state
    # Spawn two agents for observation
    for idx in range(2):
        agent_id = f"agent_{idx}"
        world.lifecycle_service.spawn_agent(
            agent_id,
            (idx, idx),
            needs={"hunger": 0.5},
            wallet=0.0,
            home_position=(0, 0),
        )

    agent_ids = ["agent_0"]
    envelope = world_context.observe(agent_ids=agent_ids)
    returned_ids = [agent.agent_id for agent in envelope.agents]
    assert returned_ids == agent_ids

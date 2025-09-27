from __future__ import annotations

from pathlib import Path

import pytest

from townlet.agents.models import Personality
from townlet.config import SimulationConfig, load_config
from townlet.world.grid import AgentSnapshot, WorldState


@pytest.fixture(scope="module")
def base_config() -> SimulationConfig:
    return load_config(Path("configs/examples/poc_hybrid.yaml"))


def _with_relationship_modifiers(
    config: SimulationConfig, enabled: bool
) -> SimulationConfig:
    data = config.model_dump()
    data["features"]["relationship_modifiers"] = enabled
    return SimulationConfig.model_validate(data)


def _build_world(config: SimulationConfig) -> WorldState:
    world = WorldState.from_config(config)
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.4, "hygiene": 0.5, "energy": 0.6},
        wallet=5.0,
        personality=Personality(extroversion=1.0, forgiveness=0.0, ambition=0.0),
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(1, 0),
        needs={"hunger": 0.3, "hygiene": 0.2, "energy": 0.7},
        wallet=3.0,
        personality=Personality(extroversion=0.0, forgiveness=0.0, ambition=0.0),
    )
    return world


def _familiarity(world: WorldState, owner: str, other: str) -> float:
    snapshot = world.relationships_snapshot()
    return snapshot.get(owner, {}).get(other, {}).get("familiarity", 0.0)


def test_chat_success_personality_bonus_applied(base_config: SimulationConfig) -> None:
    config = _with_relationship_modifiers(base_config, True)
    world = _build_world(config)

    world.record_chat_success("alice", "bob", quality=1.0)

    assert _familiarity(world, "alice", "bob") == pytest.approx(0.12)
    assert _familiarity(world, "bob", "alice") == pytest.approx(0.10)


def test_chat_success_parity_when_disabled(base_config: SimulationConfig) -> None:
    config = _with_relationship_modifiers(base_config, False)
    world = _build_world(config)

    world.record_chat_success("alice", "bob", quality=1.0)

    assert _familiarity(world, "alice", "bob") == pytest.approx(0.10)
    assert _familiarity(world, "bob", "alice") == pytest.approx(0.10)

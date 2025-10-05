from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from tests.helpers.social import seed_relationship_activity
from townlet.config import SimulationConfig, load_config
from townlet.observations.builder import ObservationBuilder
from townlet.world.grid import AgentSnapshot, WorldState


@pytest.fixture(scope="module")
def base_config() -> SimulationConfig:
    return load_config(Path("configs/examples/poc_hybrid.yaml"))


def _build_world(
    config: SimulationConfig,
    *,
    with_social: bool = True,
) -> WorldState:
    world = WorldState.from_config(config)
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.4, "hygiene": 0.5, "energy": 0.6},
        wallet=5.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(1, 0),
        needs={"hunger": 0.3, "hygiene": 0.2, "energy": 0.7},
        wallet=3.0,
    )
    if with_social:
        seed_relationship_activity(world, agent_a="alice", agent_b="bob")
    return world


def test_social_snippet_vector_length(base_config: SimulationConfig) -> None:
    builder = ObservationBuilder(base_config)
    world = _build_world(base_config)

    batch = builder.build_batch(world, terminated={})
    alice_obs = batch["alice"]
    features = alice_obs["features"]
    social_context = alice_obs["metadata"].get("social_context")
    assert social_context
    assert social_context["has_data"] is True
    assert social_context["relation_source"] in {"relationships", "rivalry_fallback"}

    assert features.shape[0] == len(builder._feature_names)

    aggregate_names = getattr(builder, "_social_aggregate_names", [])
    for name in aggregate_names:
        idx = builder._feature_index[name]
        # Rivalry aggregates should pick up the fallback rivalry signal.
        if "trust" in name:
            assert features[idx] > 0.0
        if "rivalry" in name:
            assert features[idx] >= 0.0


def test_relationship_stage_required(base_config: SimulationConfig) -> None:
    data = base_config.model_dump()
    data["features"]["stages"]["relationships"] = "OFF"
    config = SimulationConfig.model_validate(data)
    with pytest.raises(ValueError, match="relationships stage"):
        ObservationBuilder(config)


def test_disable_aggregates_via_config(base_config: SimulationConfig) -> None:
    data = base_config.model_dump()
    data["observations_config"]["social_snippet"]["include_aggregates"] = False
    config = SimulationConfig.model_validate(data)
    builder = ObservationBuilder(config)
    assert not builder._social_aggregate_names
    world = _build_world(config)
    batch = builder.build_batch(world, terminated={})
    features = batch["alice"]["features"]
    social_context = batch["alice"]["metadata"].get("social_context")
    assert social_context
    assert social_context["aggregates"] == []
    agg_indices = [
        idx
        for name, idx in builder._feature_index.items()
        if name.startswith("social_") and "mean" in name
    ]
    for idx in agg_indices:
        assert idx >= features.shape[0]  # aggregates removed


def test_observation_matches_golden_fixture(base_config: SimulationConfig) -> None:
    builder = ObservationBuilder(base_config)
    world = _build_world(base_config)
    obs = builder.build_batch(world, terminated={})
    features = obs["alice"]["features"]
    path = Path("tests/data/observations/social_snippet_gold.npz")
    assert path.exists(), "Golden observation fixture missing"
    data = np.load(path, allow_pickle=True)
    expected = data["features"]
    names = data["names"].tolist()
    assert builder._feature_names == names
    social_context = obs["alice"]["metadata"].get("social_context")
    assert social_context
    assert social_context["relation_source"] == "relationships"
    np.testing.assert_allclose(features, expected, atol=1e-6)

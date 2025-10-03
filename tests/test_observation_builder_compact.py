from __future__ import annotations

from pathlib import Path

import numpy as np

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.observations.builder import ObservationBuilder
from townlet.world.grid import AgentSnapshot


def make_compact_world() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.features.systems.observations = "compact"
    config.observations_config.hybrid.include_targets = True
    loop = SimulationLoop(config)
    world = loop.world
    world.agents.clear()
    world.register_object(object_id="stove_1", object_type="stove", position=(2, 0))
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.2, "hygiene": 0.7, "energy": 0.9},
        wallet=4.0,
    )
    return loop


def test_compact_observation_features_only() -> None:
    loop = make_compact_world()
    builder: ObservationBuilder = loop.observations
    world = loop.world
    obs = builder.build_batch(world, terminated={})["alice"]

    map_tensor = obs["map"]
    features = obs["features"]
    metadata = obs["metadata"]

    assert map_tensor.shape == (0, 0, 0)
    assert metadata["map_shape"] == (0, 0, 0)
    assert metadata["variant"] == "compact"
    assert metadata["map_channels"] == []

    feature_names = metadata["feature_names"]
    assert len(feature_names) == features.shape[0]
    hunger_idx = feature_names.index("need_hunger")
    assert np.isclose(features[hunger_idx], 0.2)

    social_context = metadata.get("social_context")
    assert social_context
    assert social_context["configured_slots"] >= 0
    assert social_context["filled_slots"] == 0
    assert social_context["relation_source"] in {"empty", "rivalry_fallback"}

    reservation_idx = feature_names.index("reservation_active")
    queue_idx = feature_names.index("in_queue")
    assert features[reservation_idx] == 0.0
    assert features[queue_idx] == 0.0

    north_idx = feature_names.index("path_hint_north")
    east_idx = feature_names.index("path_hint_east")
    assert np.isclose(features[north_idx], 0.0)
    assert np.isclose(features[east_idx], 1.0)

    landmark_slices = metadata.get("landmark_slices")
    assert landmark_slices
    stove_slice = landmark_slices["stove"]
    dx, dy, dist = features[stove_slice[0] : stove_slice[1]]
    assert np.isclose(dx, 1.0)
    assert np.isclose(dy, 0.0)
    assert np.isclose(dist, 2.0)

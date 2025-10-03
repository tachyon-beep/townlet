from __future__ import annotations

from pathlib import Path

import numpy as np

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.observations.builder import ObservationBuilder
from townlet.world.grid import AgentSnapshot


def make_full_world() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.features.systems.observations = "full"
    config.observations_config.hybrid.include_targets = True
    config.observations_config.social_snippet.top_friends = 0
    config.observations_config.social_snippet.top_rivals = 0
    config.observations_config.social_snippet.include_aggregates = False
    loop = SimulationLoop(config)
    world = loop.world
    world.agents.clear()
    world.register_object(object_id="fridge_1", object_type="fridge", position=(1, 0))
    world.register_object(object_id="stove_1", object_type="stove", position=(0, 2))
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.3, "hygiene": 0.6, "energy": 0.8},
        wallet=5.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(1, 0),
        needs={"hunger": 0.5, "hygiene": 0.4, "energy": 0.9},
        wallet=3.0,
    )
    return loop


def test_full_observation_map_and_features() -> None:
    loop = make_full_world()
    builder: ObservationBuilder = loop.observations
    world = loop.world
    observations = builder.build_batch(world, terminated={})

    obs = observations["alice"]
    map_tensor = obs["map"]
    features = obs["features"]
    metadata = obs["metadata"]

    window = builder.hybrid_cfg.local_window
    assert map_tensor.shape == (6, window, window)
    assert metadata["map_shape"] == (6, window, window)
    assert metadata["variant"] == "full"
    center = window // 2
    # Self channel
    assert map_tensor[0, center, center] == 1.0
    # Agent channel (bob at (1,0))
    assert map_tensor[1, center, center + 1] == 1.0
    # Object channel (fridge at (1,0))
    assert map_tensor[2, center, center + 1] == 1.0
    # Path hint channels should encode normalized vector to tile (1,0)
    assert np.isclose(map_tensor[4, center, center + 1], 1.0)
    assert np.isclose(map_tensor[5, center, center + 1], 0.0)

    feature_names = metadata["feature_names"]
    hunger_idx = feature_names.index("need_hunger")
    assert np.isclose(features[hunger_idx], 0.3)

    landmark_slices = metadata.get("landmark_slices")
    assert landmark_slices
    stove_slice = landmark_slices["stove"]
    dx, dy, dist = features[stove_slice[0] : stove_slice[1]]
    assert np.isclose(dx, 0.0)
    assert np.isclose(dy, 1.0)
    assert np.isclose(dist, 2.0)

    assert metadata["map_channels"] == [
        "self",
        "agents",
        "objects",
        "reservations",
        "path_dx",
        "path_dy",
    ]

    feature_names = metadata["feature_names"]
    assert len(feature_names) == features.shape[0]
    assert "social_context" not in metadata

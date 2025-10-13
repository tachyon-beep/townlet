from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world.observations.service import WorldObservationService
from townlet.world.grid import AgentSnapshot


def make_compact_world(*, object_channels: list[str] | None = None) -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.features.systems.observations = "compact"
    config.observations_config.compact.include_targets = True
    if object_channels is not None:
        config.observations_config.compact.object_channels = list(object_channels)
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
    world.rebuild_spatial_index()
    return loop


def test_compact_observation_features_only() -> None:
    loop = make_compact_world()
    service = WorldObservationService(config=loop.config)
    world = loop.world
    obs = service.build_batch(world, terminated={})["alice"]

    map_tensor = obs["map"]
    features = obs["features"]
    metadata = obs["metadata"]

    window = service.compact_cfg.map_window
    channels = service.compact_map_channels
    radius = window // 2
    assert map_tensor.shape == (len(channels), window, window)
    assert metadata["map_shape"] == (len(channels), window, window)
    assert metadata["variant"] == "compact"
    assert metadata["map_channels"] == list(channels)

    channel_index = {name: idx for idx, name in enumerate(channels)}
    assert map_tensor[channel_index["self"], radius, radius] == pytest.approx(1.0)
    assert map_tensor[channel_index["agents"], radius, radius] == pytest.approx(0.0)
    stove_x = radius + 2
    stove_y = radius + 0
    assert map_tensor[channel_index["objects"], stove_y, stove_x] == pytest.approx(1.0)
    assert map_tensor[channel_index["walkable"], stove_y, stove_x] == pytest.approx(0.0)
    assert metadata.get("compact") == {
        "map_window": window,
        "object_channels": [],
        "normalize_counts": True,
        "include_targets": True,
    }

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

    summary = metadata.get("local_summary")
    assert summary is not None
    assert summary["object_count"] >= 1.0
    assert summary["agent_count"] == pytest.approx(0.0)
    agent_ratio_idx = feature_names.index("neighbor_agent_ratio")
    object_ratio_idx = feature_names.index("neighbor_object_ratio")
    reserved_ratio_idx = feature_names.index("reserved_tile_ratio")
    nearest_agent_idx = feature_names.index("nearest_agent_distance")
    assert np.isclose(features[agent_ratio_idx], summary["agent_ratio"])
    assert np.isclose(features[object_ratio_idx], summary["object_ratio"])
    assert np.isclose(features[reserved_ratio_idx], summary["reserved_ratio"])
    assert np.isclose(
        features[nearest_agent_idx], summary["nearest_agent_distance_norm"]
    )


def test_compact_object_channels() -> None:
    loop = make_compact_world(object_channels=["stove"])
    service = WorldObservationService(config=loop.config)
    world = loop.world
    obs = service.build_batch(world, terminated={})["alice"]

    map_tensor = obs["map"]
    metadata = obs["metadata"]
    channels = metadata["map_channels"]
    assert "object:stove" in channels
    assert metadata.get("compact", {}).get("object_channels") == ["stove"]

    channel_index = {name: idx for idx, name in enumerate(channels)}
    stove_idx = channel_index["object:stove"]
    radius = service.compact_cfg.map_window // 2
    stove_x = radius + 2
    stove_y = radius
    assert map_tensor[stove_idx, stove_y, stove_x] == pytest.approx(1.0)

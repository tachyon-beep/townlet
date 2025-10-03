from pathlib import Path

import numpy as np

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.observations.builder import ObservationBuilder
from townlet.console.command import ConsoleCommandEnvelope
from townlet.world.grid import AgentSnapshot


def make_world(enforce_job_loop: bool = False) -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.conflict.rivalry.avoid_threshold = 0.1
    config.employment.enforce_job_loop = enforce_job_loop
    config.observations_config.hybrid.include_targets = True
    loop = SimulationLoop(config)
    world = loop.world
    world.agents.clear()
    world.register_object(object_id="stove_test", object_type="stove", position=(2, 0))
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.4, "hygiene": 0.5, "energy": 0.6},
        wallet=2.0,
        last_action_id="wait",
        last_action_success=True,
        last_action_duration=4,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(1, 0),
        needs={"hunger": 0.7, "hygiene": 0.8, "energy": 0.9},
        wallet=3.0,
    )
    world._assign_jobs_to_agents()  # type: ignore[attr-defined]
    return loop


def test_observation_builder_hybrid_map_and_features() -> None:
    loop = make_world(enforce_job_loop=True)
    builder: ObservationBuilder = loop.observations
    world = loop.world
    observations = builder.build_batch(world, terminated={})

    obs = observations["alice"]
    map_tensor = obs["map"]
    features = obs["features"]
    metadata = obs["metadata"]

    assert map_tensor.shape == (
        4,
        builder.hybrid_cfg.local_window,
        builder.hybrid_cfg.local_window,
    )
    assert metadata["map_shape"] == (
        4,
        builder.hybrid_cfg.local_window,
        builder.hybrid_cfg.local_window,
    )
    assert metadata["variant"] == "hybrid"
    center = builder.hybrid_cfg.local_window // 2
    assert map_tensor[0, center, center] == 1.0
    # Bob is at (1,0) relative to Alice
    assert map_tensor[1, center, center + 1] == 1.0
    # Stove object occupies (2,0)
    assert map_tensor[2, center, center + 2] == 1.0

    feature_names = metadata["feature_names"]
    assert len(feature_names) == features.shape[0]
    hunger_idx = feature_names.index("need_hunger")
    wallet_idx = feature_names.index("wallet")
    shift_pre_idx = feature_names.index("shift_pre")

    assert np.isclose(features[hunger_idx], 0.4)
    assert np.isclose(features[wallet_idx], 2.0)
    # Default shift state pre-shift should be one-hot
    assert features[shift_pre_idx] == 1.0
    assert features[feature_names.index("ctx_reset_flag")] == 0.0
    assert features[feature_names.index("rivalry_max")] == 0.0
    assert features[feature_names.index("rivalry_avoid_count")] == 0.0
    assert features[feature_names.index("last_action_success")] == 1.0
    assert features[feature_names.index("last_action_duration")] == 4.0
    assert features[feature_names.index("last_action_id_hash")] > 0.0
    stove_dx_idx = feature_names.index("stove_dx")
    stove_dy_idx = feature_names.index("stove_dy")
    stove_dist_idx = feature_names.index("stove_dist")
    assert np.isclose(features[stove_dx_idx], 1.0)
    assert np.isclose(features[stove_dy_idx], 0.0)
    assert np.isclose(features[stove_dist_idx], 2.0)
    landmark_slices = metadata.get("landmark_slices", {})
    assert landmark_slices.get("stove") == (stove_dx_idx, stove_dist_idx + 1)

    social_context = metadata.get("social_context")
    assert social_context
    assert social_context["configured_slots"] >= 0
    assert social_context["relation_source"] in {"empty", "rivalry_fallback", "relationships"}


def test_observation_ctx_reset_releases_slot() -> None:
    loop = make_world()
    builder: ObservationBuilder = loop.observations
    world = loop.world

    terminated = {"alice": True}
    observations = builder.build_batch(world, terminated=terminated)
    obs = observations["alice"]
    feature_names = obs["metadata"]["feature_names"]
    idx = feature_names.index("ctx_reset_flag")
    assert obs["features"][idx] == 1.0
    assert not world.embedding_allocator.has_assignment("alice")


def test_observation_rivalry_features_reflect_conflict() -> None:
    loop = make_world()
    world = loop.world
    world.register_rivalry_conflict("alice", "bob")
    builder: ObservationBuilder = loop.observations
    observations = builder.build_batch(world, terminated={})
    obs = observations["alice"]
    feature_names = obs["metadata"]["feature_names"]
    assert obs["features"][feature_names.index("rivalry_max")] > 0.0
    assert obs["features"][feature_names.index("rivalry_avoid_count")] >= 1.0


def test_observation_queue_and_reservation_flags() -> None:
    loop = make_world()
    builder: ObservationBuilder = loop.observations
    world = loop.world

    world._active_reservations["stove_test"] = "alice"
    if "stove_test" in world.objects:
        world.objects["stove_test"].occupied_by = "alice"
    world.queue_manager.requeue_to_tail("stove_test", "bob", tick=world.tick)

    observations = builder.build_batch(world, terminated={})

    alice_obs = observations["alice"]
    feature_names = alice_obs["metadata"]["feature_names"]
    reservation_idx = feature_names.index("reservation_active")
    assert alice_obs["features"][reservation_idx] == 1.0

    bob_obs = observations["bob"]
    bob_feature_names = bob_obs["metadata"]["feature_names"]
    queue_idx = bob_feature_names.index("in_queue")
    assert bob_obs["features"][queue_idx] == 1.0


def test_observation_respawn_resets_features() -> None:
    loop = make_world()
    builder: ObservationBuilder = loop.observations
    world = loop.world

    world.tick = 10
    world.agents["alice"].needs["hunger"] = 0.01
    terminated = loop.lifecycle.evaluate(world, tick=world.tick)
    assert terminated["alice"] is True

    loop.lifecycle.finalize(world, tick=world.tick, terminated=terminated)
    loop.lifecycle.process_respawns(world, tick=world.tick)

    respawn_id = next(agent_id for agent_id in world.agents if agent_id.startswith("alice"))
    assert respawn_id != "alice"

    observations = builder.build_batch(world, terminated={})
    obs = observations[respawn_id]
    feature_names = obs["metadata"]["feature_names"]
    hunger_idx = feature_names.index("need_hunger")
    ctx_idx = feature_names.index("ctx_reset_flag")
    assert obs["features"][hunger_idx] == 0.5
    assert obs["features"][ctx_idx] == 0.0


def test_ctx_reset_flag_on_teleport_and_possession() -> None:
    loop = make_world()
    builder: ObservationBuilder = loop.observations
    world = loop.world

    envelope = ConsoleCommandEnvelope(
        name="teleport",
        args=[],
        kwargs={"payload": {"agent_id": "alice", "position": [5, 5]}},
        cmd_id="test-teleport-ctx",
        mode="admin",
    )
    world._console_teleport_agent(envelope)

    observations = builder.build_batch(world, terminated={})
    alice_obs = observations["alice"]
    feature_names = alice_obs["metadata"]["feature_names"]
    idx = feature_names.index("ctx_reset_flag")
    assert alice_obs["features"][idx] == 1.0

    loop.policy.acquire_possession("bob")
    observations = builder.build_batch(world, terminated={})
    bob_obs = observations["bob"]
    feature_names = bob_obs["metadata"]["feature_names"]
    idx = feature_names.index("ctx_reset_flag")
    assert bob_obs["features"][idx] == 1.0

    loop.policy.release_possession("bob")
    observations = builder.build_batch(world, terminated={})
    bob_obs = observations["bob"]
    feature_names = bob_obs["metadata"]["feature_names"]
    idx = feature_names.index("ctx_reset_flag")
    assert bob_obs["features"][idx] == 0.0

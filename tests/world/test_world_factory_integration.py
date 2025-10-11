from __future__ import annotations

import random
from pathlib import Path

from townlet.config import load_config
from townlet.factories import create_world
from townlet.snapshots.state import SnapshotState
from townlet.world.dto.observation import ObservationEnvelope


def test_create_world_instantiates_context_from_config() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world_runtime = create_world(
        provider="default",
        config=config,
        ticks_per_day=config.observations_config.hybrid.time_ticks_per_day,
        world_kwargs={"rng": random.Random(1)},
    )

    assert list(world_runtime.agents()) == []
    result = world_runtime.tick(tick=1, policy_actions={})
    snapshot = world_runtime.snapshot()
    assert isinstance(snapshot, SnapshotState)
    assert snapshot.tick == 1
    assert isinstance(result.console_results, list)
    assert world_runtime.lifecycle_manager.config is config


def test_world_context_observe_produces_dto_envelope() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world_runtime = create_world(
        provider="default",
        config=config,
        world_kwargs={"rng": random.Random(5)},
    )

    world_runtime.tick(tick=1, policy_actions={})
    context = world_runtime.context
    envelope = context.observe()
    assert isinstance(envelope, ObservationEnvelope)
    assert envelope.schema_version.startswith("0.")

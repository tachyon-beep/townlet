from __future__ import annotations

import random
from pathlib import Path

from townlet.config import load_config
from townlet.factories import create_world
from townlet.lifecycle.manager import LifecycleManager
from townlet.observations.builder import ObservationBuilder
from townlet.scheduler.perturbations import PerturbationScheduler


def test_create_world_instantiates_context_from_config() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    lifecycle = LifecycleManager(config=config)
    perturbations = PerturbationScheduler(config=config, rng=random.Random(2))
    observation_builder = ObservationBuilder(config=config)

    world_runtime = create_world(
        provider="default",
        config=config,
        lifecycle=lifecycle,
        perturbations=perturbations,
        ticks_per_day=observation_builder.hybrid_cfg.time_ticks_per_day,
        world_kwargs={"rng": random.Random(1)},
        observation_builder=observation_builder,
    )

    # Initial world should have no agents and tick safely.
    assert list(world_runtime.agents()) == []
    result = world_runtime.tick(tick=1, policy_actions={})
    snapshot = world_runtime.snapshot()
    assert snapshot["tick"] == 1
    assert isinstance(result.console_results, list)

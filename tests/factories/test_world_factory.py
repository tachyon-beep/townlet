from __future__ import annotations

import random
from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.lifecycle.manager import LifecycleManager
from townlet.observations import ObservationBuilder
from townlet.scheduler.perturbations import PerturbationScheduler
from townlet.world.grid import WorldState
from townlet.world.runtime import RuntimeStepResult

from townlet.factories import create_world


@pytest.fixture()
def base_config():
    return load_config(Path("configs/examples/poc_hybrid.yaml"))


def _build_dependencies(config):
    world = WorldState.from_config(config)
    lifecycle = LifecycleManager(config=config)
    perturbations = PerturbationScheduler(config=config, rng=random.Random(42))
    ticks_per_day = 1440
    builder = ObservationBuilder(config=config)
    return world, lifecycle, perturbations, ticks_per_day, builder


def test_create_world_returns_context_adapter(base_config):
    world, lifecycle, perturbations, ticks_per_day, builder = _build_dependencies(base_config)
    adapter = create_world(
        provider="default",
        world=world,
        lifecycle=lifecycle,
        perturbations=perturbations,
        ticks_per_day=ticks_per_day,
        observation_builder=builder,
    )
    result = adapter.tick(
        tick=1,
        console_operations=[],
        action_provider=None,
        policy_actions={},
    )
    assert isinstance(result, RuntimeStepResult)
    observations = adapter.observe()
    assert isinstance(observations, dict)


def test_create_world_requires_config_or_world(base_config):
    lifecycle = LifecycleManager(config=base_config)
    perturbations = PerturbationScheduler(config=base_config, rng=random.Random(1))
    with pytest.raises(TypeError):
        create_world(
            provider="default",
            lifecycle=lifecycle,
            perturbations=perturbations,
            ticks_per_day=1440,
        )


def test_create_world_requires_lifecycle_when_modular(base_config):
    world = WorldState.from_config(base_config)
    builder = ObservationBuilder(config=base_config)
    perturbations = PerturbationScheduler(config=base_config, rng=random.Random(1))
    with pytest.raises(TypeError):
        create_world(
            provider="default",
            world=world,
            perturbations=perturbations,
            ticks_per_day=1440,
            observation_builder=builder,
        )

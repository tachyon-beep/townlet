from __future__ import annotations

import random
from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.factories import create_world
from townlet.world.dto.observation import GlobalObservationDTO, ObservationEnvelope
from townlet.world.grid import WorldState
from townlet.world.runtime import RuntimeStepResult


@pytest.fixture()
def base_config():
    return load_config(Path("configs/examples/poc_hybrid.yaml"))


def test_create_world_returns_context_adapter(base_config):
    adapter = create_world(
        provider="default",
        config=base_config,
        world_kwargs={"rng": random.Random(42)},
    )
    result = adapter.tick(
        tick=1,
        console_operations=[],
        action_provider=None,
        policy_actions={},
    )
    assert isinstance(result, RuntimeStepResult)
    assert isinstance(result.events, list)
    assert all(isinstance(event, dict) for event in result.events)
    envelope = adapter.observe()
    assert isinstance(envelope, ObservationEnvelope)
    assert envelope.tick == 1
    assert isinstance(envelope.global_context, GlobalObservationDTO)
    # Use new component accessor pattern
    comp = adapter.components()
    assert comp["lifecycle"].config is base_config
    assert comp["perturbations"].config is base_config


def test_create_world_requires_config_or_world(base_config):
    with pytest.raises(TypeError):
        create_world(
            provider="default",
            ticks_per_day=1440,
        )


def test_create_world_rejects_legacy_service_overrides(base_config):
    world = WorldState.from_config(base_config)
    with pytest.raises(TypeError, match="Unsupported arguments"):
        create_world(
            provider="default",
            world=world,
            lifecycle="invalid",
        )


def test_create_world_rejects_observation_builder_override(base_config):
    with pytest.raises(TypeError, match="Unsupported arguments"):
        create_world(
            provider="default",
            config=base_config,
            observation_builder=object(),
        )


def test_create_world_rejects_legacy_runtime_argument():
    with pytest.raises(TypeError):
        create_world(provider="default", runtime=object())


def test_create_world_requires_valid_provider(base_config):
    from townlet.factories.registry import ConfigurationError

    with pytest.raises(ConfigurationError):
        create_world(provider="does_not_exist", config=base_config)

from __future__ import annotations

import pytest

from townlet.factories.policy_factory import create_policy
from townlet.factories.registry import REGISTRY, ConfigurationError, register
from townlet.factories.telemetry_factory import create_telemetry
from townlet.factories.world_factory import create_world
from townlet.testing.dummies import DummyPolicy, DummyTelemetry, DummyWorld


class _Provider:
    def __init__(self, provider: str, options: dict[str, object] | None = None) -> None:
        self.provider = provider
        self.options = options or {}


class _Runtime:
    def __init__(self, world: str, policy: str, telemetry: str) -> None:
        self.world = _Provider(world)
        self.policy = _Provider(policy)
        self.telemetry = _Provider(telemetry)


class _Config:
    def __init__(self, world: str = "dummy", policy: str = "dummy", telemetry: str = "dummy") -> None:
        self.runtime = _Runtime(world, policy, telemetry)
        self.seed = 0


def test_factories_return_registered_dummies() -> None:
    cfg = _Config()
    world = create_world(cfg)
    policy = create_policy(cfg)
    telemetry = create_telemetry(cfg)
    assert isinstance(world, DummyWorld)
    assert isinstance(policy, DummyPolicy)
    assert isinstance(telemetry, DummyTelemetry)


def test_factories_accept_mapping_config() -> None:
    cfg = {
        "runtime": {
            "world": {"provider": "dummy"},
            "policy": {"provider": "dummy"},
            "telemetry": {"provider": "dummy"},
        }
    }
    world = create_world(cfg)
    policy = create_policy(cfg)
    telemetry = create_telemetry(cfg)
    assert isinstance(world, DummyWorld)
    assert isinstance(policy, DummyPolicy)
    assert isinstance(telemetry, DummyTelemetry)


def test_unknown_provider_raises() -> None:
    cfg = _Config(world="missing")
    with pytest.raises(ConfigurationError):
        create_world(cfg)
    cfg.runtime.world.provider = "dummy"
    cfg.runtime.policy.provider = "missing"
    with pytest.raises(ConfigurationError):
        create_policy(cfg)
    cfg.runtime.policy.provider = "dummy"
    cfg.runtime.telemetry.provider = "missing"
    with pytest.raises(ConfigurationError):
        create_telemetry(cfg)


def test_created_objects_follow_ports() -> None:
    cfg = _Config()
    world = create_world(cfg)
    policy = create_policy(cfg)
    telemetry = create_telemetry(cfg)
    world.reset()
    agents = list(world.agents())
    policy.on_episode_start(agents)
    observations = world.observe()
    actions = policy.decide(observations)
    world.apply_actions(actions)
    world.tick()
    telemetry.start()
    telemetry.emit_event("tick", world.snapshot())
    telemetry.emit_metric("tick_duration", 1.0)
    telemetry.stop()


def test_policy_factory_passes_options() -> None:
    captured: dict[str, object] = {}

    @register("policy", "options-probe")
    def _build_policy(*, cfg: object, **options: object) -> DummyPolicy:
        captured.update(options)
        return DummyPolicy()

    try:
        cfg = {
            "runtime": {
                "policy": {
                    "provider": "options-probe",
                    "options": {"foo": "bar", "count": 3},
                }
            }
        }
        policy = create_policy(cfg)
        assert isinstance(policy, DummyPolicy)
        assert captured == {"foo": "bar", "count": 3}
    finally:
        REGISTRY["policy"].pop("options-probe", None)

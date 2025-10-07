from __future__ import annotations

import pytest

from townlet.factories.policy_factory import create_policy
from townlet.factories.registry import ConfigurationError
from townlet.factories.telemetry_factory import create_telemetry
from townlet.factories.world_factory import create_world


@pytest.mark.parametrize(
    "factory, cfg",
    [
        (create_world, {"provider": "default"}),
        (create_world, {"provider": "dummy", "agent_count": 2}),
        (create_policy, {"provider": "scripted"}),
        (create_policy, {"provider": "dummy"}),
        (create_telemetry, {"provider": "stdout"}),
        (create_telemetry, {"provider": "dummy"}),
    ],
)
def test_factories_return_port_implementations(factory, cfg) -> None:
    instance = factory(cfg)
    assert instance is not None


@pytest.mark.parametrize(
    "factory",
    [create_world, create_policy, create_telemetry],
)
def test_unknown_provider_raises(factory) -> None:
    with pytest.raises(ConfigurationError) as exc:
        factory({"provider": "unknown"})
    assert "Unknown" in str(exc.value)

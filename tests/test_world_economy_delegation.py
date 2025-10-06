from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop


def _make_world():
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.world.agents.clear()
    return loop.world


def test_set_price_target_delegates_to_service(monkeypatch: pytest.MonkeyPatch) -> None:
    world = _make_world()
    service = Mock(wraps=world.economy_service)
    monkeypatch.setattr(world, "_economy_service", service, raising=False)

    world.set_price_target("meal_cost", 1.23)
    service.set_price_target.assert_called_once_with("meal_cost", 1.23)


def test_apply_price_spike_updates_economy() -> None:
    world = _make_world()
    baseline = dict(world.config.economy)

    world.apply_price_spike("event-1", magnitude=1.5, targets=["meal_cost"])

    assert world.config.economy["meal_cost"] == pytest.approx(baseline["meal_cost"] * 1.5)
    assert "event-1" in world.active_price_spikes()

    world.clear_price_spike("event-1")
    assert world.config.economy["meal_cost"] == pytest.approx(baseline["meal_cost"])


def test_utility_outage_toggles_stock() -> None:
    world = _make_world()
    object_id = "stove_1"
    world.register_object(object_id=object_id, object_type="stove", position=(0, 0))
    obj = world.objects[object_id]
    obj.stock.setdefault("power_on", 1.0)

    world.apply_utility_outage("outage-1", "power")
    assert obj.stock.get("power_on") == 0.0
    assert not world.utility_online("power")

    world.clear_utility_outage("outage-1", "power")
    assert obj.stock.get("power_on") == 1.0
    assert world.utility_online("power")

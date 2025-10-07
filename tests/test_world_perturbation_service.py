from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world.perturbations import PerturbationService


def _make_services():
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.world.agents.clear()
    economy = Mock()
    service = PerturbationService(
        economy_service=economy,
        agents=loop.world.agents,
        objects=loop.world.objects,
        emit_event=Mock(),
        request_ctx_reset=loop.world.request_ctx_reset,
        tick_supplier=lambda: loop.tick,
    )
    return loop.world, economy, service


def test_apply_price_spike_forwards_calls() -> None:
    _, economy, service = _make_services()

    service.apply_price_spike("evt", magnitude=2.0, targets=["meal_cost"])

    economy.apply_price_spike.assert_called_once_with(
        "evt", magnitude=2.0, targets=["meal_cost"]
    )


def test_apply_arranged_meet_moves_agents() -> None:
    world, _, service = _make_services()
    world.register_object(
        object_id="cafe_1",
        object_type="cafe",
        position=(3, 4),
    )

    world.spawn_agent("alice", (0, 0))
    world.spawn_agent("bob", (1, 1))

    service.apply_arranged_meet(location="cafe_1", targets=["alice", "bob"])

    assert world.agents["alice"].position == (3, 4)
    assert world.agents["bob"].position == (3, 4)

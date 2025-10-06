from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world import AgentSnapshot


@pytest.fixture()
def simulation_loop() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.world.agents.clear()
    loop.world.objects.clear()
    return loop


def test_adapter_reflects_world_state(simulation_loop: SimulationLoop) -> None:
    loop = simulation_loop
    adapter = loop.world_adapter
    world = loop.world

    world.register_object(object_id="stove_1", object_type="stove", position=(1, 0))
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5},
    )

    assert "alice" in adapter.agent_snapshots_view()
    assert adapter.objects["stove_1"].object_type == "stove"
    assert adapter.queue_manager is world.queue_manager


def test_adapter_prevents_mutation(simulation_loop: SimulationLoop) -> None:
    adapter = simulation_loop.world_adapter

    with pytest.raises(TypeError):
        adapter.objects["new"] = object()  # type: ignore[index]


def test_adapter_consumes_ctx_reset_requests(simulation_loop: SimulationLoop) -> None:
    loop = simulation_loop
    adapter = loop.world_adapter
    world = loop.world

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5},
    )
    world.request_ctx_reset("alice")
    assert adapter.consume_ctx_reset_requests() == {"alice"}
    assert not adapter.consume_ctx_reset_requests()

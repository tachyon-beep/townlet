from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world import AgentSnapshot
from townlet.world.core import WorldContext


@pytest.fixture()
def simulation_loop() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.world.agents.clear()
    loop.world.objects.clear()
    return loop


def test_world_context_mirrors_world_state(simulation_loop: SimulationLoop) -> None:
    world = simulation_loop.world
    context = world.context

    assert isinstance(context, WorldContext)
    assert simulation_loop.world_context is context

    # mutate state and ensure context sees the changes
    world.register_object(object_id="fridge_1", object_type="fridge", position=(0, 0))
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5},
    )

    assert context.objects_view()["fridge_1"].object_type == "fridge"
    assert "alice" in context.agents_view()
    assert context.queue_manager is world.queue_manager
    assert context.affordance_service is getattr(world, "_affordance_service")


def test_world_context_event_and_console_bridge(simulation_loop: SimulationLoop) -> None:
    world = simulation_loop.world
    context = world.context

    context.emit_event("test_event", {"payload": 1})
    events = world.drain_events()
    assert events and events[-1]["event"] == "test_event"

    console_service = getattr(world, "_console")
    assert context.console is console_service
    assert context.console_bridge is console_service.bridge

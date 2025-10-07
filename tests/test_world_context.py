from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world import AgentSnapshot
from townlet.world.agents.nightly_reset import NightlyResetService
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
    assert context.affordance_service is world._affordance_service  # pylint: disable=protected-access

    adapter = simulation_loop.world_adapter
    assert adapter.queue_manager is world.queue_manager
    with pytest.raises(TypeError):
        adapter.objects["new_object"] = object()  # type: ignore[index]


def test_world_context_event_and_console_bridge(simulation_loop: SimulationLoop) -> None:
    world = simulation_loop.world
    context = world.context

    context.emit_event("test_event", {"payload": 1})
    events = world.drain_events()
    assert events and events[-1]["event"] == "test_event"

    console_service = world._console  # pylint: disable=protected-access
    assert context.console is console_service
    assert context.console_bridge is console_service.bridge


def test_world_context_nightly_reset_proxy(
    simulation_loop: SimulationLoop, monkeypatch: pytest.MonkeyPatch
) -> None:
    world = simulation_loop.world
    captured: list[int] = []

    def fake_apply(self: NightlyResetService, tick: int) -> list[str]:
        captured.append(tick)
        return ["ok"]

    monkeypatch.setattr(NightlyResetService, "apply", fake_apply)
    world.tick = 123

    result = world.context.apply_nightly_reset(world.tick)

    assert captured == [123]
    assert result == ["ok"]

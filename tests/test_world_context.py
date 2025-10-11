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
    assert context.observation_service is not None

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




def test_world_context_reset_deterministic(simulation_loop: SimulationLoop) -> None:
    world = simulation_loop.world
    context = world.context

    # Produce an event and mutate tick to ensure reset clears state
    context.emit_event("reset.test", {"value": 1})
    world.tick = 42

    context.reset(seed=123)
    first_random = world.rng.random()

    # Events drained and tick reset
    assert world.tick == 0
    assert world.drain_events() == []

    context.reset(seed=123)
    second_random = world.rng.random()

    assert first_random == second_random
    assert world.tick == 0


def test_world_context_tick_executes_actions(simulation_loop: SimulationLoop) -> None:
    loop = simulation_loop
    world = loop.world
    context = world.context

    world.lifecycle_service.spawn_agent(
        "alice",
        (0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=0.0,
        home_position=(0, 0),
    )

    context.apply_actions({"alice": {"kind": "move", "position": (1, 1)}})

    result = context.tick(
        tick=1,
        console_operations=[],
        prepared_actions={},
        lifecycle=loop.lifecycle,
        perturbations=loop.perturbations,
        ticks_per_day=loop._ticks_per_day,
    )

    assert world.agents["alice"].position == (1, 1)
    assert result.actions["alice"]["kind"] == "move"
    assert isinstance(result.console_results, list)


def test_world_context_apply_actions_validation(simulation_loop: SimulationLoop) -> None:
    loop = simulation_loop
    world = loop.world
    context = world.context

    world.lifecycle_service.spawn_agent(
        "alice",
        (0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=0.0,
        home_position=(0, 0),
    )

    context.apply_actions({"alice": {"kind": "move", "position": (1, 1)}})
    context.apply_actions({"alice": None})

    result = context.tick(
        tick=1,
        console_operations=[],
        prepared_actions={},
        lifecycle=loop.lifecycle,
        perturbations=loop.perturbations,
        ticks_per_day=loop._ticks_per_day,
    )

    assert "alice" not in result.actions  # None cleared the pending action

    with pytest.raises(TypeError):
        context.apply_actions({"alice": 42})


def test_world_context_tick_merges_pending_and_prepared(simulation_loop: SimulationLoop) -> None:
    loop = simulation_loop
    world = loop.world
    context = world.context

    world.lifecycle_service.spawn_agent(
        "alice",
        (0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=0.0,
        home_position=(0, 0),
    )

    context.apply_actions({"alice": {"kind": "move", "position": (1, 1)}})
    prepared = {"alice": {"kind": "move", "position": (2, 2)}}

    result = context.tick(
        tick=1,
        console_operations=[],
        prepared_actions=prepared,
        lifecycle=loop.lifecycle,
        perturbations=loop.perturbations,
        ticks_per_day=loop._ticks_per_day,
    )

    assert world.agents["alice"].position == (2, 2)
    assert result.actions["alice"]["position"] == (2, 2)
    assert context._pending_actions == {}


def test_world_context_tick_triggers_nightly_reset(
    simulation_loop: SimulationLoop, monkeypatch: pytest.MonkeyPatch
) -> None:
    loop = simulation_loop
    world = loop.world
    context = world.context
    captured: list[int] = []

    def fake_apply(self, tick: int) -> list[str]:
        captured.append(tick)
        return ["ok"]

    monkeypatch.setattr(type(context.nightly_reset_service), "apply", fake_apply, raising=False)

    result = context.tick(
        tick=loop._ticks_per_day or 1,
        console_operations=[],
        prepared_actions={},
        lifecycle=loop.lifecycle,
        perturbations=loop.perturbations,
        ticks_per_day=loop._ticks_per_day,
    )

    assert isinstance(result.termination_reasons, dict)
    expected_tick = loop._ticks_per_day or 1
    assert captured == [expected_tick]


def test_world_context_observe_uses_configured_service(simulation_loop: SimulationLoop) -> None:
    context = simulation_loop.world.context
    context.state.lifecycle_service.spawn_agent(
        "sample_agent",
        (0, 0),
        needs={"hunger": 0.5, "energy": 0.5},
        wallet=5.0,
        home_position=(0, 0),
    )
    envelope = context.observe()
    assert envelope.tick == context.state.tick
    assert envelope.agents

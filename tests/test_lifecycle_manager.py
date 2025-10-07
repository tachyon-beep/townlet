from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.lifecycle.manager import LifecycleManager
from townlet.world.agents.lifecycle import LifecycleService
from townlet.world.grid import AgentSnapshot, WorldState


def _make_world(respawn_delay: int = 0) -> tuple[LifecycleManager, WorldState]:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.lifecycle.respawn_delay_ticks = respawn_delay
    world = WorldState.from_config(config)
    world.agents.clear()
    world.tick = 0
    manager = LifecycleManager(config)
    return manager, world


def _spawn_agent(world: WorldState, agent_id: str = "alice") -> AgentSnapshot:
    snapshot = world.lifecycle_service.spawn_agent(
        agent_id,
        (0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=0.0,
    )
    return world.agents[snapshot.agent_id]


def test_respawn_after_delay() -> None:
    manager, world = _make_world(respawn_delay=2)
    snapshot = _spawn_agent(world)
    snapshot.needs["hunger"] = 0.01
    terminated = manager.evaluate(world, tick=0)
    assert terminated["alice"] is True
    manager.finalize(world, tick=0, terminated=terminated)
    assert "alice" not in world.agents
    manager.process_respawns(world, tick=1)
    assert "alice" not in world.agents
    manager.process_respawns(world, tick=2)
    assert "alice" not in world.agents
    respawned_id = next(agent_id for agent_id in world.agents if agent_id.startswith("alice#"))
    respawned = world.agents[respawned_id]
    assert respawned.needs == {"hunger": 0.5, "hygiene": 0.5, "energy": 0.5}
    assert respawned.shift_state == "pre_shift"
    assert respawned.home_position == (0, 0)
    assert respawned.origin_agent_id == "alice"


def test_employment_exit_emits_event_and_resets_state() -> None:
    manager, world = _make_world(respawn_delay=0)
    snapshot = _spawn_agent(world)
    world.employment.enqueue_exit(world, snapshot.agent_id, tick=0)
    terminated = manager.evaluate(world, tick=0)
    assert terminated[snapshot.agent_id] is True
    manager.finalize(world, tick=0, terminated=terminated)
    events = world.drain_events()
    assert any(
        event.get("event") == "employment_exit_processed"
        and event.get("agent_id") == snapshot.agent_id
        for event in events
    )
    assert world.employment.has_context(snapshot.agent_id) is False
    assert not world.employment.exit_queue_contains(snapshot.agent_id)


def test_employment_daily_reset() -> None:
    manager, world = _make_world(respawn_delay=0)
    _spawn_agent(world)
    world.set_employment_exits_today(5)
    terminated = manager.evaluate(world, tick=0)
    manager.finalize(world, tick=0, terminated=terminated)
    assert world.employment_exits_today() == 0


def test_termination_reasons_captured() -> None:
    manager, world = _make_world(respawn_delay=0)
    alice = _spawn_agent(world)
    alice.needs["hunger"] = 0.01
    manager.evaluate(world, tick=0)
    reasons = manager.termination_reasons()
    assert reasons.get("alice") == "faint"
    world.employment.enqueue_exit(world, alice.agent_id, tick=1)
    manager.evaluate(world, tick=1)
    reasons = manager.termination_reasons()
    assert reasons.get(alice.agent_id) == "eviction"


def test_world_spawn_agent_delegates(monkeypatch: pytest.MonkeyPatch) -> None:
    _, world = _make_world(respawn_delay=0)
    calls: list[tuple] = []
    original = LifecycleService.spawn_agent

    def wrapped(self: LifecycleService, *args, **kwargs):
        calls.append((args, kwargs))
        return original(self, *args, **kwargs)

    monkeypatch.setattr(LifecycleService, "spawn_agent", wrapped)

    world.spawn_agent("delegate", (2, 0))

    assert calls

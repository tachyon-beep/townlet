from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.world.agents.lifecycle import LifecycleService
from townlet.world.grid import WorldState


@pytest.fixture()
def world() -> WorldState:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.agents.clear()
    world.tick = 0
    world.drain_events()
    return world


def _spawn(world: WorldState, agent_id: str = "alice", position: tuple[int, int] = (0, 0)):
    return world.lifecycle_service.spawn_agent(
        agent_id,
        position,
        needs={"hunger": 0.5, "hygiene": 0.6, "energy": 0.7},
        wallet=1.0,
    )


def test_spawn_agent_emits_event_and_allocates(world: WorldState) -> None:
    world.drain_events()
    snapshot = _spawn(world, "alice", (0, 0))

    assert snapshot.agent_id in world.agents
    assert world.embedding_allocator.has_assignment(snapshot.agent_id)

    events = world.drain_events()
    assert any(event.get("event") == "agent_spawned" for event in events)


def test_teleport_agent_updates_position(world: WorldState) -> None:
    _spawn(world, "alice", (0, 0))
    world.drain_events()

    dest = world.lifecycle_service.teleport_agent("alice", (3, 2))

    assert dest == (3, 2)
    assert world.agent_position("alice") == (3, 2)

    events = world.drain_events()
    assert any(event.get("event") == "agent_teleported" for event in events)


def test_remove_agent_releases_resources(world: WorldState) -> None:
    snapshot = _spawn(world, "alice", (0, 0))
    world.drain_events()

    world.register_object(object_id="stove_1", object_type="stove", position=(1, 0))
    world._active_reservations["stove_1"] = snapshot.agent_id
    world.objects["stove_1"].occupied_by = snapshot.agent_id
    world.queue_manager.request_access("stove_1", snapshot.agent_id, world.tick)

    blueprint = world.lifecycle_service.remove_agent(snapshot.agent_id, tick=5)

    assert blueprint["agent_id"] == snapshot.agent_id
    assert snapshot.agent_id not in world.agents
    assert not world.embedding_allocator.has_assignment(snapshot.agent_id)
    assert world.queue_manager.active_agent("stove_1") != snapshot.agent_id
    assert world._active_reservations.get("stove_1") is None
    assert world.objects["stove_1"].occupied_by is None
    assert world.employment.has_context(snapshot.agent_id) is False
    assert world.queue_manager.queue_snapshot("stove_1") == []

    events = world.drain_events()
    assert any(event.get("event") == "agent_removed" for event in events)


def test_kill_agent_emits_event(world: WorldState, monkeypatch: pytest.MonkeyPatch) -> None:
    snapshot = _spawn(world, "alice", (0, 0))
    world.drain_events()

    remove_calls: list[tuple] = []

    original_remove = LifecycleService.remove_agent

    def wrapped_remove(self: LifecycleService, *args, **kwargs):
        remove_calls.append(args)
        return original_remove(self, *args, **kwargs)

    monkeypatch.setattr(LifecycleService, "remove_agent", wrapped_remove)

    assert world.lifecycle_service.kill_agent(snapshot.agent_id, reason="test")
    assert remove_calls

    events = world.drain_events()
    assert any(event.get("event") == "agent_killed" for event in events)


def test_respawn_agent_restores_profile(world: WorldState) -> None:
    original = _spawn(world, "alice", (0, 0))
    blueprint = world.lifecycle_service.remove_agent(original.agent_id, tick=0)
    world.drain_events()

    world.lifecycle_service.respawn_agent(blueprint)

    respawned_id = next(agent_id for agent_id in world.agents if agent_id.startswith("alice"))
    respawned = world.agents[respawned_id]
    assert respawned.origin_agent_id == original.agent_id
    assert respawned.home_position == original.home_position
    assert respawned.needs["hunger"] == pytest.approx(0.5)

    events = world.drain_events()
    assert any(event.get("event") == "agent_respawn" for event in events)


def test_sync_reservation_for_agent_invokes_callback(
    world: WorldState, monkeypatch: pytest.MonkeyPatch
) -> None:
    _spawn(world, "alice", (0, 0))
    world._active_reservations["stove_1"] = "alice"

    called: list[str] = []
    monkeypatch.setattr(
        LifecycleService,
        "sync_reservation",
        lambda self, object_id: called.append(object_id),
    )

    world.lifecycle_service.sync_reservation_for_agent("alice")

    assert called == ["stove_1"]


def test_generate_agent_id_unique(world: WorldState) -> None:
    first = world.lifecycle_service.generate_agent_id("agent")
    second = world.lifecycle_service.generate_agent_id("agent")

    assert first != second
    assert first.startswith("agent#")
    assert second.startswith("agent#")

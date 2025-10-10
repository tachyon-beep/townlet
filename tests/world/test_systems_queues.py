from __future__ import annotations

from types import SimpleNamespace

from townlet.config.conflict import QueueFairnessConfig
from townlet.world.queue.conflict import QueueConflictTracker
from townlet.world.queue.manager import QueueManager
from townlet.world.spatial import WorldSpatialIndex
from townlet.world.events import EventDispatcher
from townlet.world.rng import RngStreamManager
from townlet.world.systems import SystemContext, queues


def _make_manager() -> QueueManager:
    cfg = SimpleNamespace(queue_fairness=QueueFairnessConfig())
    return QueueManager(cfg)


def test_request_access_updates_reservation() -> None:
    manager = _make_manager()
    objects = {
        "stall": SimpleNamespace(position=(1, 2), occupied_by=None),
    }
    active: dict[str, str] = {}
    spatial_index = WorldSpatialIndex()

    granted = queues.request_access(
        manager=manager,
        objects=objects,
        active_reservations=active,
        spatial_index=spatial_index,
        object_id="stall",
        agent_id="alice",
        tick=0,
    )

    assert granted is True
    assert active["stall"] == "alice"
    assert objects["stall"].occupied_by == "alice"
    assert (1, 2) in spatial_index.reservation_tiles()


def test_refresh_reservations_clears_inactive_slots() -> None:
    manager = _make_manager()
    objects = {
        "stall": SimpleNamespace(position=(0, 0), occupied_by=None),
    }
    active: dict[str, str] = {}
    spatial_index = WorldSpatialIndex()

    queues.request_access(
        manager=manager,
        objects=objects,
        active_reservations=active,
        spatial_index=spatial_index,
        object_id="stall",
        agent_id="alice",
        tick=0,
    )
    manager.release("stall", "alice", tick=5, success=False)

    queues.refresh_reservations(
        manager=manager,
        objects=objects,
        active_reservations=active,
        spatial_index=spatial_index,
    )

    assert "stall" not in active
    assert objects["stall"].occupied_by is None
    assert (0, 0) not in spatial_index.reservation_tiles()


def test_record_blocked_attempt_returns_bool() -> None:
    manager = _make_manager()
    assert isinstance(queues.record_blocked_attempt(manager, "stall"), bool)


def test_step_records_ghost_step_conflict() -> None:
    cfg = SimpleNamespace(queue_fairness=QueueFairnessConfig(ghost_step_after=1))
    manager = QueueManager(cfg)
    objects = {
        "stall": SimpleNamespace(position=(0, 0), occupied_by=None),
    }
    active: dict[str, str] = {}
    spatial_index = WorldSpatialIndex()

    queues.request_access(
        manager=manager,
        objects=objects,
        active_reservations=active,
        spatial_index=spatial_index,
        object_id="stall",
        agent_id="alice",
        tick=0,
    )
    queues.request_access(
        manager=manager,
        objects=objects,
        active_reservations=active,
        spatial_index=spatial_index,
        object_id="stall",
        agent_id="bob",
        tick=0,
    )

    class DummyWorld:
        def __init__(self) -> None:
            self.events: list[dict[str, object]] = []
            rivalry_cfg = SimpleNamespace(
                ghost_step_boost=1.0,
                handover_boost=0.4,
                queue_length_boost=0.25,
            )
            self.config = SimpleNamespace(conflict=SimpleNamespace(rivalry=rivalry_cfg))
            self.tick = 0

        def update_relationship(self, *args, **kwargs) -> None:
            return None

        def _emit_event(self, name: str, payload: dict[str, object]) -> None:
            self.events.append({"event": name, **payload})

    tracker = QueueConflictTracker(world=DummyWorld(), record_rivalry_conflict=lambda *a, **k: None)

    class DummyService:
        def __init__(self) -> None:
            self.removed: list[str] = []

        def remove_agent(self, agent_id: str) -> None:
            self.removed.append(agent_id)

    service = DummyService()

    class DummyState:
        def __init__(self) -> None:
            self.tick = 5
            self.queue_manager = manager
            self._active_reservations = active
            self.objects = objects
            self._affordance_service = service
            self._queue_conflicts = tracker

        def refresh_reservations(self) -> None:
            queues.refresh_reservations(
                manager=manager,
                objects=self.objects,
                active_reservations=self._active_reservations,
                spatial_index=spatial_index,
            )

        def _record_queue_conflict(self, **payload: object) -> None:
            tracker.record_queue_conflict(**payload)

        def _sync_reservation(self, object_id: str) -> None:
            queues.sync_reservation(
                manager=manager,
                objects=self.objects,
                active_reservations=self._active_reservations,
                spatial_index=spatial_index,
                object_id=object_id,
            )

    state = DummyState()
    ctx = SystemContext(
        state=state,
        rng=RngStreamManager.from_seed(42),
        events=EventDispatcher(),
    )

    queues.step(ctx)

    assert manager.active_agent("stall") == "bob"
    assert service.removed == ["alice"]
    conflict_events = tracker.consume_rivalry_events()
    assert conflict_events
    assert conflict_events[0]["reason"] == "ghost_step"


def test_handle_handover_promotes_next_agent() -> None:
    manager = _make_manager()
    objects = {
        "stall": SimpleNamespace(position=(1, 2), occupied_by=None),
    }
    active: dict[str, str] = {}
    spatial_index = WorldSpatialIndex()

    assert queues.request_access(
        manager=manager,
        objects=objects,
        active_reservations=active,
        spatial_index=spatial_index,
        object_id="stall",
        agent_id="alice",
        tick=0,
    )
    queues.request_access(
        manager=manager,
        objects=objects,
        active_reservations=active,
        spatial_index=spatial_index,
        object_id="stall",
        agent_id="bob",
        tick=1,
    )
    waiting = manager.queue_snapshot("stall")
    events: list[dict[str, object]] = []

    def record_conflict(**payload: object) -> None:
        events.append(dict(payload))

    def sync_reservation(object_id: str) -> None:
        queues.sync_reservation(
            manager=manager,
            objects=objects,
            active_reservations=active,
            spatial_index=spatial_index,
            object_id=object_id,
        )

    queues.handle_handover(
        manager=manager,
        object_id="stall",
        departing_agent="alice",
        tick=5,
        waiting=waiting,
        preferred_agent=None,
        record_queue_conflict=record_conflict,
        queue_conflicts=None,
        sync_reservation=sync_reservation,
    )

    assert manager.active_agent("stall") == "bob"
    assert active["stall"] == "bob"
    assert objects["stall"].occupied_by == "bob"
    assert events
    assert events[0]["reason"] == "handover"
    assert events[0]["actor"] == "alice"
    assert events[0]["rival"] == "bob"
    assert events[0]["queue_length"] == len(waiting)


def test_handle_handover_respects_preferred_agent() -> None:
    manager = _make_manager()
    objects = {
        "stall": SimpleNamespace(position=(3, 4), occupied_by=None),
    }
    active: dict[str, str] = {}
    spatial_index = WorldSpatialIndex()

    assert queues.request_access(
        manager=manager,
        objects=objects,
        active_reservations=active,
        spatial_index=spatial_index,
        object_id="stall",
        agent_id="alice",
        tick=0,
    )
    queues.request_access(
        manager=manager,
        objects=objects,
        active_reservations=active,
        spatial_index=spatial_index,
        object_id="stall",
        agent_id="bob",
        tick=1,
    )
    queues.request_access(
        manager=manager,
        objects=objects,
        active_reservations=active,
        spatial_index=spatial_index,
        object_id="stall",
        agent_id="carol",
        tick=2,
    )
    waiting = manager.queue_snapshot("stall")
    events: list[dict[str, object]] = []

    def record_conflict(**payload: object) -> None:
        events.append(dict(payload))

    def sync_reservation(object_id: str) -> None:
        queues.sync_reservation(
            manager=manager,
            objects=objects,
            active_reservations=active,
            spatial_index=spatial_index,
            object_id=object_id,
        )

    queues.handle_handover(
        manager=manager,
        object_id="stall",
        departing_agent="alice",
        tick=10,
        waiting=waiting,
        preferred_agent="carol",
        record_queue_conflict=record_conflict,
        queue_conflicts=None,
        sync_reservation=sync_reservation,
    )

    assert manager.active_agent("stall") == "carol"
    assert active["stall"] == "carol"
    assert objects["stall"].occupied_by == "carol"
    assert events
    assert events[0]["rival"] == "carol"
    assert events[0]["queue_length"] == len(waiting)
    assert manager.metrics()["rotation_events"] >= 1

def test_step_calls_on_tick_and_refresh() -> None:
    class DummyManager:
        def __init__(self) -> None:
            self.calls: list[int] = []

        def on_tick(self, tick: int) -> None:
            self.calls.append(tick)

    class DummyState:
        def __init__(self) -> None:
            self.tick = 7
            self.queue_manager = DummyManager()
            self.refresh_calls = 0

        def refresh_reservations(self) -> None:
            self.refresh_calls += 1

    state = DummyState()
    ctx = SystemContext(
        state=state,
        rng=RngStreamManager.from_seed(123),
        events=EventDispatcher(),
    )

    queues.step(ctx)

    assert state.queue_manager.calls == [7]
    assert state.refresh_calls == 1

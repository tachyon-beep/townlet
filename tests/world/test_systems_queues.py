from __future__ import annotations

from types import SimpleNamespace

from townlet.config.conflict import QueueFairnessConfig
from townlet.world.queue.manager import QueueManager
from townlet.world.spatial import WorldSpatialIndex
from townlet.world.systems import queues


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

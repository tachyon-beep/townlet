"""Queue management helpers and tick integration."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping

from townlet.world.queue.manager import QueueManager
from townlet.world.spatial import WorldSpatialIndex

from .base import SystemContext


def step(ctx: SystemContext) -> None:
    """Run queue-related updates (WP2 Step 6 will populate)."""

    return


def request_access(
    *,
    manager: QueueManager,
    objects: Mapping[str, Any],
    active_reservations: MutableMapping[str, str],
    spatial_index: WorldSpatialIndex,
    object_id: str,
    agent_id: str,
    tick: int,
) -> bool:
    """Request access to ``object_id`` and synchronise reservation state."""

    granted = manager.request_access(object_id, agent_id, tick)
    sync_reservation(
        manager=manager,
        objects=objects,
        active_reservations=active_reservations,
        spatial_index=spatial_index,
        object_id=object_id,
    )
    return granted


def sync_reservation(
    *,
    manager: QueueManager,
    objects: Mapping[str, Any],
    active_reservations: MutableMapping[str, str],
    spatial_index: WorldSpatialIndex,
    object_id: str,
) -> None:
    """Synchronise reservation bookkeeping for ``object_id``."""

    active = manager.active_agent(object_id)
    obj = objects.get(object_id)
    if active is None:
        active_reservations.pop(object_id, None)
        if obj is not None:
            position = getattr(obj, "position", None)
            if position is not None:
                spatial_index.set_reservation(position, False)
            if hasattr(obj, "occupied_by"):
                obj.occupied_by = None
        return

    active_reservations[object_id] = active
    if obj is not None:
        position = getattr(obj, "position", None)
        if hasattr(obj, "occupied_by"):
            obj.occupied_by = active
        if position is not None:
            spatial_index.set_reservation(position, True)


def refresh_reservations(
    *,
    manager: QueueManager,
    objects: Mapping[str, Any],
    active_reservations: MutableMapping[str, str],
    spatial_index: WorldSpatialIndex,
) -> None:
    """Synchronise reservations for all known objects."""

    for object_id in list(objects.keys()):
        sync_reservation(
            manager=manager,
            objects=objects,
            active_reservations=active_reservations,
            spatial_index=spatial_index,
            object_id=object_id,
        )


def record_blocked_attempt(manager: QueueManager, object_id: str) -> bool:
    """Proxy to the queue manager's blocked attempt helper."""

    return manager.record_blocked_attempt(object_id)


__all__ = [
    "record_blocked_attempt",
    "refresh_reservations",
    "request_access",
    "step",
    "sync_reservation",
]

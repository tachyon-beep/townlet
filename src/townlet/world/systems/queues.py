"""Queue management helpers and tick integration."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Mapping, MutableMapping

from townlet.world.queue.manager import QueueManager
from townlet.world.spatial import WorldSpatialIndex

from .base import SystemContext


def step(ctx: SystemContext) -> None:
    """Synchronise queue state each tick."""

    state = ctx.state
    manager = getattr(state, "queue_manager", None)
    if manager is None:
        return

    tick = getattr(state, "tick", 0)
    on_tick = getattr(manager, "on_tick", None)
    if callable(on_tick):
        on_tick(tick)

    refresh = getattr(state, "refresh_reservations", None)
    if callable(refresh):
        refresh()

    _process_queue_conflicts(state, manager, tick)


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


def handle_handover(
    *,
    manager: QueueManager,
    object_id: str,
    departing_agent: str,
    tick: int,
    waiting: Sequence[str],
    preferred_agent: str | None,
    record_queue_conflict: Callable[..., None] | None = None,
    queue_conflicts: Any | None = None,
    sync_reservation: Callable[[str], None] | None = None,
    intensity: float = 0.5,
) -> None:
    """Promote the next queued agent after a successful affordance completion."""

    if preferred_agent not in waiting:
        preferred_agent = None
    if preferred_agent is not None:
        manager.promote_agent(object_id, preferred_agent)

    manager.release(object_id, departing_agent, tick, success=True)

    if callable(sync_reservation):
        sync_reservation(object_id)

    if not waiting:
        return

    rival = preferred_agent if preferred_agent is not None else waiting[0]
    _emit_queue_conflict(
        record_conflict=record_queue_conflict,
        queue_conflicts=queue_conflicts,
        payload={
            "object_id": object_id,
            "actor": departing_agent,
            "rival": rival,
            "reason": "handover",
            "queue_length": len(waiting),
            "intensity": intensity,
        },
    )


def _emit_queue_conflict(
    *,
    record_conflict: Callable[..., None] | None,
    queue_conflicts: Any | None,
    payload: Mapping[str, object],
) -> None:
    if callable(record_conflict):
        record_conflict(**payload)
        return
    if queue_conflicts is not None:
        try:
            queue_conflicts.record_queue_conflict(**payload)
        except Exception:
            pass


def _process_queue_conflicts(state: Any, manager: QueueManager, tick: int) -> None:
    active_reservations: Mapping[str, str] = getattr(state, "_active_reservations", {})
    if not active_reservations:
        return

    record_conflict = getattr(state, "_record_queue_conflict", None)
    sync_reservation = getattr(state, "_sync_reservation", None)
    queue_conflicts = getattr(state, "_queue_conflicts", None)
    runtime_service = getattr(state, "_affordance_service", None)

    for object_id, occupant in list(active_reservations.items()):
        queue = manager.queue_snapshot(object_id)
        if not queue:
            continue
        if not manager.record_blocked_attempt(object_id):
            continue

        waiting = manager.queue_snapshot(object_id)
        rival = waiting[0] if waiting else None
        manager.release(object_id, occupant, tick, success=False)
        manager.requeue_to_tail(object_id, occupant, tick)

        if runtime_service is not None:
            try:
                runtime_service.remove_agent(occupant)
            except AttributeError:
                pass

        if callable(sync_reservation):
            sync_reservation(object_id)

        rival_id = rival if rival is not None else occupant
        _emit_queue_conflict(
            record_conflict=record_conflict,
            queue_conflicts=queue_conflicts,
            payload={
                "object_id": object_id,
                "actor": occupant,
                "rival": rival_id,
                "reason": "ghost_step",
                "queue_length": len(waiting),
                "intensity": None,
            },
        )

__all__ = [
    "handle_handover",
    "record_blocked_attempt",
    "refresh_reservations",
    "request_access",
    "step",
    "sync_reservation",
]

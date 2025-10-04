"""Helper utilities for building observation-friendly world snapshots."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from townlet.world.grid import AgentSnapshot, WorldState
else:  # pragma: no cover - runtime typing fallbacks
    AgentSnapshot = Any  # type: ignore[assignment]
    WorldState = Any  # type: ignore[assignment]


def build_local_cache(
    world: WorldState,
    snapshots: Mapping[str, AgentSnapshot],
) -> tuple[
    dict[tuple[int, int], list[str]],
    dict[tuple[int, int], list[str]],
    set[tuple[int, int]],
]:
    """Return lookup tables describing nearby agents, objects, and reservations."""

    agent_lookup: dict[tuple[int, int], list[str]] = {}
    for agent_id, snapshot in snapshots.items():
        position = world.agent_position(agent_id) or snapshot.position
        agent_lookup.setdefault(position, []).append(agent_id)

    object_lookup: dict[tuple[int, int], list[str]] = {}
    for position, object_ids_tuple in world.objects_by_position_view().items():
        filtered = [obj_id for obj_id in object_ids_tuple if obj_id in world.objects]
        if filtered:
            object_lookup[position] = filtered

    reservation_tiles = set(world.reservation_tiles())
    return agent_lookup, object_lookup, reservation_tiles


def local_view(
    world: WorldState,
    agent_id: str,
    radius: int,
    *,
    include_agents: bool = True,
    include_objects: bool = True,
) -> dict[str, Any]:
    """Return a structured neighborhood snapshot around ``agent_id``."""

    snapshots = world.agent_snapshots_view()
    target_snapshot = snapshots.get(agent_id)
    if target_snapshot is None:
        return {
            "center": None,
            "radius": radius,
            "tiles": [],
            "agents": [],
            "objects": [],
        }

    cx, cy = target_snapshot.position
    objects_by_position = world.objects_by_position_view() if include_objects else {}
    reservation_tiles = world.reservation_tiles() if include_objects else frozenset()

    tiles: list[list[dict[str, Any]]] = []
    seen_agents: dict[str, dict[str, Any]] = {}
    seen_objects: dict[str, dict[str, Any]] = {}

    for dy in range(-radius, radius + 1):
        row: list[dict[str, Any]] = []
        for dx in range(-radius, radius + 1):
            x = cx + dx
            y = cy + dy
            position = (x, y)
            agent_ids_tuple = world.agents_at_tile(position) if include_agents else ()
            agent_ids = list(agent_ids_tuple)
            object_ids_for_tile = (
                list(objects_by_position.get(position, ())) if include_objects else []
            )

            if include_agents:
                for agent_id_at_tile in agent_ids:
                    if agent_id_at_tile == agent_id:
                        continue
                    other_snapshot = snapshots.get(agent_id_at_tile)
                    if other_snapshot is None:
                        continue
                    seen_agents.setdefault(
                        agent_id_at_tile,
                        {
                            "agent_id": agent_id_at_tile,
                            "position": other_snapshot.position,
                            "on_shift": other_snapshot.on_shift,
                        },
                    )

            if include_objects:
                for object_id in object_ids_for_tile:
                    obj = world.objects.get(object_id)
                    if obj is None:
                        continue
                    seen_objects.setdefault(
                        object_id,
                        {
                            "object_id": object_id,
                            "object_type": obj.object_type,
                            "position": obj.position,
                            "occupied_by": obj.occupied_by,
                        },
                    )

            reservation_active = bool(object_ids_for_tile) and position in reservation_tiles

            row.append(
                {
                    "position": position,
                    "self": position == (cx, cy),
                    "agent_ids": agent_ids,
                    "object_ids": object_ids_for_tile,
                    "reservation_active": reservation_active,
                }
            )
        tiles.append(row)

    return {
        "center": (cx, cy),
        "radius": radius,
        "tiles": tiles,
        "agents": list(seen_agents.values()),
        "objects": list(seen_objects.values()),
    }


def agent_context(world: WorldState, agent_id: str) -> dict[str, Any]:
    """Return scalar context fields consumed by observation builders."""

    snapshot = world.agent_snapshots_view().get(agent_id)
    if snapshot is None:
        return {}
    return {
        "needs": dict(getattr(snapshot, "needs", {})),
        "wallet": float(getattr(snapshot, "wallet", 0.0)),
        "lateness_counter": getattr(snapshot, "lateness_counter", 0),
        "on_shift": bool(getattr(snapshot, "on_shift", False)),
        "attendance_ratio": float(getattr(snapshot, "attendance_ratio", 0.0)),
        "wages_withheld": float(getattr(snapshot, "wages_withheld", 0.0)),
        "shift_state": getattr(snapshot, "shift_state", "pre_shift"),
        "last_action_id": getattr(snapshot, "last_action_id", ""),
        "last_action_success": bool(getattr(snapshot, "last_action_success", False)),
        "last_action_duration": getattr(snapshot, "last_action_duration", 0),
        "wages_paid": _maybe_call(
            world,
            "_employment_context_wages",
            getattr(snapshot, "agent_id", agent_id),
            default=float(getattr(snapshot, "wages_paid", 0.0)),
        ),
        "punctuality_bonus": _maybe_call(
            world,
            "_employment_context_punctuality",
            getattr(snapshot, "agent_id", agent_id),
            default=float(getattr(snapshot, "punctuality_bonus", 0.0)),
        ),
    }


def _maybe_call(world: object, attr: str, *args: object, default: float = 0.0) -> float:
    func = getattr(world, attr, None)
    if callable(func):
        try:
            return float(func(*args))
        except Exception:  # pragma: no cover - defensive fallback
            return default
    return default


def find_nearest_object_of_type(
    world: WorldState, object_type: str, origin: tuple[int, int]
) -> tuple[int, int] | None:
    """Return the location of the closest object matching ``object_type``."""

    targets = [
        obj.position
        for obj in world.objects.values()
        if obj.object_type == object_type and obj.position is not None
    ]
    if not targets:
        return None
    ox, oy = origin
    return min(targets, key=lambda pos: (pos[0] - ox) ** 2 + (pos[1] - oy) ** 2)


def snapshot_precondition_context(context: Mapping[str, Any]) -> dict[str, Any]:
    """Deep-copy precondition context into a JSON-serialisable structure."""

    def _clone(value: Any) -> Any:
        if isinstance(value, dict):
            return {str(key): _clone(val) for key, val in value.items()}
        if isinstance(value, list):
            return [_clone(item) for item in value]
        if isinstance(value, tuple):
            return [_clone(item) for item in value]
        return value

    return {str(key): _clone(val) for key, val in context.items()}


__all__ = [
    "agent_context",
    "build_local_cache",
    "find_nearest_object_of_type",
    "local_view",
    "snapshot_precondition_context",
]

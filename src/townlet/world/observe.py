"""Observation helpers extracted for the modular world implementation."""

from __future__ import annotations

from typing import Any

from townlet.world.core.runtime_adapter import ensure_world_adapter
from townlet.world.observations.interfaces import WorldRuntimeAdapterProtocol


def local_view(
    world: WorldRuntimeAdapterProtocol | object,
    agent_id: str,
    radius: int,
    *,
    include_agents: bool = True,
    include_objects: bool = True,
) -> dict[str, Any]:
    """Return a structured neighbourhood snapshot around ``agent_id``."""

    adapter = ensure_world_adapter(world)

    snapshots = adapter.agent_snapshots_view()
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
    objects_by_position = adapter.objects_by_position_view() if include_objects else {}
    objects_snapshot = adapter.objects_snapshot() if include_objects else {}
    reservation_tiles = set(adapter.reservation_tiles()) if include_objects else set()

    tiles: list[list[dict[str, Any]]] = []
    seen_agents: dict[str, dict[str, Any]] = {}
    seen_objects: dict[str, dict[str, Any]] = {}

    for dy in range(-radius, radius + 1):
        row: list[dict[str, Any]] = []
        for dx in range(-radius, radius + 1):
            x = cx + dx
            y = cy + dy
            position = (x, y)
            agent_ids_tuple = adapter.agents_at_tile(position) if include_agents else ()
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
                    obj = objects_snapshot.get(object_id)
                    if obj is None:
                        continue
                    seen_objects.setdefault(
                        object_id,
                        {
                            "object_id": object_id,
                            "object_type": obj.get("object_type"),
                            "position": obj.get("position"),
                            "occupied_by": obj.get("occupied_by"),
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


def find_nearest_object_of_type(
    world: WorldRuntimeAdapterProtocol | object,
    object_type: str,
    origin: tuple[int, int],
) -> tuple[int, int] | None:
    """Return the location of the closest object matching ``object_type``."""

    adapter = ensure_world_adapter(world)

    try:
        snapshot = adapter.objects_snapshot()
    except AttributeError:  # pragma: no cover - defensive fallback
        snapshot = {}

    if not snapshot:
        objects = getattr(adapter, "objects", {})
        snapshot = {
            object_id: {
                "object_type": getattr(obj, "object_type", None),
                "position": getattr(obj, "position", None),
            }
            for object_id, obj in objects.items()
        }

    targets = [
        payload.get("position")
        for payload in snapshot.values()
        if payload.get("object_type") == object_type and payload.get("position") is not None
    ]
    if not targets:
        return None
    ox, oy = origin
    return min(targets, key=lambda pos: (pos[0] - ox) ** 2 + (pos[1] - oy) ** 2)


__all__ = ["find_nearest_object_of_type", "local_view"]

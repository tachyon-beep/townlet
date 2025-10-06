"""Local cache helpers extracted during WP-C Phase 4.

These utilities mirror the legacy functions previously hosted in
``townlet.world.observation`` and are consumed by the observation builder to
construct egocentric spatial views around each agent.
"""

from __future__ import annotations

from collections.abc import Mapping

from townlet.world.agents.snapshot import AgentSnapshot
from townlet.world.core.runtime_adapter import ensure_world_adapter
from townlet.world.observations.interfaces import WorldRuntimeAdapterProtocol


def build_local_cache(
    world: WorldRuntimeAdapterProtocol | object,
    snapshots: Mapping[str, AgentSnapshot],
) -> tuple[
    dict[tuple[int, int], list[str]],
    dict[tuple[int, int], list[str]],
    set[tuple[int, int]],
]:
    """Return lookup tables describing nearby agents, objects, and reservations."""

    adapter = ensure_world_adapter(world)

    agent_lookup: dict[tuple[int, int], list[str]] = {}
    for agent_id, snapshot in snapshots.items():
        position = adapter.agent_position(agent_id) or snapshot.position
        agent_lookup.setdefault(position, []).append(agent_id)

    objects_view = adapter.objects
    object_lookup: dict[tuple[int, int], list[str]] = {}
    for position, object_ids_tuple in adapter.objects_by_position_view().items():
        filtered = [obj_id for obj_id in object_ids_tuple if obj_id in objects_view]
        if filtered:
            object_lookup[position] = filtered

    reservation_tiles = set(adapter.reservation_tiles())
    return agent_lookup, object_lookup, reservation_tiles


__all__ = ["build_local_cache"]

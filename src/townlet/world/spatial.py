"""Spatial indexing utilities extracted from the legacy world implementation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from townlet.world.agents.snapshot import AgentSnapshot

if TYPE_CHECKING:  # pragma: no cover - import for type hints only
    from .grid import InteractiveObject


class WorldSpatialIndex:
    """Maintains spatial lookups to accelerate world queries."""

    def __init__(self) -> None:
        self._agents_by_position: dict[tuple[int, int], list[str]] = {}
        self._positions_by_agent: dict[str, tuple[int, int]] = {}
        self._reservation_tiles: set[tuple[int, int]] = set()

    # Agent bookkeeping -------------------------------------------------
    def rebuild(
        self,
        agents: Mapping[str, AgentSnapshot],
        objects: Mapping[str, InteractiveObject],
        active_reservations: Mapping[str, str | None],
    ) -> None:
        """Recalculate cached lookups from authoritative world state."""

        self._agents_by_position.clear()
        self._positions_by_agent.clear()
        for agent_id, snapshot in agents.items():
            raw_position = getattr(snapshot, "position", None)
            if raw_position is None or len(raw_position) < 2:
                continue
            position = (int(raw_position[0]), int(raw_position[1]))
            self._positions_by_agent[agent_id] = position
            bucket = self._agents_by_position.setdefault(position, [])
            bucket.append(agent_id)
        for bucket in self._agents_by_position.values():
            bucket.sort()
        self._reservation_tiles.clear()
        for object_id, occupant in active_reservations.items():
            if not occupant:
                continue
            obj = objects.get(object_id)
            if obj is None:
                continue
            obj_position = getattr(obj, "position", None)
            if obj_position is None or len(obj_position) < 2:
                continue
            position_tuple = (int(obj_position[0]), int(obj_position[1]))
            self._reservation_tiles.add(position_tuple)

    def insert_agent(self, agent_id: str, position: tuple[int, int]) -> None:
        """Register a new agent at ``position`` without rebuilding indices."""

        self._positions_by_agent[agent_id] = position
        bucket = self._agents_by_position.setdefault(position, [])
        if agent_id not in bucket:
            bucket.append(agent_id)

    def move_agent(self, agent_id: str, position: tuple[int, int]) -> None:
        """Update cached lookups when an agent moves to ``position``."""

        previous = self._positions_by_agent.get(agent_id)
        if previous is not None:
            bucket = self._agents_by_position.get(previous)
            if bucket is not None:
                try:
                    bucket.remove(agent_id)
                except ValueError:
                    pass
                if not bucket:
                    self._agents_by_position.pop(previous, None)
        self.insert_agent(agent_id, position)

    def remove_agent(self, agent_id: str) -> None:
        """Remove agent entries from cached indices."""

        previous = self._positions_by_agent.pop(agent_id, None)
        if previous is None:
            return
        bucket = self._agents_by_position.get(previous)
        if bucket is None:
            return
        try:
            bucket.remove(agent_id)
        except ValueError:
            return
        if not bucket:
            self._agents_by_position.pop(previous, None)

    def position_of(self, agent_id: str) -> tuple[int, int] | None:
        """Return the cached grid position for ``agent_id`` if known."""

        return self._positions_by_agent.get(agent_id)

    def agents_at(self, position: tuple[int, int]) -> tuple[str, ...]:
        """Return agent identifiers occupying ``position``."""

        return tuple(self._agents_by_position.get(position, ()))

    # Reservation bookkeeping -------------------------------------------
    def set_reservation(self, position: tuple[int, int] | None, active: bool) -> None:
        """Toggle reservation state for the tile at ``position``."""

        if position is None:
            return
        if active:
            self._reservation_tiles.add(position)
        else:
            self._reservation_tiles.discard(position)

    def reservation_tiles(self) -> frozenset[tuple[int, int]]:
        """Return a frozen copy of tiles reserved by active affordances."""

        return frozenset(self._reservation_tiles)


__all__ = ["WorldSpatialIndex"]

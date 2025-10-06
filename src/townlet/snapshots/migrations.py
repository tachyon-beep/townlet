"""Snapshot migration registry and helpers."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from townlet.config import SimulationConfig
    from townlet.snapshots.state import SnapshotState

MigrationHandler = Callable[
    ["SnapshotState", "SimulationConfig"], "SnapshotState | None"
]


class MigrationNotFoundError(Exception):
    """Raised when no migration path exists between config identifiers."""


class MigrationExecutionError(Exception):
    """Raised when a migration handler fails or leaves the snapshot unchanged."""


@dataclass(frozen=True)
class MigrationEdge:
    source: str
    target: str
    handler: MigrationHandler

    @property
    def identifier(self) -> str:
        return getattr(
            self.handler, "__qualname__", getattr(self.handler, "__name__", "migration")
        )


class SnapshotMigrationRegistry:
    """Maintains registered snapshot migrations keyed by config identifiers."""

    def __init__(self) -> None:
        self._graph: dict[str, dict[str, MigrationEdge]] = {}

    def register(
        self, from_config: str, to_config: str, handler: MigrationHandler
    ) -> None:
        source = str(from_config)
        target = str(to_config)
        edge = MigrationEdge(source=source, target=target, handler=handler)
        self._graph.setdefault(source, {})[target] = edge

    def clear(self) -> None:
        self._graph.clear()

    def _neighbours(self, node: str) -> Iterable[MigrationEdge]:
        return self._graph.get(node, {}).values()

    def find_path(self, start: str, goal: str) -> list[MigrationEdge]:
        start = str(start)
        goal = str(goal)
        if start == goal:
            return []
        visited = {start}
        queue: deque[tuple[str, list[MigrationEdge]]] = deque([(start, [])])
        while queue:
            node, path = queue.popleft()
            for edge in self._neighbours(node):
                if edge.target in visited:
                    continue
                next_path = [*path, edge]
                if edge.target == goal:
                    return next_path
                visited.add(edge.target)
                queue.append((edge.target, next_path))
        raise MigrationNotFoundError(
            f"No snapshot migration path from {start} to {goal}"
        )

    def apply_path(
        self,
        path: list[MigrationEdge],
        state: SnapshotState,
        config: SimulationConfig,
    ) -> tuple[SnapshotState, list[str]]:
        applied: list[str] = []
        current = state
        for edge in path:
            result = edge.handler(current, config)
            if result is None:
                # handler mutated in-place
                result = current
            if (
                result.config_id == current.config_id
                and edge.target != result.config_id
            ):
                raise MigrationExecutionError(
                    f"Migration {edge.identifier} did not update config_id from {current.config_id}"
                )
            current = result
            applied.append(f"{edge.source}->{edge.target}:{edge.identifier}")
        return current, applied


registry = SnapshotMigrationRegistry()
migration_registry = registry


def register_migration(
    from_config: str, to_config: str, handler: MigrationHandler
) -> None:
    """Register a snapshot migration handler."""

    registry.register(from_config, to_config, handler)


def clear_registry() -> None:
    """Reset registry (intended for test teardown)."""

    registry.clear()

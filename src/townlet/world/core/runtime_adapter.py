"""Read-only runtime adapter exposed to policy and telemetry layers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING

from townlet.world.observations.interfaces import (
    EmbeddingAllocatorProtocol,
    WorldRuntimeAdapterProtocol,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    from townlet.config import SimulationConfig
    from townlet.observations.embedding import EmbeddingAllocator
    from townlet.world.agents.snapshot import AgentSnapshot
    from townlet.world.core.context import WorldContext
    from townlet.world.grid import WorldState
    from townlet.world.queue.manager import QueueManager


class _EmbeddingAllocatorAdapter(EmbeddingAllocatorProtocol):
    """Lightweight view over the embedding allocator."""

    __slots__ = ("_allocator",)

    def __init__(self, allocator: EmbeddingAllocator) -> None:
        self._allocator = allocator

    def allocate(self, agent_id: str, tick: int) -> int:
        return self._allocator.allocate(agent_id, tick)

    def release(self, agent_id: str, tick: int) -> None:
        self._allocator.release(agent_id, tick)

    def has_assignment(self, agent_id: str) -> bool:  # pragma: no cover - trivial
        return self._allocator.has_assignment(agent_id)

    def metrics(self) -> Mapping[str, float]:
        return self._allocator.metrics()


class WorldRuntimeAdapter(WorldRuntimeAdapterProtocol):
    """Facade providing read-only access to world state helpers."""

    __slots__ = ("_allocator_adapter", "_world")

    def __init__(self, world: WorldState) -> None:
        self._world = world
        allocator = getattr(world, "embedding_allocator", None)
        if allocator is None:
            raise TypeError("WorldRuntimeAdapter requires world with embedding allocator")
        self._allocator_adapter = _EmbeddingAllocatorAdapter(allocator)

    @property
    def tick(self) -> int:
        return self._world.tick

    @tick.setter
    def tick(self, value: int) -> None:
        raise AttributeError("WorldRuntimeAdapter.tick is read-only")

    @property
    def config(self) -> SimulationConfig:  # pragma: no cover - simple accessor
        return self._world.config

    @config.setter
    def config(self, value: object) -> None:
        raise AttributeError("WorldRuntimeAdapter.config is read-only")

    def agent_snapshots_view(self) -> Mapping[str, AgentSnapshot]:
        return self._world.agent_snapshots_view()

    def agent_position(self, agent_id: str) -> tuple[int, int] | None:
        return self._world.agent_position(agent_id)

    def agents_at_tile(self, position: tuple[int, int]) -> tuple[str, ...]:
        return self._world.agents_at_tile(position)

    def consume_ctx_reset_requests(self) -> set[str]:
        return self._world.consume_ctx_reset_requests()

    @property
    def embedding_allocator(self) -> EmbeddingAllocatorProtocol:
        return self._allocator_adapter

    def objects_by_position_view(self) -> Mapping[tuple[int, int], tuple[str, ...]]:
        return self._world.objects_by_position_view()

    def reservation_tiles(self) -> Iterable[tuple[int, int]]:  # pragma: no cover - thin proxy
        return self._world.reservation_tiles()

    @property
    def active_reservations(self) -> Mapping[str, str | None]:
        return self._world.active_reservations_view()

    @property
    def queue_manager(self) -> QueueManager:
        return self._world.queue_manager

    def relationships_snapshot(self) -> Mapping[str, Mapping[str, Mapping[str, float]]]:
        snapshot = self._world.relationships_snapshot()
        return {
            str(owner): {
                str(other): {str(metric): float(value) for metric, value in metrics.items()}
                for other, metrics in relations.items()
            }
            for owner, relations in snapshot.items()
        }

    def relationship_metrics_snapshot(self) -> Mapping[str, object]:
        getter = getattr(self._world, "relationship_metrics_snapshot", None)
        if callable(getter):
            metrics = getter()
            if isinstance(metrics, Mapping):
                return {str(key): value for key, value in metrics.items()}
        return {}

    def rivalry_top(self, agent_id: str, limit: int) -> Iterable[tuple[str, float]]:
        return tuple(self._world.rivalry_top(agent_id, limit))

    def rivalry_snapshot(self) -> Mapping[str, Mapping[str, float]]:
        snapshot_getter = getattr(self._world, "rivalry_snapshot", None)
        if callable(snapshot_getter):
            snapshot = snapshot_getter()
            if isinstance(snapshot, Mapping):
                return {
                    str(owner): {str(other): float(value) for other, value in relations.items()}
                    for owner, relations in snapshot.items()
                }
        return {}

    def consume_rivalry_events(self) -> Iterable[Mapping[str, object]]:
        consumer = getattr(self._world, "consume_rivalry_events", None)
        if callable(consumer):
            events = consumer() or []
            if isinstance(events, Iterable):
                cleaned: list[Mapping[str, object]] = []
                for event in events:
                    if isinstance(event, Mapping):
                        cleaned.append({str(key): value for key, value in event.items()})
                return cleaned
        return []

    def _employment_context_wages(self, agent_id: str) -> float:
        return self._world.employment_service.context_wages(agent_id)

    def _employment_context_punctuality(self, agent_id: str) -> float:
        return self._world.employment_service.context_punctuality(agent_id)

    def running_affordances_snapshot(self) -> Mapping[str, object]:
        snapshot_getter = getattr(self._world, "running_affordances_snapshot", None)
        if callable(snapshot_getter):
            snapshot = snapshot_getter() or {}
            if isinstance(snapshot, Mapping):
                return {str(key): value for key, value in snapshot.items()}
        return {}

    def objects_snapshot(self) -> Mapping[str, Mapping[str, object]]:
        """Return an immutable snapshot of interactive object metadata."""

        snapshot: dict[str, dict[str, object]] = {}
        for object_id, obj in self._world.objects.items():
            raw_position = getattr(obj, "position", None)
            position = None
            if raw_position is not None and len(raw_position) >= 2:
                position = (int(raw_position[0]), int(raw_position[1]))
            stock_payload = getattr(obj, "stock", {})
            stock = dict(stock_payload) if isinstance(stock_payload, Mapping) else {}
            snapshot[object_id] = {
                "object_type": getattr(obj, "object_type", ""),
                "position": position,
                "occupied_by": getattr(obj, "occupied_by", None),
                "stock": stock,
            }
        return MappingProxyType(snapshot)


def ensure_world_adapter(
    world: WorldRuntimeAdapterProtocol | WorldState | WorldContext,
) -> WorldRuntimeAdapterProtocol:
    """Return a runtime adapter, wrapping ``world`` when necessary."""

    if isinstance(world, WorldRuntimeAdapterProtocol):
        return world
    from townlet.world.grid import WorldState  # local import to avoid cycles
    try:
        from townlet.world.core.context import WorldContext
    except ImportError:  # pragma: no cover - fallback during partial initialisation
        world_context_cls = None
    else:
        world_context_cls = WorldContext

    if isinstance(world, WorldState):
        return WorldRuntimeAdapter(world)
    if world_context_cls is not None and isinstance(world, world_context_cls):
        return WorldRuntimeAdapter(world.state)
    raise TypeError(
        "world must be a WorldRuntimeAdapterProtocol or WorldState; got" f" {type(world)!r}"
    )


__all__ = ["WorldRuntimeAdapter", "ensure_world_adapter"]

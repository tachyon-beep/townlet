"""Read-only runtime adapter exposed to policy and telemetry layers."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, Iterable, Mapping, MutableMapping

from townlet.world.observations.interfaces import (
    EmbeddingAllocatorProtocol,
    WorldRuntimeAdapterProtocol,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    from townlet.config import SimulationConfig
    from townlet.observations.embedding import EmbeddingAllocator
    from townlet.world.agents.snapshot import AgentSnapshot
    from townlet.world.grid import WorldState
    from townlet.world.queue.manager import QueueManager


class _EmbeddingAllocatorAdapter(EmbeddingAllocatorProtocol):
    """Lightweight view over the embedding allocator."""

    __slots__ = ("_allocator",)

    def __init__(self, allocator: "EmbeddingAllocator") -> None:
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

    __slots__ = ("_world", "_allocator_adapter")

    def __init__(self, world: "WorldState") -> None:
        self._world = world
        self._allocator_adapter = _EmbeddingAllocatorAdapter(world.embedding_allocator)

    @property
    def tick(self) -> int:
        return self._world.tick

    @property
    def config(self) -> "SimulationConfig":  # pragma: no cover - simple accessor
        return self._world.config

    def agent_snapshots_view(self) -> Mapping[str, "AgentSnapshot"]:
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

    @property
    def objects(self) -> Mapping[str, object]:
        return MappingProxyType(self._world.objects)

    def objects_by_position_view(self) -> Mapping[tuple[int, int], tuple[str, ...]]:
        return self._world.objects_by_position_view()

    def reservation_tiles(self) -> Iterable[tuple[int, int]]:  # pragma: no cover - thin proxy
        return self._world.reservation_tiles()

    @property
    def active_reservations(self) -> Mapping[str, str | None]:
        return self._world.active_reservations_view()

    @property
    def queue_manager(self) -> "QueueManager":
        return self._world.queue_manager

    def relationships_snapshot(self) -> Mapping[str, Mapping[str, Mapping[str, float]]]:
        return self._world.relationships_snapshot()

    def rivalry_top(self, agent_id: str, limit: int) -> Iterable[tuple[str, float]]:
        return tuple(self._world.rivalry_top(agent_id, limit))

    def _employment_context_wages(self, agent_id: str) -> float:
        return self._world._employment_context_wages(agent_id)

    def _employment_context_punctuality(self, agent_id: str) -> float:
        return self._world._employment_context_punctuality(agent_id)


def ensure_world_adapter(
    world: WorldRuntimeAdapterProtocol | "WorldState",
) -> WorldRuntimeAdapterProtocol:
    """Return a runtime adapter, wrapping ``world`` when necessary."""

    if isinstance(world, WorldRuntimeAdapterProtocol):
        return world
    from townlet.world.grid import WorldState  # local import to avoid cycles

    if isinstance(world, WorldState):
        return WorldRuntimeAdapter(world)
    raise TypeError(
        "world must be a WorldRuntimeAdapterProtocol or WorldState; got" f" {type(world)!r}"
    )


__all__ = ["WorldRuntimeAdapter", "ensure_world_adapter"]

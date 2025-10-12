"""Protocols sketching the observation service and runtime adapter surfaces.

These abstractions back Phase 4 of the world modularisation work. They mirror
existing agent/employment protocols so downstream consumers (policy, telemetry,
training) can depend on stable contracts while the underlying implementation
migrates out of ``WorldState``.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Protocol, runtime_checkable

from townlet.world.agents.snapshot import AgentSnapshot
from townlet.world.queue.manager import QueueManager


@runtime_checkable
class EmbeddingAllocatorProtocol(Protocol):
    """Subset of the embedding allocator API observation builders depend on."""

    def allocate(self, agent_id: str, tick: int) -> int:
        ...

    def release(self, agent_id: str, tick: int) -> None:
        ...

    def has_assignment(self, agent_id: str) -> bool:
        ...

    def metrics(self) -> Mapping[str, float]:
        ...


@runtime_checkable
class WorldRuntimeAdapterProtocol(Protocol):
    """Read-only façade exposed to policy/telemetry layers during Phase 4."""

    tick: int
    config: object

    def agent_snapshots_view(self) -> Mapping[str, AgentSnapshot]:
        ...

    def agent_position(self, agent_id: str) -> tuple[int, int] | None:
        ...

    def agents_at_tile(self, position: tuple[int, int]) -> tuple[str, ...]:
        ...

    def consume_ctx_reset_requests(self) -> set[str]:
        ...

    @property
    def embedding_allocator(self) -> EmbeddingAllocatorProtocol:
        ...

    def objects_by_position_view(self) -> Mapping[tuple[int, int], tuple[str, ...]]:
        ...

    def reservation_tiles(self) -> Iterable[tuple[int, int]]:
        ...

    @property
    def active_reservations(self) -> Mapping[str, str | None]:
        ...

    @property
    def queue_manager(self) -> QueueManager:
        ...

    def relationships_snapshot(self) -> Mapping[str, Mapping[str, Mapping[str, float]]]:
        ...

    def rivalry_top(self, agent_id: str, limit: int) -> Iterable[tuple[str, float]]:
        ...

    def rivalry_snapshot(self) -> Mapping[str, Mapping[str, float]]:
        ...

    def consume_rivalry_events(self) -> Iterable[Mapping[str, object]]:
        ...

    def _employment_context_wages(self, agent_id: str) -> float:
        ...

    def _employment_context_punctuality(self, agent_id: str) -> float:
        ...

    def running_affordances_snapshot(self) -> Mapping[str, object]:
        ...

    def objects_snapshot(self) -> Mapping[str, Mapping[str, Any]]:
        ...

    def basket_cost(self, agent_id: str) -> float:
        ...


@runtime_checkable
class ObservationServiceProtocol(Protocol):
    """High-level contract for building per-agent observation payloads."""

    @property
    def variant(self) -> object:
        ...

    @property
    def feature_names(self) -> tuple[str, ...]:
        ...

    @property
    def social_vector_length(self) -> int:
        ...

    def build_batch(
        self,
        world: WorldRuntimeAdapterProtocol,
        terminated: Mapping[str, bool],
    ) -> Mapping[str, Mapping[str, Any]]:
        ...

    def build_single(
        self,
        world: WorldRuntimeAdapterProtocol,
        agent_id: str,
        *,
        slot: int | None = None,
    ) -> Mapping[str, Any]:
        ...


__all__ = [
    "EmbeddingAllocatorProtocol",
    "ObservationServiceProtocol",
    "WorldRuntimeAdapterProtocol",
]

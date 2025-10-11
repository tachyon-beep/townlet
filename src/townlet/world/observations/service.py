"""Observation service wrapper owned by the world context."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from townlet.observations import ObservationBuilder
from townlet.world.observations.interfaces import (
    ObservationServiceProtocol,
    WorldRuntimeAdapterProtocol,
)


class ObservationBuilderService(ObservationServiceProtocol):
    """Thin wrapper that exposes ``ObservationBuilder`` via the service protocol."""

    def __init__(self, *, config: Any) -> None:
        self._builder = ObservationBuilder(config=config)

    @property
    def variant(self) -> object:
        return self._builder.variant

    @property
    def feature_names(self) -> tuple[str, ...]:
        names = getattr(self._builder, "_feature_names", ())
        return tuple(names)

    @property
    def social_vector_length(self) -> int:
        return int(getattr(self._builder, "_social_vector_length", 0))

    def build_batch(
        self,
        world: WorldRuntimeAdapterProtocol | object,
        terminated: Mapping[str, bool],
    ) -> Mapping[str, Mapping[str, Any]]:
        return self._builder.build_batch(world, terminated)

    def build_single(
        self,
        world: WorldRuntimeAdapterProtocol | object,
        agent_id: str,
        *,
        slot: int | None = None,
    ) -> Mapping[str, Any]:
        # Fallback implementation: build full batch and return the requested entry.
        # A more efficient single-agent path can be added when required.
        batch = self._builder.build_batch(world, {})
        if agent_id not in batch:
            raise KeyError(f"agent '{agent_id}' not present in observation batch")
        entry = batch[agent_id]
        if slot is None:
            return entry
        payload = dict(entry)
        metadata = dict(payload.get("metadata", {}))
        metadata["embedding_slot"] = slot
        payload["metadata"] = metadata
        return payload


__all__ = ["ObservationBuilderService"]

"""Spatial utilities (skeleton)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, Tuple


@dataclass
class SpatialIndex:
    """Placeholder spatial index storing agent/object locations."""

    agents_by_position: dict[Tuple[int, int], list[str]] = field(default_factory=dict)

    def neighbours(self, position: Tuple[int, int], radius: int = 1) -> Iterable[Tuple[int, int]]:
        raise NotImplementedError("SpatialIndex.neighbours pending WP2 implementation")


def rebuild_index(
    index: SpatialIndex,
    agents: Mapping[str, Tuple[int, int]],
    objects: Mapping[str, Tuple[int, int]],
) -> SpatialIndex:
    """Placeholder rebuild helper to be implemented during WP2."""

    raise NotImplementedError("rebuild_index pending WP2 implementation")


__all__ = ["SpatialIndex", "rebuild_index"]

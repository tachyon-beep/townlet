"""World state container (skeleton)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorldState:
    """Minimal placeholder for modular world state used in WP2.

    Fields will be expanded as the modularisation progresses. The class lives in
    its own module so other components can type-check against it without relying
    on the legacy `world.grid.WorldState`.
    """

    tick: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


__all__ = ["WorldState"]

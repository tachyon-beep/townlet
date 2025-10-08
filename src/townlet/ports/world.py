"""Protocol defining the world runtime boundary for the simulation loop."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Protocol


class WorldRuntime(Protocol):
    """Minimal contract for advancing and querying the world state."""

    def reset(self, seed: int | None = None) -> None:
        """Reset the world to its initial state (optional seed for determinism)."""

    def tick(self) -> None:
        """Advance the world by one logical tick."""

    def agents(self) -> Iterable[str]:
        """Return the iterable of active agent identifiers."""

    def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]:
        """Return observation payloads for the specified agents (all agents by default)."""

    def apply_actions(self, actions: Mapping[str, Any]) -> None:
        """Apply a mapping of agent actions prior to advancing the tick."""

    def snapshot(self) -> Mapping[str, Any]:
        """Expose a serialisable snapshot of the current world state."""


__all__ = ["WorldRuntime"]

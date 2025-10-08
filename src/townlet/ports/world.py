"""Protocol definitions for world runtimes."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Protocol


class WorldRuntime(Protocol):
    """Port describing the behaviours required from a world runtime."""

    def reset(self, seed: int | None = None) -> None:
        """Reset the world to its initial state."""

    def tick(self) -> None:
        """Advance the world by a single tick."""

    def agents(self) -> Iterable[str]:
        """Return the identifiers of agents currently active in the world."""

    def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]:
        """Return observations for the requested agents."""

    def apply_actions(self, actions: Mapping[str, Any]) -> None:
        """Apply the supplied actions on the next tick."""

    def snapshot(self) -> Mapping[str, Any]:
        """Return a snapshot of the world suitable for telemetry."""

"""Protocol describing the world runtime surface consumed by the loop."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Protocol


class WorldRuntime(Protocol):
    """Minimal interface for advancing and inspecting the world state."""

    def reset(self, seed: int | None = None) -> None:
        """Reset the world to its initial state using ``seed`` when provided."""

    def tick(self) -> None:
        """Advance the world simulation by one tick."""

    def agents(self) -> Iterable[str]:
        """Return an iterable of agent identifiers present in the world."""

    def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]:
        """Return observations for ``agent_ids`` or all agents when ``None``."""

    def apply_actions(self, actions: Mapping[str, Any]) -> None:
        """Apply the supplied ``actions`` to the world state."""

    def snapshot(self) -> Mapping[str, Any]:
        """Expose a serialisable snapshot of the world suitable for telemetry."""

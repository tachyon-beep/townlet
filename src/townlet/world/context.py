"""World context façade (skeleton)."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .state import WorldState


class WorldContext:
    """Placeholder implementation of the `WorldRuntime` port.

    The full implementation will arrive later in WP2; for now the methods raise
    `NotImplementedError` so importers can type-check against the eventual
    interface without changing behaviour.
    """

    def __init__(self, state: WorldState | None = None) -> None:
        self._state = state or WorldState()

    def reset(self, seed: int | None = None) -> None:
        raise NotImplementedError("WorldContext.reset pending WP2 implementation")

    def tick(self) -> None:
        raise NotImplementedError("WorldContext.tick pending WP2 implementation")

    def agents(self) -> Iterable[str]:
        raise NotImplementedError("WorldContext.agents pending WP2 implementation")

    def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]:
        raise NotImplementedError("WorldContext.observe pending WP2 implementation")

    def apply_actions(self, actions: Mapping[str, Any]) -> None:
        raise NotImplementedError("WorldContext.apply_actions pending WP2 implementation")

    def snapshot(self) -> Mapping[str, Any]:
        raise NotImplementedError("WorldContext.snapshot pending WP2 implementation")


__all__ = ["WorldContext"]

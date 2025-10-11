"""Protocol defining the world runtime boundary for the simulation loop."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any, Callable, Protocol

if TYPE_CHECKING:  # pragma: no cover - typing only
    from townlet.console.command import ConsoleCommandEnvelope
    from townlet.snapshots.state import SnapshotState
    from townlet.world.grid import WorldState
    from townlet.world.runtime import RuntimeStepResult


class WorldRuntime(Protocol):
    """Minimal contract for advancing and querying the world state."""

    def reset(self, seed: int | None = None) -> None:
        """Reset the world to its initial state (optional seed for determinism)."""

    def tick(
        self,
        *,
        tick: int,
        console_operations: Iterable["ConsoleCommandEnvelope"] | None = None,
        action_provider: Callable[["WorldState", int], Mapping[str, Any]] | None = None,
        policy_actions: Mapping[str, Any] | None = None,
    ) -> "RuntimeStepResult":
        """Advance the world by one logical tick and return tick artefacts."""

    def agents(self) -> Iterable[str]:
        """Return the iterable of active agent identifiers."""

    def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]:
        """Return observation payloads for the specified agents (all agents by default)."""

    def apply_actions(self, actions: Mapping[str, Any]) -> None:
        """Apply a mapping of agent actions prior to advancing the tick."""

    def snapshot(
        self,
        *,
        config: Any | None = None,
        telemetry: "TelemetrySinkProtocol" | None = None,
        stability: Any | None = None,
        promotion: Any | None = None,
        rng_streams: Mapping[str, Any] | None = None,
        identity: Mapping[str, Any] | None = None,
    ) -> "SnapshotState":
        """Expose a serialisable snapshot of the current world state."""

    def queue_console(self, operations: Iterable["ConsoleCommandEnvelope"]) -> None:
        """Buffer console operations to be executed on the next tick."""


__all__ = ["WorldRuntime"]

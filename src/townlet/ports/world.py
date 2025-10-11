"""Protocol defining the world runtime boundary for the simulation loop."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any, Callable, Protocol, runtime_checkable

if TYPE_CHECKING:  # pragma: no cover - typing only
    from townlet.console.command import ConsoleCommandEnvelope
    from townlet.core.interfaces import TelemetrySinkProtocol
    from townlet.snapshots.state import SnapshotState
    from townlet.world.grid import WorldState
    from townlet.world.runtime import RuntimeStepResult


@runtime_checkable
class WorldRuntime(Protocol):
    """Minimal contract for advancing the world runtime."""

    def bind_world(self, world: "WorldState") -> None:
        """Rebind the runtime to a freshly constructed world instance."""

    def agents(self) -> Iterable[str]:
        """Return the list of agent identifiers."""

    def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]:
        """Return per-agent observation payloads."""

    def apply_actions(self, actions: Mapping[str, Any]) -> None:
        """Stage policy actions that should execute on the next tick."""

    def tick(
        self,
        *,
        tick: int,
        console_operations: Iterable["ConsoleCommandEnvelope"] | None = None,
        action_provider: Callable[["WorldState", int], Mapping[str, Any]] | None = None,
        policy_actions: Mapping[str, Any] | None = None,
    ) -> "RuntimeStepResult":
        """Advance the world by one tick and return observable artefacts."""

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
        """Return a diagnostic snapshot of the underlying world state."""


__all__ = ["WorldRuntime"]

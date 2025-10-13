"""Protocol defining the world runtime boundary for the simulation loop.

This module defines the WorldRuntime port protocol, which enforces typed DTO boundaries
between the simulation loop and world implementations. All world runtimes must implement
this protocol to ensure consistent data exchange.

The protocol uses DTOs from townlet.dto.observations for all observation-related data,
ensuring type safety and validation across the boundary.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from townlet.dto.observations import ObservationEnvelope

if TYPE_CHECKING:  # pragma: no cover - typing only
    from townlet.console.command import ConsoleCommandEnvelope
    from townlet.core.interfaces import TelemetrySinkProtocol
    from townlet.dto.world import SimulationSnapshot
    from townlet.world.grid import WorldState
    from townlet.world.runtime import RuntimeStepResult


@runtime_checkable
class WorldRuntime(Protocol):
    """Minimal contract for advancing the world runtime.

    This protocol defines the interface that all world runtime implementations must satisfy.
    It enforces DTO-based boundaries for observations, ensuring type safety and validation.

    The canonical implementation is `townlet.world.runtime.WorldRuntime`, which provides
    a stateful façade coordinating world tick sequencing.

    Note: This is a structural protocol (@runtime_checkable). Concrete implementations
    are NOT required to inherit from this protocol; they only need to provide compatible
    methods with matching signatures.

    Naming Convention:
        The concrete implementation class shares the name "WorldRuntime" with this protocol.
        This is intentional and works correctly because:
        1. Structural typing allows this pattern (PEP 544)
        2. Different namespaces prevent confusion (ports.world vs world.runtime)
        3. The concrete class naturally fulfills the protocol contract
        4. The adapter pattern cleanly wraps the concrete implementation

    DTO Enforcement:
        - observe() returns ObservationEnvelope (townlet.dto.observations)
        - All observations use typed DTOs rather than raw dicts

    See Also:
        - ADR-001: Port and Factory Registry
        - ADR-003: DTO Boundary specification
    """

    def bind_world(self, world: WorldState) -> None:
        """Rebind the runtime to a freshly constructed world instance."""

    def agents(self) -> Iterable[str]:
        """Return the list of agent identifiers currently active in the world."""

    def observe(self, agent_ids: Iterable[str] | None = None) -> ObservationEnvelope:
        """Return the DTO observation envelope for the requested agents.

        Args:
            agent_ids: Optional subset of agent IDs to observe. If None, observes all agents.

        Returns:
            ObservationEnvelope: Typed DTO containing agent observations and global context.
        """

    def apply_actions(self, actions: Mapping[str, Any]) -> None:
        """Stage policy actions that should execute on the next tick."""

    def tick(
        self,
        *,
        tick: int,
        console_operations: Iterable[ConsoleCommandEnvelope] | None = None,
        action_provider: Callable[[WorldState, int], Mapping[str, Any]] | None = None,
        policy_actions: Mapping[str, Any] | None = None,
    ) -> RuntimeStepResult:
        """Advance the world by one tick and return observable artefacts."""

    def snapshot(
        self,
        *,
        config: Any | None = None,
        telemetry: TelemetrySinkProtocol | None = None,
        stability: Any | None = None,
        promotion: Any | None = None,
        rng_streams: Mapping[str, Any] | None = None,
        identity: Mapping[str, Any] | None = None,
    ) -> SimulationSnapshot:
        """Return a diagnostic snapshot of the underlying world state."""


__all__ = ["WorldRuntime"]

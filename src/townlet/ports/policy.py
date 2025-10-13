"""Protocol describing the policy backend boundary.

This module defines the PolicyBackend port protocol, which enforces typed DTO boundaries
between the simulation loop and policy implementations. All policy backends must implement
this protocol to ensure consistent data exchange.

The protocol uses DTOs from townlet.dto.observations for all observation-related data,
ensuring type safety and validation across the boundary.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:  # pragma: no cover
    from townlet.dto.observations import ObservationEnvelope


class PolicyBackend(Protocol):
    """Decide actions for agents based on observations.

    This protocol defines the interface that all policy backend implementations must satisfy.
    It enforces DTO-based boundaries for observations, ensuring type safety and validation.

    Implementations include:
        - ScriptedPolicyAdapter (rule-based behavior)
        - PolicyRuntime (RL/learned policies)
        - DummyPolicyBackend (testing stub)

    DTO Enforcement:
        - decide() accepts ObservationEnvelope (townlet.dto.observations)
        - All observations use typed DTOs rather than raw dicts

    See Also:
        - ADR-001: Port and Factory Registry
        - ADR-003: DTO Boundary specification
    """

    def on_episode_start(self, agent_ids: Iterable[str]) -> None:
        """Prepare the backend for a new episode, receiving participating agent IDs."""

    def supports_observation_envelope(self) -> bool:
        """Return True when the backend consumes DTO observation envelopes.

        This capability check allows the simulation loop to verify DTO support before
        passing observation envelopes. All modern policy backends should return True.
        """

    def decide(
        self,
        *,
        tick: int,
        envelope: ObservationEnvelope,
    ) -> Mapping[str, Any]:
        """Return an action mapping for the provided DTO envelope.

        Args:
            tick: Current simulation tick number.
            envelope: ObservationEnvelope DTO containing agent observations and global context.

        Returns:
            Mapping of agent_id -> action dict for all agents that should act this tick.
        """

    def on_episode_end(self) -> None:
        """Clean up backend state at the end of an episode."""


__all__ = ["PolicyBackend"]

"""Protocol describing the policy backend boundary."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:  # pragma: no cover
    from townlet.world.dto.observation import ObservationEnvelope


class PolicyBackend(Protocol):
    """Decide actions for agents based on observations."""

    def on_episode_start(self, agent_ids: Iterable[str]) -> None:
        """Prepare the backend for a new episode, receiving participating agent IDs."""

    def supports_observation_envelope(self) -> bool:
        """Return True when the backend consumes DTO observation envelopes."""

    def decide(
        self,
        *,
        tick: int,
        envelope: ObservationEnvelope,
    ) -> Mapping[str, Any]:
        """Return an action mapping for the provided DTO envelope."""

    def on_episode_end(self) -> None:
        """Clean up backend state at the end of an episode."""


__all__ = ["PolicyBackend"]

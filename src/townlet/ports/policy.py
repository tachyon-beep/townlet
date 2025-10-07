"""Protocol describing the policy backend consumed by the simulation loop."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Protocol


class PolicyBackend(Protocol):
    """Stateless policy surface exposed to the simulation loop."""

    def on_episode_start(self, agent_ids: Iterable[str]) -> None:
        """Notify the policy that a new episode has started."""

    def decide(self, observations: Mapping[str, Any]) -> Mapping[str, Any]:
        """Return an action mapping given the latest ``observations``."""

    def on_episode_end(self) -> None:
        """Notify the policy that the episode has completed."""

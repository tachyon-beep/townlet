"""Protocol describing the policy backend boundary."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Protocol


class PolicyBackend(Protocol):
    """Decide actions for agents based on observations."""

    def on_episode_start(self, agent_ids: Iterable[str]) -> None:
        """Prepare the backend for a new episode, receiving participating agent IDs."""

    def decide(self, observations: Mapping[str, Any]) -> Mapping[str, Any]:
        """Return an action mapping for the provided observations."""

    def on_episode_end(self) -> None:
        """Clean up backend state at the end of an episode."""


__all__ = ["PolicyBackend"]

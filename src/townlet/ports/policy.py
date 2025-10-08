"""Policy backend port."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Protocol


class PolicyBackend(Protocol):
    """Port describing the contract for policy backends."""

    def on_episode_start(self, agent_ids: Iterable[str]) -> None:
        """Notify the policy that a new episode is about to start."""

    def decide(self, observations: Mapping[str, Any]) -> Mapping[str, Any]:
        """Return actions for the provided observations."""

    def on_episode_end(self) -> None:
        """Notify the policy that the episode has concluded."""

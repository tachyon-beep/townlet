from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from townlet.dto.observations import ObservationEnvelope


class DummyPolicyBackend:
    """Trivial policy backend that always returns no-op actions."""

    def __init__(self) -> None:
        self._last_envelope: ObservationEnvelope | None = None
        self._active_agents: tuple[str, ...] = ()

    def on_episode_start(self, agent_ids: Iterable[str]) -> None:
        self._active_agents = tuple(agent_ids)

    def supports_observation_envelope(self) -> bool:
        return True

    def decide(
        self,
        *,
        tick: int,
        envelope: ObservationEnvelope,
    ) -> Mapping[str, Any]:
        self._last_envelope = envelope
        return {agent_id: {} for agent_id in self._active_agents}

    def on_episode_end(self) -> None:
        self._last_envelope = None
        self._active_agents = ()

    # Diagnostic helpers -------------------------------------------------
    @property
    def last_envelope(self) -> ObservationEnvelope | None:
        return self._last_envelope

    @property
    def active_agents(self) -> tuple[str, ...]:
        return self._active_agents

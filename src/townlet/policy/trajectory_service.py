"""Trajectory and transition management helpers for PolicyRuntime."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from townlet.world.dto.observation import AgentObservationDTO, ObservationEnvelope


@dataclass
class TrajectoryService:
    """Tracks per-agent transitions and builds trajectory frames."""

    _transitions: dict[str, dict[str, Any]] = field(default_factory=dict)
    _trajectory: list[dict[str, Any]] = field(default_factory=list)
    _current_tick: int = 0

    def begin_tick(self, tick: int) -> None:
        """Record the simulation tick associated with subsequent transitions."""

        self._current_tick = tick

    def transition_entry(self, agent_id: str) -> dict[str, Any]:
        """Return (and create if needed) the transition entry for ``agent_id``."""

        return self._transitions.setdefault(agent_id, {})

    def record_action(self, agent_id: str, action_payload: dict[str, Any], action_id: int) -> dict[str, Any]:
        """Attach the selected action to ``agent_id``'s transition entry."""

        entry = self.transition_entry(agent_id)
        entry["action"] = action_payload
        entry["action_id"] = action_id
        return entry

    def append_reward(self, agent_id: str, reward: float, done: bool) -> None:
        """Append reward and termination signals to the current transition."""

        entry = self.transition_entry(agent_id)
        entry.setdefault("rewards", []).append(reward)
        entry.setdefault("dones", []).append(bool(done))

    def flush_transitions(
        self,
        observations: Mapping[str, Mapping[str, Any]] | ObservationEnvelope,
        *,
        envelope: ObservationEnvelope | None = None,
    ) -> list[dict[str, Any]]:
        """Combine transitions with observations and clear the per-agent cache."""

        frames: list[dict[str, Any]]
        if isinstance(observations, ObservationEnvelope):
            envelope = observations
            frames = self._frames_from_envelope(observations)
        elif envelope is not None:
            frames = self._frames_from_envelope(envelope, fallback=observations)
        else:
            frames = self._frames_from_mapping(observations)

        self._transitions.clear()
        return frames

    def extend_trajectory(self, frames: list[dict[str, Any]]) -> None:
        """Extend the stored trajectory list with freshly generated frames."""

        self._trajectory.extend(frames)

    def collect_trajectory(self, clear: bool = True) -> list[dict[str, Any]]:
        """Return the accumulated trajectory and optionally clear the buffer."""

        result = list(self._trajectory)
        if clear:
            self._trajectory.clear()
        return result

    def reset_state(self) -> None:
        """Clear cached transitions and trajectory information."""

        self._transitions.clear()
        self._trajectory.clear()

    @property
    def transitions(self) -> dict[str, dict[str, Any]]:
        """Return the raw transition buffer keyed by agent identifier."""

        return self._transitions

    @property
    def trajectory(self) -> list[dict[str, Any]]:
        """Return the accumulated trajectory frames without clearing them."""

        return self._trajectory

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _frames_from_mapping(
        self,
        observations: Mapping[str, Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        frames: list[dict[str, Any]] = []
        for agent_id, payload in observations.items():
            entry = self._transitions.get(agent_id, {})
            frame = {
                "tick": self._current_tick,
                "agent_id": agent_id,
                "map": payload.get("map"),
                "features": payload.get("features"),
                "metadata": payload.get("metadata"),
                "action": entry.get("action"),
                "action_id": entry.get("action_id"),
                "rewards": entry.get("rewards", []),
                "dones": entry.get("dones", []),
            }
            frames.append(frame)
        return frames

    def _frames_from_envelope(
        self,
        envelope: ObservationEnvelope,
        *,
        fallback: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        frames: list[dict[str, Any]] = []
        agent_lookup = {agent.agent_id: agent for agent in envelope.agents}
        if fallback:
            for agent_id, payload in fallback.items():
                if agent_id not in agent_lookup:
                    # Allow transitional callers to include legacy payloads for agents
                    # that were not present in the DTO (should not happen after Stage 3C).
                    agent_lookup[agent_id] = self._build_agent_from_mapping(
                        agent_id, payload
                    )
        anneal_context = dict(envelope.global_context.anneal_context or {})

        for agent_id, agent in sorted(agent_lookup.items(), key=lambda item: item[0]):
            entry = self._transitions.get(agent_id, {})
            frame = {
                "tick": self._current_tick,
                "agent_id": agent_id,
                "map": agent.map,
                "features": agent.features,
                "metadata": dict(getattr(agent, "metadata", {}) or {}),
                "anneal_context": anneal_context,
                "action": entry.get("action"),
                "action_id": entry.get("action_id"),
                "rewards": entry.get("rewards", []),
                "dones": entry.get("dones", []),
            }
            frames.append(frame)
        return frames

    def _build_agent_from_mapping(
        self,
        agent_id: str,
        payload: Mapping[str, Any],
    ) -> AgentObservationDTO:
        return AgentObservationDTO(
            agent_id=agent_id,
            map=payload.get("map"),
            features=payload.get("features"),
            metadata=payload.get("metadata") or {},
        )

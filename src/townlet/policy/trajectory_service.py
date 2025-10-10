"""Trajectory and transition management helpers for PolicyRuntime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from townlet.world.dto.observation import ObservationEnvelope


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
        *,
        envelope: ObservationEnvelope,
    ) -> list[dict[str, Any]]:
        """Combine transitions with observations and clear the per-agent cache."""

        frames = self._frames_from_envelope(envelope)

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
    def _frames_from_envelope(
        self,
        envelope: ObservationEnvelope,
    ) -> list[dict[str, Any]]:
        frames: list[dict[str, Any]] = []
        agent_lookup = {agent.agent_id: agent for agent in envelope.agents}
        anneal_context = dict(envelope.global_context.anneal_context or {})

        for agent_id, agent in sorted(agent_lookup.items(), key=lambda item: item[0]):
            entry = self._transitions.get(agent_id, {})
            metadata = dict(getattr(agent, "metadata", {}) or {})
            dto_meta = metadata.get("dto")
            if not isinstance(dto_meta, dict):
                dto_meta = {}
            metadata["dto"] = dto_meta
            dto_meta["schema_version"] = envelope.schema_version
            if agent.position:
                dto_meta["position"] = _coerce_sequence(agent.position)
            if agent.needs:
                dto_meta["needs"] = _coerce_mapping(agent.needs)
            if agent.wallet is not None:
                try:
                    dto_meta["wallet"] = float(agent.wallet)
                except (TypeError, ValueError):
                    dto_meta["wallet"] = agent.wallet
            if agent.inventory:
                dto_meta["inventory"] = _coerce_mapping(agent.inventory)
            if agent.job:
                dto_meta["job"] = _coerce_mapping(agent.job)
            if agent.personality:
                dto_meta["personality"] = _coerce_mapping(agent.personality)
            if agent.queue_state:
                dto_meta["queue_state"] = _coerce_mapping(agent.queue_state)
            if agent.pending_intent:
                dto_meta["pending_intent"] = _coerce_mapping(agent.pending_intent)

            frame = {
                "tick": self._current_tick,
                "agent_id": agent_id,
                "map": agent.map,
                "features": agent.features,
                "metadata": metadata,
                "anneal_context": anneal_context,
                "action": entry.get("action"),
                "action_id": entry.get("action_id"),
                "rewards": entry.get("rewards", []),
                "dones": entry.get("dones", []),
            }
            frames.append(frame)
        return frames


def _coerce_mapping(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {}
    return {str(key): _coerce_value(value) for key, value in payload.items()}


def _coerce_sequence(payload: Sequence[Any] | None) -> list[Any]:
    if payload is None:
        return []
    return [_coerce_value(value) for value in payload]


def _coerce_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return _coerce_mapping(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return _coerce_sequence(value)
    try:
        if isinstance(value, (int, float)):
            return float(value)
    except Exception:
        pass
    return value

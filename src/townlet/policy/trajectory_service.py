"""Trajectory and transition management helpers for PolicyRuntime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TrajectoryService:
    """Tracks per-agent transitions and builds trajectory frames."""

    _transitions: dict[str, dict[str, Any]] = field(default_factory=dict)
    _trajectory: list[dict[str, Any]] = field(default_factory=list)
    _current_tick: int = 0

    def begin_tick(self, tick: int) -> None:
        self._current_tick = tick

    def transition_entry(self, agent_id: str) -> dict[str, Any]:
        return self._transitions.setdefault(agent_id, {})

    def record_action(self, agent_id: str, action_payload: dict[str, Any], action_id: int) -> dict[str, Any]:
        entry = self.transition_entry(agent_id)
        entry["action"] = action_payload
        entry["action_id"] = action_id
        return entry

    def append_reward(self, agent_id: str, reward: float, done: bool) -> None:
        entry = self.transition_entry(agent_id)
        entry.setdefault("rewards", []).append(reward)
        entry.setdefault("dones", []).append(bool(done))

    def flush_transitions(self, observations: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
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
        self._transitions.clear()
        return frames

    def extend_trajectory(self, frames: list[dict[str, Any]]) -> None:
        self._trajectory.extend(frames)

    def collect_trajectory(self, clear: bool = True) -> list[dict[str, Any]]:
        result = list(self._trajectory)
        if clear:
            self._trajectory.clear()
        return result

    def reset_state(self) -> None:
        self._transitions.clear()
        self._trajectory.clear()

    @property
    def transitions(self) -> dict[str, dict[str, Any]]:
        return self._transitions

    @property
    def trajectory(self) -> list[dict[str, Any]]:
        return self._trajectory


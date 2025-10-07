"""Default world adapter implementing :class:`WorldRuntime`."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from townlet.factories.registry import register
from townlet.ports.world import WorldRuntime


@dataclass
class _AgentState:
    """Minimal state tracked for each agent."""

    agent_id: str
    last_action: str = "idle"
    data: dict[str, Any] = field(default_factory=dict)

    def as_observation(self, tick: int) -> dict[str, Any]:
        payload = dict(self.data)
        payload.setdefault("tick", tick)
        payload.setdefault("last_action", self.last_action)
        return payload


class DefaultWorldAdapter(WorldRuntime):
    """Lightweight in-memory world used as the default runtime."""

    def __init__(self, agents: Iterable[str] | None = None) -> None:
        self._base_agents = tuple(agents or ("agent-0",))
        if not self._base_agents:
            raise ValueError("DefaultWorldAdapter requires at least one agent")
        self._tick = 0
        self._seed = None
        self._agents: dict[str, _AgentState] = {}
        self._pending_actions: dict[str, Any] = {}
        self.reset()

    def reset(self, seed: int | None = None) -> None:
        self._seed = seed
        self._tick = 0
        self._agents = {agent_id: _AgentState(agent_id=agent_id) for agent_id in self._base_agents}
        self._pending_actions.clear()

    def tick(self) -> None:
        self._tick += 1
        for agent_id, action in list(self._pending_actions.items()):
            if agent_id in self._agents:
                self._agents[agent_id].last_action = str(action)
        self._pending_actions.clear()

    def agents(self) -> Iterable[str]:
        return tuple(self._agents.keys())

    def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]:
        ids = tuple(agent_ids) if agent_ids is not None else tuple(self._agents.keys())
        return {agent_id: self._agents[agent_id].as_observation(self._tick) for agent_id in ids if agent_id in self._agents}

    def apply_actions(self, actions: Mapping[str, Any]) -> None:
        self._pending_actions = dict(actions)

    def snapshot(self) -> Mapping[str, Any]:
        return {
            "tick": self._tick,
            "agents": {agent_id: state.as_observation(self._tick) for agent_id, state in self._agents.items()},
            "seed": self._seed,
        }


@register("world", "default")
def _build_default_world(**kwargs: Any) -> WorldRuntime:
    return DefaultWorldAdapter(**kwargs)

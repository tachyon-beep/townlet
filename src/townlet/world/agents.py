"""Agent registry primitives (skeleton)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional


@dataclass
class AgentRecord:
    """Minimal placeholder for agent metadata."""

    agent_id: str
    position: tuple[int, int] = (0, 0)


class AgentRegistry:
    """Lightweight registry; real logic will be added during WP2."""

    def __init__(self) -> None:
        self._agents: Dict[str, AgentRecord] = {}

    def add(self, record: AgentRecord) -> None:
        raise NotImplementedError("AgentRegistry.add pending WP2 implementation")

    def remove(self, agent_id: str) -> None:
        raise NotImplementedError("AgentRegistry.remove pending WP2 implementation")

    def get(self, agent_id: str) -> Optional[AgentRecord]:
        raise NotImplementedError("AgentRegistry.get pending WP2 implementation")

    def ids(self) -> Iterable[str]:
        raise NotImplementedError("AgentRegistry.ids pending WP2 implementation")


__all__ = ["AgentRecord", "AgentRegistry"]

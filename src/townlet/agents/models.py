"""Agent-related dataclasses and helpers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Personality:
    extroversion: float
    forgiveness: float
    ambition: float


@dataclass
class RelationshipEdge:
    other_id: str
    trust: float
    familiarity: float
    rivalry: float


@dataclass
class AgentState:
    """Canonical agent state used across modules."""

    agent_id: str
    needs: dict[str, float]
    wallet: float
    personality: Personality
    relationships: list[RelationshipEdge] = field(default_factory=list)

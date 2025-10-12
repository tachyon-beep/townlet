"""Relationships and rivalry helpers."""

from __future__ import annotations

from townlet.agents.relationship_modifiers import RelationshipEvent
from townlet.world.agents.relationships_service import RelationshipService
from townlet.world.relationships import RelationshipLedger

from .base import SystemContext


def step(ctx: SystemContext) -> None:
    """Advance relationship decay each tick."""

    state = ctx.state
    service = getattr(state, "_relationships", None)

    if service is None:
        legacy_decay = getattr(state, "relationship_decay", None)
        if callable(legacy_decay):
            legacy_decay()
        return

    decay(service)


def relationships_snapshot(service: RelationshipService) -> dict[str, dict[str, dict[str, float]]]:
    return service.relationships_snapshot()


def relationship_metrics_snapshot(service: RelationshipService) -> dict[str, object]:
    return service.relationship_metrics_snapshot()


def load_relationship_metrics(service: RelationshipService, payload: dict[str, object] | None) -> None:
    service.load_relationship_metrics(payload)


def load_relationship_snapshot(
    service: RelationshipService,
    snapshot: dict[str, dict[str, dict[str, float]]],
) -> None:
    service.load_relationship_snapshot(snapshot)


def update_relationship(
    service: RelationshipService,
    agent_a: str,
    agent_b: str,
    *,
    trust: float = 0.0,
    familiarity: float = 0.0,
    rivalry: float = 0.0,
    event: RelationshipEvent = "generic",
) -> None:
    service.update_relationship(
        agent_a,
        agent_b,
        trust=trust,
        familiarity=familiarity,
        rivalry=rivalry,
        event=event,
    )


def set_relationship(
    service: RelationshipService,
    agent_a: str,
    agent_b: str,
    *,
    trust: float,
    familiarity: float,
    rivalry: float,
) -> None:
    service.set_relationship(
        agent_a,
        agent_b,
        trust=trust,
        familiarity=familiarity,
        rivalry=rivalry,
    )


def relationship_tie(service: RelationshipService, agent_id: str, other_id: str):
    return service.relationship_tie(agent_id, other_id)


def get_relationship_ledger(service: RelationshipService, agent_id: str) -> RelationshipLedger:
    return service.get_relationship_ledger(agent_id)


def get_rivalry_ledger(service: RelationshipService, agent_id: str):
    return service.get_rivalry_ledger(agent_id)


def rivalry_snapshot(service: RelationshipService) -> dict[str, dict[str, float]]:
    return service.rivalry_snapshot()


def rivalry_value(service: RelationshipService, agent_id: str, other_id: str) -> float:
    return service.rivalry_value(agent_id, other_id)


def rivalry_should_avoid(service: RelationshipService, agent_id: str, other_id: str) -> bool:
    return service.rivalry_should_avoid(agent_id, other_id)


def rivalry_top(service: RelationshipService, agent_id: str, limit: int) -> list[tuple[str, float]]:
    return service.rivalry_top(agent_id, limit)


def apply_rivalry_conflict(
    service: RelationshipService,
    agent_a: str,
    agent_b: str,
    *,
    intensity: float,
) -> None:
    service.apply_rivalry_conflict(agent_a, agent_b, intensity=intensity)


def decay(service: RelationshipService) -> None:
    service.decay()


def remove_agent(service: RelationshipService, agent_id: str) -> None:
    service.remove_agent(agent_id)


__all__ = [
    "apply_rivalry_conflict",
    "decay",
    "get_relationship_ledger",
    "get_rivalry_ledger",
    "load_relationship_metrics",
    "load_relationship_snapshot",
    "relationship_metrics_snapshot",
    "relationship_tie",
    "relationships_snapshot",
    "remove_agent",
    "rivalry_should_avoid",
    "rivalry_snapshot",
    "rivalry_top",
    "rivalry_value",
    "set_relationship",
    "step",
    "update_relationship",
]

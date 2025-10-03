"""Test helpers for seeding social interaction data."""

from __future__ import annotations

from townlet.world.grid import WorldState


def seed_relationship_activity(
    world: WorldState,
    *,
    agent_a: str,
    agent_b: str,
    rivalry_intensity: float = 1.0,
) -> None:
    """Populate trust/familiarity/rivalry metrics for tests expecting social signals."""

    world.register_rivalry_conflict(agent_a, agent_b, intensity=rivalry_intensity)
    world.update_relationship(
        agent_a,
        agent_b,
        trust=0.6,
        familiarity=0.3,
    )

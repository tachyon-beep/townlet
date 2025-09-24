"""Agent lifecycle enforcement (exits, spawns, cooldowns)."""
from __future__ import annotations

from typing import Dict

from townlet.config import SimulationConfig
from townlet.world.grid import WorldState


class LifecycleManager:
    """Centralises lifecycle checks described in docs/CONCEPTUAL_DESIGN.md#18."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.exits_today = 0

    def evaluate(self, world: WorldState, tick: int) -> Dict[str, bool]:
        """Return a map of agent_id -> terminated flag."""
        terminated: Dict[str, bool] = {}
        for agent_id, snapshot in world.agents.items():
            hunger = snapshot.needs.get("hunger", 0.0)
            if hunger <= 0.03:
                terminated[agent_id] = True
            else:
                terminated[agent_id] = False
        return terminated

"""Reward calculation guardrails and aggregation."""
from __future__ import annotations

from typing import Dict

from townlet.config import SimulationConfig
from townlet.world.grid import WorldState


class RewardEngine:
    """Compute per-agent rewards with clipping and guardrails."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config

    def compute(self, world: WorldState, terminated: Dict[str, bool]) -> Dict[str, float]:
        rewards: Dict[str, float] = {}
        clip_value = self.config.rewards.clip.clip_per_tick
        weights = self.config.rewards.needs_weights
        survival_tick = self.config.rewards.survival_tick
        for agent_id, snapshot in world.agents.items():
            total = survival_tick
            for need, value in snapshot.needs.items():
                weight = weights.__dict__.get(need, 0.0)
                deficit = 1.0 - value
                total -= weight * max(0.0, deficit) ** 2
            total = max(min(total, clip_value), -clip_value)
            if terminated.get(agent_id):
                total = min(total, 0.0)
            rewards[agent_id] = total
        return rewards

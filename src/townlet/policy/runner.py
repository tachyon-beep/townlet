"""Policy orchestration scaffolding."""
from __future__ import annotations

from typing import Dict

from townlet.config import SimulationConfig
from townlet.world.grid import WorldState
from townlet.policy.behavior import AgentIntent, BehaviorController, build_behavior


class PolicyRuntime:
    """Bridges the simulation with PPO/backends via PettingZoo."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.behavior: BehaviorController = build_behavior(config)

    def decide(self, world: WorldState, tick: int) -> Dict[str, object]:
        """Return a primitive action per agent."""
        actions: Dict[str, object] = {}
        for agent_id in world.agents:
            intent: AgentIntent = self.behavior.decide(world, agent_id)
            if intent.kind == "wait":
                actions[agent_id] = {"kind": "wait"}
            else:
                actions[agent_id] = {
                    "kind": intent.kind,
                    "object": intent.object_id,
                    "affordance": intent.affordance_id,
                    "blocked": intent.blocked,
                }
        return actions

    def post_step(self, rewards: Dict[str, float], terminated: Dict[str, bool]) -> None:
        """Record rewards and termination signals into buffers."""
        # TODO(@townlet): Feed transitions into PPO learner.
        _ = rewards, terminated


class TrainingHarness:
    """Coordinates RL training sessions."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        # TODO(@townlet): Wire up PPO trainer, evaluators, and promotion hooks.

    def run(self) -> None:
        """Entry point for CLI training runs."""
        # TODO(@townlet): Implement epoch loop + stability guardrails.
        raise NotImplementedError("Training harness not yet implemented")

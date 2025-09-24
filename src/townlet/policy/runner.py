"""Policy orchestration scaffolding."""
from __future__ import annotations

from typing import Dict

from townlet.config import SimulationConfig
from townlet.world.grid import WorldState


class PolicyRuntime:
    """Bridges the simulation with PPO/backends via PettingZoo."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        # TODO(@townlet): Initialise PettingZoo env and scripted controllers.

    def decide(self, world: WorldState, tick: int) -> Dict[str, object]:
        """Return a primitive action per agent."""
        # TODO(@townlet): Integrate meta-policy + scripted controllers.
        return {agent_id: {"action": "wait", "tick": tick} for agent_id in world.agents}

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

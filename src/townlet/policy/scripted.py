"""Simple scripted policy helpers for trajectory capture."""

from __future__ import annotations

from dataclasses import dataclass

from townlet.world.grid import WorldState


class ScriptedPolicy:
    """Base class for scripted policies used during BC trajectory capture."""

    name: str = "scripted"

    def decide(
        self, world: WorldState, tick: int
    ) -> dict[str, dict]:  # pragma: no cover - interface
        raise NotImplementedError

    def describe(self) -> str:
        return self.name

    @property
    def trajectory_prefix(self) -> str:
        return self.name


@dataclass
class IdlePolicy(ScriptedPolicy):
    """Default scripted policy: all agents wait every tick."""

    name: str = "idle"

    def decide(self, world: WorldState, tick: int) -> dict[str, dict]:
        return {agent_id: {"kind": "wait"} for agent_id in world.agents.keys()}


def get_scripted_policy(name: str) -> ScriptedPolicy:
    """Factory for scripted policies; extend with richer behaviours as needed."""

    normalised = name.strip().lower()
    if normalised in {"idle", "idle_policy"}:
        return IdlePolicy()
    raise ValueError(f"Unknown scripted policy: {name}")


class ScriptedPolicyAdapter:
    """Adapter so SimulationLoop can call scripted policies."""

    def __init__(self, scripted_policy: ScriptedPolicy) -> None:
        self.scripted_policy = scripted_policy
        self.last_actions: dict[str, dict] = {}
        self.last_rewards: dict[str, float] = {}
        self.last_terminated: dict[str, bool] = {}

    def decide(self, world: WorldState, tick: int) -> dict[str, dict]:
        actions = self.scripted_policy.decide(world, tick)
        # Ensure every agent has an action (default wait)
        wait_action = {"kind": "wait"}
        self.last_actions = {
            agent_id: actions.get(agent_id, wait_action)
            for agent_id in world.agents.keys()
        }
        return self.last_actions

    def post_step(self, rewards: dict[str, float], terminated: dict[str, bool]) -> None:
        base_agents = self.last_actions.keys()
        self.last_rewards = {
            agent_id: float(rewards.get(agent_id, 0.0)) for agent_id in base_agents
        }
        self.last_terminated = {
            agent_id: bool(terminated.get(agent_id, False)) for agent_id in base_agents
        }

    def flush_transitions(
        self, observations
    ) -> None:  # pragma: no cover - SimulationLoop hook
        # Scripted policies do not accumulate PPO transitions.
        return

    def collect_trajectory(
        self, *, clear: bool = False
    ):  # pragma: no cover - SimulationLoop hook
        return []

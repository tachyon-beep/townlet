"""Helpers for applying scenario initialisation to simulation loops."""
from __future__ import annotations

from typing import Any

from townlet.core.sim_loop import SimulationLoop
from townlet.policy.behavior import AgentIntent
from townlet.world.grid import AgentSnapshot


def apply_scenario(loop: SimulationLoop, scenario: dict[str, Any]) -> None:
    objects = scenario.get("objects", [])
    for obj in objects:
        position = None
        if "position" in obj and obj["position"] is not None:
            raw = obj["position"]
            if isinstance(raw, (list, tuple)) and len(raw) == 2:
                position = (int(raw[0]), int(raw[1]))
            else:
                raise ValueError(f"Invalid object position for {obj['id']}: {raw}")
        loop.world.register_object(
            object_id=obj["id"],
            object_type=obj["type"],
            position=position,
        )

    schedules: dict[str, list[AgentIntent]] = {}
    for agent in scenario.get("agents", []):
        agent_id = agent["id"]
        position = tuple(agent.get("position", (0, 0)))  # type: ignore[arg-type]
        needs = dict(agent.get("needs", {}))
        snapshot = AgentSnapshot(
            agent_id,
            position,
            needs,
            wallet=float(agent.get("wallet", 0.0)),
        )
        if agent.get("job"):
            snapshot.job_id = agent["job"]
        loop.world.agents[agent_id] = snapshot
        intents: list[AgentIntent] = []
        for entry in agent.get("schedule", []):
            data = dict(entry)
            kind = data.pop("kind", "wait")
            if "object" in data and "object_id" not in data:
                data["object_id"] = data.pop("object")
            if "affordance" in data and "affordance_id" not in data:
                data["affordance_id"] = data.pop("affordance")
            if "position" in data and data["position"] is not None:
                data["position"] = tuple(data["position"])
            intents.append(AgentIntent(kind=kind, **data))
        schedules[agent_id] = intents
    if schedules:
        loop.policy.behavior = ScenarioBehavior(loop.policy.behavior, schedules)


def seed_default_agents(loop: SimulationLoop) -> None:
    loop.world.register_object(object_id="stove_1", object_type="stove")
    loop.world.agents["alice"] = AgentSnapshot(
        "alice",
        (0, 0),
        {"hunger": 0.3, "hygiene": 0.4, "energy": 0.5},
        wallet=2.0,
    )
    loop.world.agents["bob"] = AgentSnapshot(
        "bob",
        (1, 0),
        {"hunger": 0.6, "hygiene": 0.7, "energy": 0.8},
        wallet=3.0,
    )


def has_agents(loop: SimulationLoop) -> bool:
    return bool(loop.world.agents)


class ScenarioBehavior:
    """Wraps an existing behavior controller with scripted schedules."""

    def __init__(self, base_behavior, schedules: dict[str, list[AgentIntent]]) -> None:
        self.base = base_behavior
        self._schedules = schedules
        self._indices: dict[str, int] = dict.fromkeys(schedules, 0)

    def decide(self, world, agent_id):  # type: ignore[override]
        seq = self._schedules.get(agent_id)
        if not seq:
            return self.base.decide(world, agent_id)
        idx = self._indices.setdefault(agent_id, 0)
        intent = seq[idx % len(seq)]
        self._indices[agent_id] = idx + 1
        return intent

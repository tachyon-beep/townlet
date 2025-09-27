"""Behavior controller interfaces for scripted decision logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from townlet.config import SimulationConfig
from townlet.world.grid import WorldState


@dataclass
class AgentIntent:
    """Represents the next action an agent wishes to perform."""

    kind: str
    object_id: Optional[str] = None
    affordance_id: Optional[str] = None
    blocked: bool = False
    position: Optional[tuple[int, int]] = None


class BehaviorController(Protocol):
    """Defines the interface for agent decision logic."""

    def decide(self, world: WorldState, agent_id: str) -> AgentIntent: ...


class IdleBehavior(BehaviorController):
    """Default no-op behavior that keeps agents idle."""

    def decide(self, world: WorldState, agent_id: str) -> AgentIntent:  # noqa: D401
        return AgentIntent(kind="wait")


class ScriptedBehavior(BehaviorController):
    """Simple rule-based controller used before RL policies are available."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.thresholds = config.behavior
        self.pending: dict[str, dict[str, str]] = {}

    def decide(self, world: WorldState, agent_id: str) -> AgentIntent:
        snapshot = world.agents.get(agent_id)
        if snapshot is None:
            return AgentIntent(kind="wait")

        self._cleanup_pending(world, agent_id)
        pending = self.pending.get(agent_id)
        if pending:
            object_id = pending["object_id"]
            affordance_id = pending["affordance_id"]
            active = world.queue_manager.active_agent(object_id)
            running = world._running_affordances.get(object_id)  # type: ignore[attr-defined]
            if running and running.agent_id == agent_id:
                return AgentIntent(kind="wait")
            if active == agent_id:
                return AgentIntent(
                    kind="start", object_id=object_id, affordance_id=affordance_id
                )
            if not self._rivals_in_queue(world, agent_id, object_id):
                return AgentIntent(kind="request", object_id=object_id)
            self.pending.pop(agent_id, None)

        # If pending intent was dropped due to rivalry, fall through to new plan.

        job_intent = self._maybe_move_to_job(world, agent_id, snapshot)
        if job_intent:
            return job_intent

        need_intent = self._satisfy_needs(world, agent_id, snapshot)
        if need_intent:
            return need_intent

        return AgentIntent(kind="wait")

    def _cleanup_pending(self, world: WorldState, agent_id: str) -> None:
        state = self.pending.get(agent_id)
        if not state:
            return
        object_id = state["object_id"]
        running = world._running_affordances.get(object_id)  # type: ignore[attr-defined]
        active = world.queue_manager.active_agent(object_id)
        if running and running.agent_id == agent_id:
            return
        if active == agent_id:
            return
        self.pending.pop(agent_id, None)

    def _maybe_move_to_job(
        self, world: WorldState, agent_id: str, snapshot: object
    ) -> Optional[AgentIntent]:
        job_id = getattr(snapshot, "job_id", None)
        if job_id is None:
            return None
        job_spec = self.config.jobs.get(job_id)
        if job_spec is None or job_spec.location is None:
            return None
        buffer = self.thresholds.job_arrival_buffer
        start = job_spec.start_tick
        required_position = job_spec.location
        if (
            start - buffer <= world.tick < start
            and snapshot.position != required_position
        ):
            return AgentIntent(kind="move", position=required_position)
        return None

    def _satisfy_needs(
        self, world: WorldState, agent_id: str, snapshot: object
    ) -> Optional[AgentIntent]:
        hunger = snapshot.needs.get("hunger", 1.0)
        hygiene = snapshot.needs.get("hygiene", 1.0)
        energy = snapshot.needs.get("energy", 1.0)

        if hunger < self.thresholds.hunger_threshold:
            intent = self._plan_meal(world, agent_id)
            if intent:
                return intent
        if hygiene < self.thresholds.hygiene_threshold:
            shower_id = self._find_object_of_type(world, "shower")
            if shower_id:
                if not self._rivals_in_queue(world, agent_id, shower_id):
                    self.pending[agent_id] = {
                        "object_id": shower_id,
                        "affordance_id": "use_shower",
                    }
                    return AgentIntent(kind="request", object_id=shower_id)
        if energy < self.thresholds.energy_threshold:
            bed_id = self._find_object_of_type(world, "bed")
            if bed_id:
                if not self._rivals_in_queue(world, agent_id, bed_id):
                    self.pending[agent_id] = {
                        "object_id": bed_id,
                        "affordance_id": "rest_sleep",
                    }
                    return AgentIntent(kind="request", object_id=bed_id)
        return None

    def _rivals_in_queue(
        self, world: WorldState, agent_id: str, object_id: str
    ) -> bool:
        active = world.queue_manager.active_agent(object_id)
        if (
            active
            and active != agent_id
            and world.rivalry_should_avoid(agent_id, active)
        ):
            return True
        queue = world.queue_manager.queue_snapshot(object_id)
        for rival_id in queue:
            if rival_id == agent_id:
                continue
            if world.rivalry_should_avoid(agent_id, rival_id):
                return True
        return False

    def _plan_meal(self, world: WorldState, agent_id: str) -> Optional[AgentIntent]:
        fridge_id = self._find_object_of_type(world, "fridge")
        stove_id = self._find_object_of_type(world, "stove")
        if fridge_id:
            fridge = world.objects.get(fridge_id)
            if fridge and fridge.stock.get("meals", 0) > 0:
                if not self._rivals_in_queue(world, agent_id, fridge_id):
                    self.pending[agent_id] = {
                        "object_id": fridge_id,
                        "affordance_id": "eat_meal",
                    }
                    return AgentIntent(kind="request", object_id=fridge_id)
        if stove_id:
            stove = world.objects.get(stove_id)
            if stove and stove.stock.get("raw_ingredients", 0) > 0:
                if not self._rivals_in_queue(world, agent_id, stove_id):
                    self.pending[agent_id] = {
                        "object_id": stove_id,
                        "affordance_id": "cook_meal",
                    }
                    return AgentIntent(kind="request", object_id=stove_id)
        return None

    def _find_object_of_type(
        self, world: WorldState, object_type: str
    ) -> Optional[str]:
        for object_id, obj in world.objects.items():
            if obj.object_type == object_type:
                return object_id
        return None


def build_behavior(config: SimulationConfig) -> BehaviorController:
    return ScriptedBehavior(config)

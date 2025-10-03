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
    target_agent: Optional[str] = None
    quality: Optional[float] = None


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
        self._chat_cooldowns: dict[str, int] = {}
        self._chat_cooldown_ticks: int = 30
        self._chat_min_extroversion: float = 0.2

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
            running = world.affordance_runtime.running_affordances.get(object_id)
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

        chat_intent = self._maybe_chat(world, agent_id, snapshot)
        if chat_intent:
            return chat_intent

        avoid_intent = self._avoid_rivals(world, agent_id, snapshot)
        if avoid_intent:
            return avoid_intent

        return AgentIntent(kind="wait")

    def cancel_pending(self, agent_id: str) -> None:
        self.pending.pop(agent_id, None)

    def _cleanup_pending(self, world: WorldState, agent_id: str) -> None:
        state = self.pending.get(agent_id)
        if not state:
            return
        object_id = state["object_id"]
        running = world.affordance_runtime.running_affordances.get(object_id)
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
            if shower_id and not self._rivals_in_queue(world, agent_id, shower_id):
                self.pending[agent_id] = {
                    "object_id": shower_id,
                    "affordance_id": "use_shower",
                }
                return AgentIntent(kind="request", object_id=shower_id)
        if energy < self.thresholds.energy_threshold:
            bed_id = self._find_object_of_type(world, "bed")
            if bed_id and not self._rivals_in_queue(world, agent_id, bed_id):
                self.pending[agent_id] = {
                    "object_id": bed_id,
                    "affordance_id": "rest_sleep",
                }
                return AgentIntent(kind="request", object_id=bed_id)
        return None

    def _maybe_chat(
        self, world: WorldState, agent_id: str, snapshot: object
    ) -> Optional[AgentIntent]:
        relationships_stage = getattr(self.config.features.stages, "relationships", "OFF")
        if relationships_stage == "OFF":
            return None
        tick = int(getattr(world, "tick", 0))
        if tick < self._chat_cooldowns.get(agent_id, 0):
            return None
        personality = getattr(snapshot, "personality", None)
        extroversion = float(getattr(personality, "extroversion", 0.0)) if personality else 0.0
        if extroversion < self._chat_min_extroversion:
            return None
        if snapshot.needs.get("hunger", 1.0) < self.thresholds.hunger_threshold:
            return None
        if snapshot.needs.get("hygiene", 1.0) < self.thresholds.hygiene_threshold:
            return None
        if snapshot.needs.get("energy", 1.0) < self.thresholds.energy_threshold:
            return None

        position = getattr(snapshot, "position", None)
        if position is None:
            return None

        candidates: list[tuple[float, str, float]] = []
        for other_id, other in world.agents.items():
            if other_id == agent_id:
                continue
            if getattr(other, "position", None) != position:
                continue
            if world.rivalry_should_avoid(agent_id, other_id):
                continue
            tie = world.relationship_tie(agent_id, other_id)
            trust = float(getattr(tie, "trust", 0.0)) if tie else 0.0
            familiarity = float(getattr(tie, "familiarity", 0.0)) if tie else 0.0
            rivalry = world.rivalry_value(agent_id, other_id)
            score = trust + familiarity - rivalry + 0.1 * extroversion
            candidates.append((score, other_id, rivalry))

        if not candidates:
            return None

        candidates.sort(key=lambda entry: entry[0], reverse=True)
        best_score, listener_id, rivalry_value = candidates[0]
        if best_score <= 0.0:
            return None

        tie = world.relationship_tie(agent_id, listener_id)
        trust = float(getattr(tie, "trust", 0.0)) if tie else 0.0
        familiarity = float(getattr(tie, "familiarity", 0.0)) if tie else 0.0
        quality = 0.5 + 0.3 * extroversion + 0.2 * trust + 0.1 * familiarity - 0.2 * rivalry_value
        quality = max(0.1, min(1.0, quality))

        self._chat_cooldowns[agent_id] = tick + self._chat_cooldown_ticks
        self.pending.pop(agent_id, None)
        return AgentIntent(kind="chat", target_agent=listener_id, quality=quality)

    def _avoid_rivals(
        self, world: WorldState, agent_id: str, snapshot: object
    ) -> Optional[AgentIntent]:
        position = getattr(snapshot, "position", None)
        if position is None:
            return None
        cx, cy = position
        rivals_present = any(
            other_id != agent_id
            and getattr(other, "position", None) == position
            and world.rivalry_should_avoid(agent_id, other_id)
            for other_id, other in world.agents.items()
        )
        if not rivals_present:
            return None

        grid_size = getattr(self.config.world, "grid_size", (48, 48))
        width, height = int(grid_size[0]), int(grid_size[1])
        occupied_positions = {
            getattr(agent, "position", None)
            for agent in world.agents.values()
        }
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            candidate = (nx, ny)
            if candidate in occupied_positions:
                continue
            return AgentIntent(kind="move", position=candidate)
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
            if (
                fridge
                and fridge.stock.get("meals", 0) > 0
                and not self._rivals_in_queue(world, agent_id, fridge_id)
            ):
                self.pending[agent_id] = {
                    "object_id": fridge_id,
                    "affordance_id": "eat_meal",
                }
                return AgentIntent(kind="request", object_id=fridge_id)
        if stove_id:
            stove = world.objects.get(stove_id)
            if (
                stove
                and stove.stock.get("raw_ingredients", 0) > 0
                and not self._rivals_in_queue(world, agent_id, stove_id)
            ):
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

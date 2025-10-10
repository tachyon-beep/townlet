"""Behavior controller interfaces for scripted decision logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Protocol

from townlet.agents.models import PersonalityProfiles
from townlet.config import SimulationConfig
from townlet.policy.dto_view import DTOWorldView
from townlet.world.grid import WorldState


@dataclass
class AgentIntent:
    """Represents the next action an agent wishes to perform."""

    kind: str
    object_id: str | None = None
    affordance_id: str | None = None
    blocked: bool = False
    position: tuple[int, int] | None = None
    target_agent: str | None = None
    quality: float | None = None


class BehaviorController(Protocol):
    """Defines the interface for agent decision logic."""

    def decide(
        self,
        world: WorldState,
        agent_id: str,
        *,
        dto_world: DTOWorldView | None = None,
    ) -> AgentIntent: ...


class IdleBehavior(BehaviorController):
    """Default no-op behavior that keeps agents idle."""

    def decide(
        self,
        world: WorldState,
        agent_id: str,
        *,
        dto_world: DTOWorldView | None = None,
    ) -> AgentIntent:
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
        self._personality_bias_enabled = config.personality_profiles_enabled()
        self._need_scaling_enabled = config.reward_personality_scaling_enabled()
        base_threshold = float(config.conflict.rivalry.avoid_threshold)
        self._avoid_threshold_base = max(0.0, min(1.0, base_threshold))

    def decide(
        self,
        world: WorldState,
        agent_id: str,
        *,
        dto_world: DTOWorldView | None = None,
    ) -> AgentIntent:
        snapshot = self._agent_snapshot(world, agent_id, dto_world)
        if snapshot is None:
            return AgentIntent(kind="wait")

        queue_view = self._queue_view(world, dto_world)
        running_affordances = self._running_affordances(world, dto_world)
        relationship_view = self._relationship_view(world, dto_world)
        current_tick = self._current_tick(world, dto_world)

        self._cleanup_pending(agent_id, queue_view, running_affordances)
        pending = self.pending.get(agent_id)
        if pending:
            object_id = pending["object_id"]
            affordance_id = pending["affordance_id"]
            active = queue_view.active_agent(object_id)
            running = running_affordances.get(object_id)
            if running and getattr(running, "agent_id", None) == agent_id:
                return AgentIntent(kind="wait")
            if active == agent_id:
                return AgentIntent(
                    kind="start", object_id=object_id, affordance_id=affordance_id
                )
            if not self._rivals_in_queue(
                world,
                agent_id,
                object_id,
                queue_view=queue_view,
                relationship_view=relationship_view,
                dto_world=dto_world,
            ):
                return AgentIntent(kind="request", object_id=object_id)
            self.pending.pop(agent_id, None)

        # If pending intent was dropped due to rivalry, fall through to new plan.

        job_intent = self._maybe_move_to_job(
            world,
            agent_id,
            snapshot,
            current_tick=current_tick,
        )
        if job_intent:
            return job_intent

        need_intent = self._satisfy_needs(
            world,
            agent_id,
            snapshot,
            queue_view=queue_view,
            relationship_view=relationship_view,
            dto_world=dto_world,
        )
        if need_intent:
            return need_intent

        chat_intent = self._maybe_chat(
            world,
            agent_id,
            snapshot,
            relationship_view=relationship_view,
            dto_world=dto_world,
            current_tick=current_tick,
        )
        if chat_intent:
            return chat_intent

        avoid_intent = self._avoid_rivals(
            world,
            agent_id,
            snapshot,
            relationship_view=relationship_view,
            dto_world=dto_world,
        )
        if avoid_intent:
            return avoid_intent

        return AgentIntent(kind="wait")

    def cancel_pending(self, agent_id: str) -> None:
        self.pending.pop(agent_id, None)

    def _cleanup_pending(
        self,
        agent_id: str,
        queue_view: object,
        running_affordances: Mapping[str, Any],
    ) -> None:
        state = self.pending.get(agent_id)
        if not state:
            return
        object_id = state["object_id"]
        running = running_affordances.get(object_id)
        active = queue_view.active_agent(object_id)
        if running and getattr(running, "agent_id", None) == agent_id:
            return
        if active == agent_id:
            return
        self.pending.pop(agent_id, None)

    def _maybe_move_to_job(
        self,
        world: WorldState,
        agent_id: str,
        snapshot: object,
        *,
        current_tick: int,
    ) -> AgentIntent | None:
        job_id = getattr(snapshot, "job_id", None)
        if job_id is None:
            return None
        job_spec = self.config.jobs.get(job_id)
        if job_spec is None or job_spec.location is None:
            return None
        buffer = self.thresholds.job_arrival_buffer
        work_bias = self._behavior_bias(snapshot, "work_affinity")
        if work_bias != 1.0:
            scaled = round(buffer * work_bias)
            buffer = int(min(240, max(0, scaled)))
        start = job_spec.start_tick
        required_position = job_spec.location
        if (
            start - buffer <= current_tick < start
            and snapshot.position != required_position
        ):
            return AgentIntent(kind="move", position=required_position)
        return None

    def _satisfy_needs(
        self,
        world: WorldState,
        agent_id: str,
        snapshot: object,
        *,
        queue_view: object,
        relationship_view: object,
        dto_world: DTOWorldView | None,
    ) -> AgentIntent | None:
        hunger = snapshot.needs.get("hunger", 1.0)
        hygiene = snapshot.needs.get("hygiene", 1.0)
        energy = snapshot.needs.get("energy", 1.0)

        hunger_threshold = self._need_threshold(
            snapshot, "hunger", self.thresholds.hunger_threshold
        )
        hygiene_threshold = self._need_threshold(
            snapshot, "hygiene", self.thresholds.hygiene_threshold
        )
        energy_threshold = self._need_threshold(
            snapshot, "energy", self.thresholds.energy_threshold
        )

        if hunger < hunger_threshold:
            intent = self._plan_meal(
                world,
                agent_id,
                queue_view=queue_view,
                relationship_view=relationship_view,
                dto_world=dto_world,
            )
            if intent:
                return intent
        if hygiene < hygiene_threshold:
            shower_id = self._find_object_of_type(world, "shower")
            if shower_id and not self._rivals_in_queue(
                world,
                agent_id,
                shower_id,
                queue_view=queue_view,
                relationship_view=relationship_view,
                dto_world=dto_world,
            ):
                self.pending[agent_id] = {
                    "object_id": shower_id,
                    "affordance_id": "use_shower",
                }
                return AgentIntent(kind="request", object_id=shower_id)
        if energy < energy_threshold:
            bed_id = self._find_object_of_type(world, "bed")
            if bed_id and not self._rivals_in_queue(
                world,
                agent_id,
                bed_id,
                queue_view=queue_view,
                relationship_view=relationship_view,
                dto_world=dto_world,
            ):
                self.pending[agent_id] = {
                    "object_id": bed_id,
                    "affordance_id": "rest_sleep",
                }
                return AgentIntent(kind="request", object_id=bed_id)
        return None

    def _maybe_chat(
        self,
        world: WorldState,
        agent_id: str,
        snapshot: object,
        *,
        relationship_view: object,
        dto_world: DTOWorldView | None,
        current_tick: int,
    ) -> AgentIntent | None:
        relationships_stage = getattr(self.config.features.stages, "relationships", "OFF")
        if relationships_stage == "OFF":
            return None
        tick = current_tick
        chat_bias = self._behavior_bias(snapshot, "chat_preference")
        bias_factor = chat_bias if chat_bias > 0.0 else 1.0
        min_extroversion = min(1.0, max(0.0, self._chat_min_extroversion / bias_factor))
        cooldown_ticks = max(1, round(self._chat_cooldown_ticks / bias_factor))

        hunger_threshold = self._need_threshold(
            snapshot, "hunger", self.thresholds.hunger_threshold
        )
        hygiene_threshold = self._need_threshold(
            snapshot, "hygiene", self.thresholds.hygiene_threshold
        )
        energy_threshold = self._need_threshold(
            snapshot, "energy", self.thresholds.energy_threshold
        )

        if tick < self._chat_cooldowns.get(agent_id, 0):
            return None
        personality = getattr(snapshot, "personality", None)
        extroversion = float(getattr(personality, "extroversion", 0.0)) if personality else 0.0
        if extroversion < min_extroversion:
            return None
        if snapshot.needs.get("hunger", 1.0) < hunger_threshold:
            return None
        if snapshot.needs.get("hygiene", 1.0) < hygiene_threshold:
            return None
        if snapshot.needs.get("energy", 1.0) < energy_threshold:
            return None

        position = getattr(snapshot, "position", None)
        if position is None:
            return None

        candidates: list[tuple[float, str, float]] = []
        for other_id, other in self._iter_agent_snapshots(world, dto_world):
            if other_id == agent_id:
                continue
            if getattr(other, "position", None) != position:
                continue
            if self.should_avoid(
                world,
                agent_id,
                other_id,
                relationship_view=relationship_view,
                dto_world=dto_world,
            ):
                continue
            tie = relationship_view.relationship_tie(agent_id, other_id)
            trust = float(getattr(tie, "trust", 0.0)) if tie else 0.0
            familiarity = float(getattr(tie, "familiarity", 0.0)) if tie else 0.0
            rivalry = relationship_view.rivalry_value(agent_id, other_id)
            score = trust + familiarity - rivalry + 0.1 * extroversion
            candidates.append((score, other_id, rivalry))

        if not candidates:
            return None

        candidates.sort(key=lambda entry: entry[0], reverse=True)
        best_score, listener_id, rivalry_value = candidates[0]
        if best_score <= 0.0:
            return None

        tie = relationship_view.relationship_tie(agent_id, listener_id)
        trust = float(getattr(tie, "trust", 0.0)) if tie else 0.0
        familiarity = float(getattr(tie, "familiarity", 0.0)) if tie else 0.0
        quality = 0.5 + 0.3 * extroversion + 0.2 * trust + 0.1 * familiarity - 0.2 * rivalry_value
        quality *= max(0.5, min(1.5, bias_factor))
        quality = max(0.1, min(1.0, quality))

        self._chat_cooldowns[agent_id] = tick + cooldown_ticks
        self.pending.pop(agent_id, None)
        return AgentIntent(kind="chat", target_agent=listener_id, quality=quality)

    def _avoid_rivals(
        self,
        world: WorldState,
        agent_id: str,
        snapshot: object,
        *,
        relationship_view: object,
        dto_world: DTOWorldView | None,
    ) -> AgentIntent | None:
        position = getattr(snapshot, "position", None)
        if position is None:
            return None
        cx, cy = position
        rivals_present = any(
            other_id != agent_id
            and getattr(other, "position", None) == position
            and self.should_avoid(
                world,
                agent_id,
                other_id,
                relationship_view=relationship_view,
                dto_world=dto_world,
            )
            for other_id, other in self._iter_agent_snapshots(world, dto_world)
        )
        if not rivals_present:
            return None

        grid_size = getattr(self.config.world, "grid_size", (48, 48))
        width, height = int(grid_size[0]), int(grid_size[1])
        occupied_positions = {
            getattr(agent, "position", None)
            for _, agent in self._iter_agent_snapshots(world, dto_world)
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
        self,
        world: WorldState,
        agent_id: str,
        object_id: str,
        *,
        queue_view: object,
        relationship_view: object,
        dto_world: DTOWorldView | None,
    ) -> bool:
        active = queue_view.active_agent(object_id)
        if (
            active
            and active != agent_id
            and self.should_avoid(
                world,
                agent_id,
                active,
                relationship_view=relationship_view,
                dto_world=dto_world,
            )
        ):
            return True
        queue = queue_view.queue_snapshot(object_id)
        for rival_id in queue:
            if rival_id == agent_id:
                continue
            if self.should_avoid(
                world,
                agent_id,
                rival_id,
                relationship_view=relationship_view,
                dto_world=dto_world,
            ):
                return True
        return False

    def _plan_meal(
        self,
        world: WorldState,
        agent_id: str,
        *,
        queue_view: object,
        relationship_view: object,
        dto_world: DTOWorldView | None,
    ) -> AgentIntent | None:
        fridge_id = self._find_object_of_type(world, "fridge")
        stove_id = self._find_object_of_type(world, "stove")
        if fridge_id:
            fridge = world.objects.get(fridge_id)
            if (
                fridge
                and fridge.stock.get("meals", 0) > 0
                and not self._rivals_in_queue(
                    world,
                    agent_id,
                    fridge_id,
                    queue_view=queue_view,
                    relationship_view=relationship_view,
                    dto_world=dto_world,
                )
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
                and not self._rivals_in_queue(
                    world,
                    agent_id,
                    stove_id,
                    queue_view=queue_view,
                    relationship_view=relationship_view,
                    dto_world=dto_world,
                )
            ):
                self.pending[agent_id] = {
                    "object_id": stove_id,
                    "affordance_id": "cook_meal",
                }
                return AgentIntent(kind="request", object_id=stove_id)
        return None

    def _find_object_of_type(
        self, world: WorldState, object_type: str
    ) -> str | None:
        # TODO(WP3C): expose object roster via DTO to remove this legacy fallback.
        for object_id, obj in world.objects.items():
            if obj.object_type == object_type:
                return object_id
        return None

    def _behavior_bias(self, snapshot: object, key: str, default: float = 1.0) -> float:
        if not self._personality_bias_enabled:
            return default
        profile_name = getattr(snapshot, "personality_profile", None)
        if not profile_name:
            return default
        try:
            profile = PersonalityProfiles.get(str(profile_name))
        except KeyError:
            return default
        value = profile.behaviour_bias.get(key, default)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return default
        if numeric <= 0.0:
            return default
        return max(0.1, min(5.0, numeric))

    def _need_multiplier(self, snapshot: object, need: str) -> float:
        if not self._need_scaling_enabled:
            return 1.0
        profile_name = getattr(snapshot, "personality_profile", None)
        if not profile_name:
            return 1.0
        try:
            profile = PersonalityProfiles.get(str(profile_name))
        except KeyError:
            return 1.0
        try:
            raw = profile.need_multipliers.get(need, 1.0)
            multiplier = float(raw)
        except (TypeError, ValueError):
            return 1.0
        if multiplier <= 0.0:
            return 1.0
        return max(0.1, min(5.0, multiplier))

    def _need_threshold(self, snapshot: object, need: str, base: float) -> float:
        multiplier = self._need_multiplier(snapshot, need)
        threshold = base * multiplier
        return max(0.0, min(1.0, threshold))

    def should_avoid(
        self,
        world: WorldState,
        agent_id: str,
        other_id: str,
        *,
        dto_world: DTOWorldView | None = None,
        relationship_view: object | None = None,
    ) -> bool:
        snapshot = self._agent_snapshot(world, agent_id, dto_world)
        view = relationship_view if relationship_view is not None else (
            dto_world if dto_world is not None else world
        )
        if snapshot is None:
            checker = getattr(view, "rivalry_should_avoid", None)
            if callable(checker):
                return bool(checker(agent_id, other_id))
            return world.rivalry_should_avoid(agent_id, other_id)
        threshold = self._avoid_threshold_base
        if self._personality_bias_enabled:
            bias = self._behavior_bias(snapshot, "conflict_tolerance")
            if bias != 1.0:
                threshold = threshold / bias if bias > 0.0 else threshold
                threshold = max(0.0, min(1.0, threshold))
        rivalry_getter = getattr(view, "rivalry_value", None)
        if callable(rivalry_getter):
            try:
                rivalry_value = float(rivalry_getter(agent_id, other_id))
            except Exception:  # pragma: no cover - defensive fallback
                rivalry_value = float(world.rivalry_value(agent_id, other_id))
        else:
            rivalry_value = world.rivalry_value(agent_id, other_id)
        return rivalry_value >= threshold

    # ------------------------------------------------------------------
    # DTO helper views
    # ------------------------------------------------------------------
    def _queue_view(
        self,
        world: WorldState,
        dto_world: DTOWorldView | None,
    ) -> object:
        if dto_world is not None:
            return dto_world.queue_manager
        return world.queue_manager

    def _running_affordances(
        self,
        world: WorldState,
        dto_world: DTOWorldView | None,
    ) -> Mapping[str, Any]:
        if dto_world is not None:
            running = dto_world.affordance_runtime.running_affordances
            if isinstance(running, Mapping):
                return running
        runtime = getattr(world, "affordance_runtime", None)
        if runtime is not None:
            mapping = getattr(runtime, "running_affordances", {})
            if isinstance(mapping, Mapping):
                return mapping
        return {}

    def _relationship_view(
        self,
        world: WorldState,
        dto_world: DTOWorldView | None,
    ) -> object:
        return dto_world if dto_world is not None else world

    def _current_tick(
        self,
        world: WorldState,
        dto_world: DTOWorldView | None,
    ) -> int:
        if dto_world is not None:
            return int(dto_world.tick)
        return int(getattr(world, "tick", 0))

    def _agent_snapshot(
        self,
        world: WorldState,
        agent_id: str,
        dto_world: DTOWorldView | None,
    ) -> object | None:
        if dto_world is not None:
            snapshot = dto_world.agent_snapshot(agent_id)
            if snapshot is not None:
                return snapshot
        agents = getattr(world, "agents", None)
        if agents is None:
            return None
        getter = getattr(agents, "get", None)
        if callable(getter):
            return getter(agent_id)
        return None

    def _iter_agent_snapshots(
        self,
        world: WorldState,
        dto_world: DTOWorldView | None,
    ) -> Iterable[tuple[str, object]]:
        if dto_world is not None:
            yield from dto_world.iter_agent_snapshots()
            return
        agents = getattr(world, "agents", None)
        if agents is None:
            return
        items = getattr(agents, "items", None)
        if callable(items):
            yield from items()


def build_behavior(config: SimulationConfig) -> BehaviorController:
    return ScriptedBehavior(config)

"""Grid world representation and affordance integration."""

from __future__ import annotations

import random
from collections import deque
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from townlet.agents.models import Personality
from townlet.agents.relationship_modifiers import (
    RelationshipDelta,
    RelationshipEvent,
    apply_personality_modifiers,
)
from townlet.config import EmploymentConfig, SimulationConfig
from townlet.config.affordance_manifest import (
    AffordanceManifestError,
    load_affordance_manifest,
)
from townlet.observations.embedding import EmbeddingAllocator
from townlet.telemetry.relationship_metrics import RelationshipChurnAccumulator
from townlet.world.queue_manager import QueueManager
from townlet.world.relationships import RelationshipLedger, RelationshipParameters
from townlet.world.rivalry import RivalryLedger, RivalryParameters


def _default_personality() -> Personality:
    """Provide a neutral personality for agents lacking explicit traits."""

    return Personality(extroversion=0.0, forgiveness=0.0, ambition=0.0)


@dataclass
class AgentSnapshot:
    """Minimal agent view used for scaffolding."""

    agent_id: str
    position: tuple[int, int]
    needs: dict[str, float]
    wallet: float = 0.0
    personality: Personality = field(default_factory=_default_personality)
    inventory: dict[str, int] = field(default_factory=dict)
    job_id: str | None = None
    on_shift: bool = False
    lateness_counter: int = 0
    last_late_tick: int = -1
    shift_state: str = "pre_shift"
    late_ticks_today: int = 0
    attendance_ratio: float = 0.0
    absent_shifts_7d: int = 0
    wages_withheld: float = 0.0
    exit_pending: bool = False
    last_action_id: str = ""
    last_action_success: bool = False
    last_action_duration: int = 0
    episode_tick: int = 0


@dataclass
class InteractiveObject:
    """Represents an interactive world object with optional occupancy."""

    object_id: str
    object_type: str
    occupied_by: str | None = None
    stock: dict[str, int] = field(default_factory=dict)
    position: tuple[int, int] | None = None


@dataclass
class RunningAffordance:
    """Tracks an affordance currently executing on an object."""

    agent_id: str
    affordance_id: str
    duration_remaining: int
    effects: dict[str, float]


@dataclass
class AffordanceSpec:
    """Static affordance definition loaded from configuration."""

    affordance_id: str
    object_type: str
    duration: int
    effects: dict[str, float]
    preconditions: list[str] = field(default_factory=list)
    hooks: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class WorldState:
    """Holds mutable world state for the simulation tick."""

    config: SimulationConfig
    agents: dict[str, AgentSnapshot] = field(default_factory=dict)
    tick: int = 0
    queue_manager: QueueManager = field(init=False)
    embedding_allocator: EmbeddingAllocator = field(init=False)
    _active_reservations: dict[str, str] = field(init=False, default_factory=dict)
    objects: dict[str, InteractiveObject] = field(init=False, default_factory=dict)
    affordances: dict[str, AffordanceSpec] = field(init=False, default_factory=dict)
    _running_affordances: dict[str, RunningAffordance] = field(
        init=False, default_factory=dict
    )
    _pending_events: dict[int, list[dict[str, Any]]] = field(
        init=False, default_factory=dict
    )
    store_stock: dict[str, dict[str, int]] = field(init=False, default_factory=dict)
    _job_keys: list[str] = field(init=False, default_factory=list)
    _employment_state: dict[str, dict[str, Any]] = field(
        init=False, default_factory=dict
    )
    _employment_exit_queue: list[str] = field(init=False, default_factory=list)
    _employment_exits_today: int = field(init=False, default=0)
    _employment_exit_queue_timestamps: dict[str, int] = field(
        init=False, default_factory=dict
    )
    _employment_manual_exits: set[str] = field(init=False, default_factory=set)

    _rivalry_ledgers: dict[str, RivalryLedger] = field(init=False, default_factory=dict)
    _relationship_ledgers: dict[str, RelationshipLedger] = field(
        init=False, default_factory=dict
    )
    _relationship_churn: RelationshipChurnAccumulator = field(init=False)
    _rivalry_events: deque[dict[str, Any]] = field(init=False, default_factory=deque)
    _relationship_window_ticks: int = 600
    _recent_meal_participants: dict[str, dict[str, Any]] = field(
        init=False, default_factory=dict
    )
    _chat_events: list[dict[str, Any]] = field(init=False, default_factory=list)
    _rng_seed: Optional[int] = field(init=False, default=None)
    _rng_state: Optional[tuple[Any, ...]] = field(init=False, default=None)
    _rng: Optional[random.Random] = field(init=False, default=None, repr=False)
    _affordance_manifest_info: dict[str, object] = field(
        init=False, default_factory=dict
    )
    _objects_by_position: dict[tuple[int, int], list[str]] = field(
        init=False, default_factory=dict
    )

    @classmethod
    def from_config(
        cls,
        config: SimulationConfig,
        *,
        rng: Optional[random.Random] = None,
    ) -> "WorldState":
        """Bootstrap the initial world from config."""

        instance = cls(config=config)
        instance.attach_rng(rng or random.Random())
        return instance

    def __post_init__(self) -> None:
        self.queue_manager = QueueManager(config=self.config)
        self.embedding_allocator = EmbeddingAllocator(config=self.config)
        self._active_reservations = {}
        self.objects = {}
        self.affordances = {}
        self._running_affordances = {}
        self._pending_events = {}
        self.store_stock = {}
        self._job_keys = list(self.config.jobs.keys())
        self._employment_state = {}
        self._employment_exit_queue = []
        self._employment_exits_today = 0
        self._employment_exit_queue_timestamps = {}
        self._employment_manual_exits = set()
        self._rivalry_ledgers = {}
        self._relationship_ledgers = {}
        self._relationship_window_ticks = 600
        self._relationship_churn = RelationshipChurnAccumulator(
            window_ticks=self._relationship_window_ticks,
            max_samples=8,
        )
        self._rivalry_events = deque(maxlen=256)
        self._recent_meal_participants = {}
        self._chat_events = []
        self._load_affordance_definitions()
        self._rng_seed = None
        if self._rng is None:
            self._rng = random.Random()
        self._rng_state = self._rng.getstate()

    def apply_console(self, operations: Iterable[Any]) -> None:
        """Apply console operations before the tick sequence runs."""
        for operation in operations:
            # TODO(@townlet): Implement concrete console op handlers.
            _ = operation

    def attach_rng(self, rng: random.Random) -> None:
        """Attach a deterministic RNG used for world-level randomness."""

        self._rng = rng
        self._rng_state = rng.getstate()

    @property
    def rng(self) -> random.Random:
        if self._rng is None:
            self._rng = random.Random()
        return self._rng

    def get_rng_state(self) -> tuple[Any, ...]:
        return self.rng.getstate()

    def set_rng_state(self, state: tuple[Any, ...]) -> None:
        self.rng.setstate(state)
        self._rng_state = state

    def register_object(
        self,
        *,
        object_id: str,
        object_type: str,
        position: tuple[int, int] | None = None,
    ) -> None:
        """Register or update an interactive object in the world."""

        existing = self.objects.get(object_id)
        if existing is not None and existing.position is not None:
            self._unindex_object_position(object_id, existing.position)

        obj = InteractiveObject(
            object_id=object_id,
            object_type=object_type,
            position=position,
        )
        if object_type == "fridge":
            obj.stock["meals"] = 5
        if object_type == "stove":
            obj.stock["raw_ingredients"] = 3
        if object_type == "bed":
            obj.stock["sleep_slots"] = 1
        self.objects[object_id] = obj
        self.store_stock[object_id] = obj.stock
        if obj.position is not None:
            self._index_object_position(object_id, obj.position)

    def _index_object_position(self, object_id: str, position: tuple[int, int]) -> None:
        bucket = self._objects_by_position.setdefault(position, [])
        if object_id not in bucket:
            bucket.append(object_id)

    def _unindex_object_position(
        self, object_id: str, position: tuple[int, int]
    ) -> None:
        bucket = self._objects_by_position.get(position)
        if not bucket:
            return
        try:
            bucket.remove(object_id)
        except ValueError:
            return
        if not bucket:
            self._objects_by_position.pop(position, None)

    def register_affordance(
        self,
        *,
        affordance_id: str,
        object_type: str,
        duration: int,
        effects: dict[str, float],
        preconditions: Iterable[str] | None = None,
        hooks: Mapping[str, Iterable[str]] | None = None,
    ) -> None:
        """Register an affordance available in the world."""
        self.affordances[affordance_id] = AffordanceSpec(
            affordance_id=affordance_id,
            object_type=object_type,
            duration=duration,
            effects=dict(effects),
            preconditions=list(preconditions or []),
            hooks={key: list(values) for key, values in (hooks or {}).items()},
        )

    def apply_actions(self, actions: dict[str, Any]) -> None:
        """Apply agent actions for the current tick."""
        current_tick = self.tick
        for agent_id, action in actions.items():
            snapshot = self.agents.get(agent_id)
            if snapshot is None:
                continue
            if not isinstance(action, dict):
                continue

            kind = action.get("kind")
            object_id = action.get("object")
            action_success = False
            action_duration = int(action.get("duration", 1))

            if kind == "request" and object_id:
                granted = self.queue_manager.request_access(
                    object_id, agent_id, current_tick
                )
                self._sync_reservation(object_id)
                if not granted and action.get("blocked"):
                    self._handle_blocked(object_id, current_tick)
                action_success = bool(granted)
            elif kind == "move" and action.get("position"):
                target_pos = tuple(action["position"])
                snapshot.position = target_pos
                action_success = True
            elif kind == "start" and object_id:
                affordance_id = action.get("affordance")
                if affordance_id:
                    action_success = self._start_affordance(
                        agent_id, object_id, affordance_id
                    )
            elif kind == "release" and object_id:
                success = bool(action.get("success", True))
                running = self._running_affordances.pop(object_id, None)
                if running is not None and success:
                    self._apply_affordance_effects(running.agent_id, running.effects)
                    self._emit_event(
                        "affordance_finish",
                        {
                            "agent_id": running.agent_id,
                            "object_id": object_id,
                            "affordance_id": running.affordance_id,
                        },
                    )
                    obj = self.objects.get(object_id)
                    if obj is not None:
                        obj.occupied_by = None
                self.queue_manager.release(
                    object_id, agent_id, current_tick, success=success
                )
                self._sync_reservation(object_id)
                if not success:
                    if running is not None:
                        self._emit_event(
                            "affordance_fail",
                            {
                                "agent_id": agent_id,
                                "object_id": object_id,
                                "affordance_id": running.affordance_id,
                            },
                        )
                    self._running_affordances.pop(object_id, None)
                action_success = success
            elif kind == "blocked" and object_id:
                self._handle_blocked(object_id, current_tick)
                action_success = False
            # TODO(@townlet): Update agent snapshot based on outcomes.

            if kind:
                snapshot.last_action_id = str(kind)
                snapshot.last_action_success = action_success
                snapshot.last_action_duration = action_duration

    def resolve_affordances(self, current_tick: int) -> None:
        """Resolve queued affordances and hooks."""
        # Tick the queue manager so cooldowns expire and fairness checks apply.
        self.queue_manager.on_tick(current_tick)
        # Automatically monitor stalled queues and trigger ghost steps when required.
        for object_id, occupant in list(self._active_reservations.items()):
            queue = self.queue_manager.queue_snapshot(object_id)
            if not queue:
                continue
            if self.queue_manager.record_blocked_attempt(object_id):
                waiting = self.queue_manager.queue_snapshot(object_id)
                rival = waiting[0] if waiting else None
                self.queue_manager.release(
                    object_id, occupant, current_tick, success=False
                )
                self.queue_manager.requeue_to_tail(
                    object_id, occupant, current_tick
                )
                if rival is not None:
                    self._record_queue_conflict(
                        object_id=object_id,
                        actor=occupant,
                        rival=rival,
                        reason="ghost_step",
                        queue_length=len(waiting),
                        intensity=None,
                    )
                self._running_affordances.pop(object_id, None)
                self._sync_reservation(object_id)
        # TODO(@townlet): Integrate with affordance registry and hook dispatch.

        for object_id, running in list(self._running_affordances.items()):
            running.duration_remaining -= 1
            if running.duration_remaining <= 0:
                self._apply_affordance_effects(running.agent_id, running.effects)
                self._running_affordances.pop(object_id, None)
                waiting = self.queue_manager.queue_snapshot(object_id)
                self.queue_manager.release(
                    object_id, running.agent_id, current_tick, success=True
                )
                self._sync_reservation(object_id)
                if waiting:
                    next_agent = waiting[0]
                    self._record_queue_conflict(
                        object_id=object_id,
                        actor=running.agent_id,
                        rival=next_agent,
                        reason="handover",
                        queue_length=len(waiting),
                        intensity=0.5,
                    )
                self._emit_event(
                    "affordance_finish",
                    {
                        "agent_id": running.agent_id,
                        "object_id": object_id,
                        "affordance_id": running.affordance_id,
                    },
                )

        self._apply_need_decay()

    def snapshot(self) -> dict[str, AgentSnapshot]:
        """Return a shallow copy of the agent dictionary for observers."""
        return dict(self.agents)

    def local_view(
        self,
        agent_id: str,
        radius: int,
        *,
        include_agents: bool = True,
        include_objects: bool = True,
    ) -> dict[str, Any]:
        """Return local neighborhood information for observation builders."""

        snapshot = self.agents.get(agent_id)
        if snapshot is None:
            return {
                "center": None,
                "radius": radius,
                "tiles": [],
                "agents": [],
                "objects": [],
            }

        cx, cy = snapshot.position
        agent_lookup: dict[tuple[int, int], list[str]] = {}
        if include_agents:
            for other in self.agents.values():
                position = other.position
                agent_lookup.setdefault(position, []).append(other.agent_id)

        object_lookup: dict[tuple[int, int], list[str]] = {}
        if include_objects:
            for position, object_ids in self._objects_by_position.items():
                filtered = [obj_id for obj_id in object_ids if obj_id in self.objects]
                if filtered:
                    object_lookup[position] = filtered

        tiles: list[list[dict[str, Any]]] = []
        seen_agents: dict[str, dict[str, Any]] = {}
        seen_objects: dict[str, dict[str, Any]] = {}

        for dy in range(-radius, radius + 1):
            row: list[dict[str, Any]] = []
            for dx in range(-radius, radius + 1):
                x = cx + dx
                y = cy + dy
                position = (x, y)
                agent_ids = agent_lookup.get(position, [])
                object_ids = object_lookup.get(position, [])
                if include_agents:
                    for agent_id_at_tile in agent_ids:
                        if agent_id_at_tile == agent_id:
                            continue
                        other = self.agents.get(agent_id_at_tile)
                        if other is not None:
                            seen_agents.setdefault(
                                agent_id_at_tile,
                                {
                                    "agent_id": agent_id_at_tile,
                                    "position": other.position,
                                    "on_shift": other.on_shift,
                                },
                            )
                if include_objects:
                    for object_id in object_ids:
                        obj = self.objects.get(object_id)
                        if obj is None:
                            continue
                        seen_objects.setdefault(
                            object_id,
                            {
                                "object_id": object_id,
                                "object_type": obj.object_type,
                                "position": obj.position,
                                "occupied_by": obj.occupied_by,
                            },
                        )
                reservation_active = False
                if object_ids:
                    reservation_active = any(
                        self._active_reservations.get(object_id) is not None
                        for object_id in object_ids
                    )
                row.append(
                    {
                        "position": position,
                        "self": position == (cx, cy),
                        "agent_ids": list(agent_ids),
                        "object_ids": list(object_ids),
                        "reservation_active": reservation_active,
                    }
                )
            tiles.append(row)

        return {
            "center": (cx, cy),
            "radius": radius,
            "tiles": tiles,
            "agents": list(seen_agents.values()),
            "objects": list(seen_objects.values()),
        }

    def agent_context(self, agent_id: str) -> dict[str, object]:
        """Return scalar context fields for the requested agent."""

        snapshot = self.agents.get(agent_id)
        if snapshot is None:
            return {}
        return {
            "needs": dict(snapshot.needs),
            "wallet": snapshot.wallet,
            "lateness_counter": snapshot.lateness_counter,
            "on_shift": snapshot.on_shift,
            "attendance_ratio": snapshot.attendance_ratio,
            "wages_withheld": snapshot.wages_withheld,
            "shift_state": snapshot.shift_state,
            "last_action_id": snapshot.last_action_id,
            "last_action_success": snapshot.last_action_success,
            "last_action_duration": snapshot.last_action_duration,
            "wages_paid": self._employment_context_wages(snapshot.agent_id),
            "punctuality_bonus": self._employment_context_punctuality(
                snapshot.agent_id
            ),
        }

    @property
    def active_reservations(self) -> dict[str, str]:
        """Expose a copy of active reservations for diagnostics/tests."""
        return dict(self._active_reservations)

    def drain_events(self) -> list[dict[str, Any]]:
        """Return all pending events accumulated up to the current tick."""
        events: list[dict[str, Any]] = []
        for _, batch in sorted(self._pending_events.items()):
            events.extend(batch)
        self._pending_events.clear()
        return events

    def _record_queue_conflict(
        self,
        *,
        object_id: str,
        actor: str,
        rival: str,
        reason: str,
        queue_length: int,
        intensity: float | None = None,
    ) -> None:
        if actor == rival:
            return
        payload = {
            "object_id": object_id,
            "actor": actor,
            "rival": rival,
            "reason": reason,
            "queue_length": queue_length,
        }
        if reason == "handover":
            self.update_relationship(
                actor,
                rival,
                trust=0.05,
                familiarity=0.05,
                rivalry=-0.05,
                event="queue_polite",
            )
            self._emit_event("queue_interaction", {**payload, "variant": "handover"})
            return

        params = self.config.conflict.rivalry
        base_intensity = intensity
        if base_intensity is None:
            boost = (
                params.ghost_step_boost
                if reason == "ghost_step"
                else params.handover_boost
            )
            base_intensity = boost + params.queue_length_boost * max(
                queue_length - 1, 0
            )
        clamped_intensity = min(5.0, max(0.1, base_intensity))
        self.register_rivalry_conflict(
            actor, rival, intensity=clamped_intensity, reason=reason
        )
        self.update_relationship(
            actor,
            rival,
            rivalry=0.05 * clamped_intensity,
            event="conflict",
        )
        self._emit_event(
            "queue_conflict",
            {
                **payload,
                "intensity": clamped_intensity,
            },
        )

    def register_rivalry_conflict(
        self,
        agent_a: str,
        agent_b: str,
        *,
        intensity: float = 1.0,
        reason: str = "conflict",
    ) -> None:
        """Record a rivalry-inducing conflict between two agents.

        Both ledgers are updated symmetrically so downstream consumers can
        inspect rivalry magnitudes without having to normalise directionality.
        """
        if agent_a == agent_b:
            return
        ledger_a = self._get_rivalry_ledger(agent_a)
        ledger_b = self._get_rivalry_ledger(agent_b)
        ledger_a.apply_conflict(agent_b, intensity=intensity)
        ledger_b.apply_conflict(agent_a, intensity=intensity)
        self.update_relationship(
            agent_a,
            agent_b,
            rivalry=0.1 * intensity,
            event="conflict",
        )
        self._record_rivalry_event(
            agent_a=agent_a, agent_b=agent_b, intensity=intensity, reason=reason
        )

    def rivalry_snapshot(self) -> dict[str, dict[str, float]]:
        """Expose rivalry ledgers for telemetry/diagnostics."""
        snapshot: dict[str, dict[str, float]] = {}
        for agent_id, ledger in self._rivalry_ledgers.items():
            data = ledger.snapshot()
            if data:
                snapshot[agent_id] = data
        return snapshot

    def relationships_snapshot(self) -> dict[str, dict[str, dict[str, float]]]:
        snapshot: dict[str, dict[str, dict[str, float]]] = {}
        for agent_id, ledger in self._relationship_ledgers.items():
            data = ledger.snapshot()
            if data:
                snapshot[agent_id] = data
        return snapshot

    def relationship_tie(self, agent_id: str, other_id: str) -> RelationshipTie | None:
        """Return the current relationship tie between two agents, if any."""

        ledger = self._relationship_ledgers.get(agent_id)
        if ledger is None:
            return None
        return ledger.tie_for(other_id)

    def consume_chat_events(self) -> list[dict[str, Any]]:
        """Return chat events staged for reward calculations and clear the buffer."""

        events = list(self._chat_events)
        self._chat_events.clear()
        return events

    def rivalry_value(self, agent_id: str, other_id: str) -> float:
        """Return the rivalry score between two agents, if present."""
        ledger = self._rivalry_ledgers.get(agent_id)
        if ledger is None:
            return 0.0
        return ledger.score_for(other_id)

    def rivalry_should_avoid(self, agent_id: str, other_id: str) -> bool:
        ledger = self._rivalry_ledgers.get(agent_id)
        if ledger is None:
            return False
        return ledger.should_avoid(other_id)

    def rivalry_top(self, agent_id: str, limit: int) -> list[tuple[str, float]]:
        ledger = self._rivalry_ledgers.get(agent_id)
        if ledger is None:
            return []
        return ledger.top_rivals(limit)

    def consume_rivalry_events(self) -> list[dict[str, Any]]:
        """Return rivalry events recorded since the last call."""

        if not self._rivalry_events:
            return []
        events = list(self._rivalry_events)
        self._rivalry_events.clear()
        return events

    def _record_rivalry_event(
        self, *, agent_a: str, agent_b: str, intensity: float, reason: str
    ) -> None:
        self._rivalry_events.append(
            {
                "tick": int(self.tick),
                "agent_a": agent_a,
                "agent_b": agent_b,
                "intensity": float(intensity),
                "reason": reason,
            }
        )

    def _get_rivalry_ledger(self, agent_id: str) -> RivalryLedger:
        ledger = self._rivalry_ledgers.get(agent_id)
        if ledger is None:
            ledger = RivalryLedger(
                owner_id=agent_id,
                params=self._rivalry_parameters(),
                eviction_hook=self._record_relationship_eviction,
            )
            self._rivalry_ledgers[agent_id] = ledger
        else:
            ledger.eviction_hook = self._record_relationship_eviction
        return ledger

    def _get_relationship_ledger(self, agent_id: str) -> RelationshipLedger:
        ledger = self._relationship_ledgers.get(agent_id)
        if ledger is None:
            ledger = RelationshipLedger(
                owner_id=agent_id,
                params=self._relationship_parameters(),
                eviction_hook=self._record_relationship_eviction,
            )
            self._relationship_ledgers[agent_id] = ledger
        else:
            ledger.set_eviction_hook(
                owner_id=agent_id,
                hook=self._record_relationship_eviction,
            )
        return ledger

    def _relationship_parameters(self) -> RelationshipParameters:
        return RelationshipParameters(max_edges=self.config.conflict.rivalry.max_edges)

    def _personality_for(self, agent_id: str) -> Personality:
        snapshot = self.agents.get(agent_id)
        if snapshot is None or snapshot.personality is None:
            return _default_personality()
        return snapshot.personality

    def _apply_relationship_delta(
        self,
        owner_id: str,
        other_id: str,
        *,
        delta: RelationshipDelta,
        event: RelationshipEvent,
    ) -> None:
        ledger = self._get_relationship_ledger(owner_id)
        adjusted = apply_personality_modifiers(
            delta=delta,
            personality=self._personality_for(owner_id),
            event=event,
            enabled=bool(self.config.features.relationship_modifiers),
        )
        ledger.apply_delta(
            other_id,
            trust=adjusted.trust,
            familiarity=adjusted.familiarity,
            rivalry=adjusted.rivalry,
        )

    def _rivalry_parameters(self) -> RivalryParameters:
        cfg = self.config.conflict.rivalry
        return RivalryParameters(
            increment_per_conflict=cfg.increment_per_conflict,
            decay_per_tick=cfg.decay_per_tick,
            min_value=cfg.min_value,
            max_value=cfg.max_value,
            avoid_threshold=cfg.avoid_threshold,
            eviction_threshold=cfg.eviction_threshold,
            max_edges=cfg.max_edges,
        )

    def _decay_rivalry_ledgers(self) -> None:
        if not self._rivalry_ledgers:
            return
        empty_agents: list[str] = []
        for agent_id, ledger in self._rivalry_ledgers.items():
            ledger.decay(ticks=1)
            if not ledger.snapshot():
                empty_agents.append(agent_id)
        for agent_id in empty_agents:
            self._rivalry_ledgers.pop(agent_id, None)
        self._decay_relationship_ledgers()

    def _decay_relationship_ledgers(self) -> None:
        if not self._relationship_ledgers:
            return
        empty_agents: list[str] = []
        for agent_id, ledger in self._relationship_ledgers.items():
            ledger.decay()
            if not ledger.snapshot():
                empty_agents.append(agent_id)
        for agent_id in empty_agents:
            self._relationship_ledgers.pop(agent_id, None)

    def _record_relationship_eviction(
        self, owner_id: str, other_id: str, reason: str
    ) -> None:
        self._relationship_churn.record_eviction(
            tick=self.tick,
            owner_id=owner_id,
            evicted_id=other_id,
            reason=reason,
        )

    def relationship_metrics_snapshot(self) -> dict[str, object]:
        return self._relationship_churn.latest_payload()

    def load_relationship_snapshot(
        self,
        snapshot: dict[str, dict[str, dict[str, float]]],
    ) -> None:
        """Restore relationship ledgers from persisted snapshot data."""

        self._relationship_ledgers.clear()
        for owner_id, edges in snapshot.items():
            ledger = RelationshipLedger(
                owner_id=owner_id,
                params=self._relationship_parameters(),
            )
            ledger.inject(edges)
            ledger.set_eviction_hook(
                owner_id=owner_id,
                hook=self._record_relationship_eviction,
            )
            self._relationship_ledgers[owner_id] = ledger

    def update_relationship(
        self,
        agent_a: str,
        agent_b: str,
        *,
        trust: float = 0.0,
        familiarity: float = 0.0,
        rivalry: float = 0.0,
        event: RelationshipEvent = "generic",
    ) -> None:
        if agent_a == agent_b:
            return
        delta = RelationshipDelta(trust=trust, familiarity=familiarity, rivalry=rivalry)
        self._apply_relationship_delta(agent_a, agent_b, delta=delta, event=event)
        self._apply_relationship_delta(agent_b, agent_a, delta=delta, event=event)

    def record_chat_success(self, speaker: str, listener: str, quality: float) -> None:
        clipped_quality = max(0.0, min(1.0, quality))
        self.update_relationship(
            speaker,
            listener,
            trust=0.05 * clipped_quality,
            familiarity=0.10 * clipped_quality,
            event="chat_success",
        )
        self._chat_events.append(
            {
                "event": "chat_success",
                "speaker": speaker,
                "listener": listener,
                "quality": clipped_quality,
                "tick": self.tick,
            }
        )
        self._emit_event(
            "chat_success",
            {
                "speaker": speaker,
                "listener": listener,
                "quality": clipped_quality,
            },
        )

    def record_chat_failure(self, speaker: str, listener: str) -> None:
        self.update_relationship(
            speaker,
            listener,
            trust=0.0,
            familiarity=-0.05,
            rivalry=0.05,
            event="chat_failure",
        )
        self._chat_events.append(
            {
                "event": "chat_failure",
                "speaker": speaker,
                "listener": listener,
                "tick": self.tick,
            }
        )
        self._emit_event(
            "chat_failure",
            {
                "speaker": speaker,
                "listener": listener,
            },
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _sync_reservation(self, object_id: str) -> None:
        active = self.queue_manager.active_agent(object_id)
        obj = self.objects.get(object_id)
        if active is None:
            self._active_reservations.pop(object_id, None)
            if obj is not None:
                obj.occupied_by = None
        else:
            self._active_reservations[object_id] = active
            if obj is not None:
                obj.occupied_by = active

    def _handle_blocked(self, object_id: str, tick: int) -> None:
        if self.queue_manager.record_blocked_attempt(object_id):
            occupant = self.queue_manager.active_agent(object_id)
            if occupant is not None:
                self.queue_manager.release(object_id, occupant, tick, success=False)
            self._running_affordances.pop(object_id, None)
            self._sync_reservation(object_id)

    def _start_affordance(
        self, agent_id: str, object_id: str, affordance_id: str
    ) -> bool:
        if self.queue_manager.active_agent(object_id) != agent_id:
            return False
        if object_id in self._running_affordances:
            return False
        obj = self.objects.get(object_id)
        spec = self.affordances.get(affordance_id)
        if obj is None or spec is None:
            return False
        if spec.object_type != obj.object_type:
            return False

        self._running_affordances[object_id] = RunningAffordance(
            agent_id=agent_id,
            affordance_id=affordance_id,
            duration_remaining=max(spec.duration, 1),
            effects=spec.effects,
        )
        obj.occupied_by = agent_id
        self._handle_affordance_economy_start(agent_id, object_id, spec)
        self._emit_event(
            "affordance_start",
            {
                "agent_id": agent_id,
                "object_id": object_id,
                "affordance_id": affordance_id,
                "duration": spec.duration,
            },
        )
        return True

    def _apply_affordance_effects(
        self, agent_id: str, effects: dict[str, float]
    ) -> None:
        snapshot = self.agents.get(agent_id)
        if snapshot is None:
            return
        for key, delta in effects.items():
            if key in snapshot.needs:
                new_value = snapshot.needs[key] + delta
                snapshot.needs[key] = max(0.0, min(1.0, new_value))
            elif key == "money":
                snapshot.wallet += delta

    def _emit_event(self, event: str, payload: dict[str, Any]) -> None:
        events = self._pending_events.setdefault(self.tick, [])
        events.append({"event": event, "tick": self.tick, **payload})

    def _load_affordance_definitions(self) -> None:
        manifest_path = Path(self.config.affordances.affordances_file).expanduser()
        try:
            manifest = load_affordance_manifest(manifest_path)
        except FileNotFoundError as error:
            raise RuntimeError(
                f"Affordance manifest not found at {manifest_path}."
            ) from error
        except AffordanceManifestError as error:
            raise RuntimeError(
                f"Failed to load affordance manifest {manifest_path}: {error}"
            ) from error

        self.objects.clear()
        self.affordances.clear()
        self.store_stock.clear()

        for entry in manifest.objects:
            self.register_object(
                object_id=entry.object_id,
                object_type=entry.object_type,
                position=getattr(entry, "position", None),
            )
            if entry.stock:
                obj = self.objects.get(entry.object_id)
                if obj is not None:
                    obj.stock.update(entry.stock)
                    self.store_stock[entry.object_id] = obj.stock

        for entry in manifest.affordances:
            self.register_affordance(
                affordance_id=entry.affordance_id,
                object_type=entry.object_type,
                duration=entry.duration,
                effects=entry.effects,
                preconditions=entry.preconditions,
                hooks=entry.hooks,
            )

        self._affordance_manifest_info = {
            "path": str(manifest.path),
            "checksum": manifest.checksum,
            "object_count": manifest.object_count,
            "affordance_count": manifest.affordance_count,
        }
        self._assign_jobs_to_agents()

    def affordance_manifest_metadata(self) -> dict[str, object]:
        """Expose manifest metadata (path, checksum, counts) for telemetry."""

        return dict(self._affordance_manifest_info)

    def find_nearest_object_of_type(
        self, object_type: str, origin: tuple[int, int]
    ) -> tuple[int, int] | None:
        targets = [
            obj.position
            for obj in self.objects.values()
            if obj.object_type == object_type and obj.position is not None
        ]
        if not targets:
            return None
        ox, oy = origin
        closest = min(targets, key=lambda pos: (pos[0] - ox) ** 2 + (pos[1] - oy) ** 2)
        return closest

    def _apply_need_decay(self) -> None:
        decay_rates = self.config.rewards.decay_rates
        for snapshot in self.agents.values():
            for need, decay in decay_rates.items():
                if need in snapshot.needs:
                    snapshot.needs[need] = max(0.0, snapshot.needs[need] - decay)
        self._decay_rivalry_ledgers()
        self._apply_job_state()
        self._update_basket_metrics()

    def _assign_jobs_to_agents(self) -> None:
        if not self._job_keys:
            return
        for index, snapshot in enumerate(self.agents.values()):
            if snapshot.job_id is None or snapshot.job_id not in self.config.jobs:
                snapshot.job_id = self._job_keys[index % len(self._job_keys)]
            snapshot.inventory.setdefault("meals_cooked", 0)
            snapshot.inventory.setdefault("meals_consumed", 0)
            snapshot.inventory.setdefault("wages_earned", 0)

    def _apply_job_state(self) -> None:
        if self.config.employment.enforce_job_loop:
            self._apply_job_state_enforced()
        else:
            self._apply_job_state_legacy()

    def _apply_job_state_legacy(self) -> None:
        jobs = self.config.jobs
        default_job_id = self._job_keys[0] if self._job_keys else None
        for snapshot in self.agents.values():
            job_id = snapshot.job_id
            if job_id is None or job_id not in jobs:
                if default_job_id is None:
                    snapshot.on_shift = False
                    continue
                job_id = default_job_id
                snapshot.job_id = job_id
            spec = jobs[job_id]
            start = spec.start_tick
            end = spec.end_tick or spec.start_tick
            wage_rate = spec.wage_rate or self.config.economy.get("wage_income", 0.0)
            lateness_penalty = spec.lateness_penalty
            location = spec.location
            required_position = tuple(location) if location else (0, 0)

            if start <= self.tick <= end:
                snapshot.on_shift = True
                if self.tick == start and snapshot.position != required_position:
                    snapshot.lateness_counter += 1
                    if snapshot.last_late_tick != self.tick:
                        snapshot.wallet = max(0.0, snapshot.wallet - lateness_penalty)
                        snapshot.last_late_tick = self.tick
                        self._emit_event(
                            "job_late",
                            {
                                "agent_id": snapshot.agent_id,
                                "job_id": job_id,
                                "tick": self.tick,
                            },
                        )
                if location and tuple(location) != snapshot.position:
                    snapshot.on_shift = False
                else:
                    snapshot.wallet += wage_rate
                    snapshot.inventory["wages_earned"] = (
                        snapshot.inventory.get("wages_earned", 0) + 1
                    )
            else:
                snapshot.on_shift = False

    def _apply_job_state_enforced(self) -> None:
        jobs = self.config.jobs
        default_job_id = self._job_keys[0] if self._job_keys else None
        employment_cfg = self.config.employment
        arrival_buffer = self.config.behavior.job_arrival_buffer
        ticks_per_day = max(1, employment_cfg.exit_review_window)
        seven_day_window = ticks_per_day * 7

        for snapshot in self.agents.values():
            ctx = self._get_employment_context(snapshot.agent_id)
            # Reset daily counters when day changes.
            current_day = self.tick // ticks_per_day
            if ctx["current_day"] != current_day:
                ctx["current_day"] = current_day
                ctx["late_ticks"] = 0
                ctx["wages_paid"] = 0.0
                snapshot.late_ticks_today = 0

            job_id = snapshot.job_id
            if job_id is None or job_id not in jobs:
                if default_job_id is None:
                    self._employment_idle_state(snapshot, ctx)
                    continue
                job_id = default_job_id
                snapshot.job_id = job_id

            spec = jobs[job_id]
            start = spec.start_tick
            end = spec.end_tick or spec.start_tick
            if end < start:
                end = start
            wage_rate = spec.wage_rate or self.config.economy.get("wage_income", 0.0)
            lateness_penalty = spec.lateness_penalty
            required_position = tuple(spec.location) if spec.location else None
            at_required_location = (
                required_position is None or snapshot.position == required_position
            )

            # Maintenance: drop stale absence events beyond rolling window.
            while ctx["absence_events"] and (
                self.tick - ctx["absence_events"][0] > seven_day_window
            ):
                ctx["absence_events"].popleft()
            snapshot.absent_shifts_7d = len(ctx["absence_events"])

            if self.tick < start - arrival_buffer:
                self._employment_idle_state(snapshot, ctx)
                continue

            if start - arrival_buffer <= self.tick < start:
                self._employment_prepare_state(snapshot, ctx)
                continue

            if start <= self.tick <= end:
                self._employment_begin_shift(ctx, start, end)
                state = self._employment_determine_state(
                    ctx=ctx,
                    tick=self.tick,
                    start=start,
                    at_required_location=at_required_location,
                    employment_cfg=employment_cfg,
                )
                self._employment_apply_state_effects(
                    snapshot=snapshot,
                    ctx=ctx,
                    state=state,
                    at_required_location=at_required_location,
                    wage_rate=wage_rate,
                    lateness_penalty=lateness_penalty,
                    employment_cfg=employment_cfg,
                )
                continue

            # Post-shift window.
            self._employment_finalize_shift(
                snapshot=snapshot,
                ctx=ctx,
                employment_cfg=employment_cfg,
                job_id=job_id,
            )

    # ------------------------------------------------------------------
    # Employment helpers
    # ------------------------------------------------------------------
    def _employment_context_defaults(self) -> dict[str, Any]:
        window = max(1, self.config.employment.attendance_window)
        return {
            "state": "pre_shift",
            "late_penalty_applied": False,
            "absence_penalty_applied": False,
            "late_event_emitted": False,
            "absence_event_emitted": False,
            "departure_event_emitted": False,
            "late_help_event_emitted": False,
            "took_shift_event_emitted": False,
            "shift_started_tick": None,
            "shift_end_tick": None,
            "last_present_tick": None,
            "ever_on_time": False,
            "scheduled_ticks": 0,
            "on_time_ticks": 0,
            "late_ticks": 0,
            "wages_paid": 0.0,
            "attendance_samples": deque(maxlen=window),
            "absence_events": deque(),
            "shift_outcome_recorded": False,
            "current_day": -1,
            "late_counter_recorded": False,
        }

    def _get_employment_context(self, agent_id: str) -> dict[str, Any]:
        ctx = self._employment_state.get(agent_id)
        if ctx is None or ctx.get("attendance_samples") is None:
            ctx = self._employment_context_defaults()
            self._employment_state[agent_id] = ctx
        # Resize deque if window changed via config reload.
        window = max(1, self.config.employment.attendance_window)
        samples: deque[float] = ctx["attendance_samples"]
        if samples.maxlen != window:
            new_samples: deque[float] = deque(samples, maxlen=window)
            ctx["attendance_samples"] = new_samples
        return ctx

    def _employment_context_wages(self, agent_id: str) -> float:
        ctx = self._employment_state.get(agent_id)
        if not ctx:
            return 0.0
        return float(ctx.get("wages_paid", 0.0))

    def _employment_context_punctuality(self, agent_id: str) -> float:
        ctx = self._employment_state.get(agent_id)
        if not ctx:
            return 0.0
        scheduled = max(1, int(ctx.get("scheduled_ticks", 0)))
        on_time = float(ctx.get("on_time_ticks", 0))
        value = on_time / scheduled
        return max(0.0, min(1.0, value))

    def _employment_idle_state(
        self, snapshot: AgentSnapshot, ctx: dict[str, Any]
    ) -> None:
        if ctx["state"] != "pre_shift":
            ctx["state"] = "pre_shift"
            ctx["late_penalty_applied"] = False
            ctx["absence_penalty_applied"] = False
            ctx["late_event_emitted"] = False
            ctx["absence_event_emitted"] = False
            ctx["departure_event_emitted"] = False
            ctx["late_help_event_emitted"] = False
            ctx["took_shift_event_emitted"] = False
            ctx["shift_started_tick"] = None
            ctx["shift_end_tick"] = None
            ctx["last_present_tick"] = None
            ctx["ever_on_time"] = False
            ctx["scheduled_ticks"] = 0
            ctx["on_time_ticks"] = 0
            ctx["shift_outcome_recorded"] = False
        snapshot.shift_state = "pre_shift"
        snapshot.on_shift = False

    def _employment_prepare_state(
        self, snapshot: AgentSnapshot, ctx: dict[str, Any]
    ) -> None:
        ctx["state"] = "await_start"
        snapshot.shift_state = "await_start"
        snapshot.on_shift = False

    def _employment_begin_shift(
        self, ctx: dict[str, Any], start: int, end: int
    ) -> None:
        if ctx["shift_started_tick"] != start:
            ctx["shift_started_tick"] = start
            ctx["shift_end_tick"] = end
            ctx["scheduled_ticks"] = max(1, end - start + 1)
            ctx["on_time_ticks"] = 0
            ctx["late_ticks"] = 0
            ctx["wages_paid"] = 0.0
            ctx["late_penalty_applied"] = False
            ctx["absence_penalty_applied"] = False
            ctx["late_event_emitted"] = False
            ctx["absence_event_emitted"] = False
            ctx["departure_event_emitted"] = False
            ctx["late_help_event_emitted"] = False
            ctx["took_shift_event_emitted"] = False
            ctx["shift_outcome_recorded"] = False
            ctx["ever_on_time"] = False
            ctx["last_present_tick"] = None
            ctx["late_counter_recorded"] = False

    def _employment_determine_state(
        self,
        *,
        ctx: dict[str, Any],
        tick: int,
        start: int,
        at_required_location: bool,
        employment_cfg: EmploymentConfig,
    ) -> str:
        ticks_since_start = tick - start
        state = ctx["state"]

        if at_required_location:
            ctx["last_present_tick"] = tick
            if ctx["ever_on_time"] or ticks_since_start <= employment_cfg.grace_ticks:
                state = "on_time"
                ctx["ever_on_time"] = True
            else:
                state = "late"
        else:
            if ticks_since_start <= employment_cfg.grace_ticks:
                state = "late"
            elif ticks_since_start > employment_cfg.absent_cutoff:
                state = "absent"
            elif (
                ctx["last_present_tick"] is not None
                and tick - ctx["last_present_tick"] > employment_cfg.absence_slack
            ):
                state = "absent"
            else:
                state = "late"

        return state

    def _employment_apply_state_effects(
        self,
        *,
        snapshot: AgentSnapshot,
        ctx: dict[str, Any],
        state: str,
        at_required_location: bool,
        wage_rate: float,
        lateness_penalty: float,
        employment_cfg: EmploymentConfig,
    ) -> None:
        previous_state = ctx["state"]
        ctx["state"] = state
        snapshot.shift_state = state
        eligible_for_wage = state in {"on_time", "late"} and at_required_location
        coworkers = self._employment_coworkers_on_shift(snapshot)

        if state == "on_time":
            ctx["on_time_ticks"] += 1
        if state == "late":
            ctx["late_ticks"] += 1
            snapshot.late_ticks_today += 1
            if not ctx["late_penalty_applied"] and previous_state not in {
                "on_time",
                "late",
            }:
                snapshot.wallet = max(0.0, snapshot.wallet - lateness_penalty)
                ctx["late_penalty_applied"] = True
                if not ctx["late_counter_recorded"]:
                    snapshot.lateness_counter += 1
                    ctx["late_counter_recorded"] = True
            if not ctx["late_event_emitted"]:
                self._emit_event(
                    "shift_late_start",
                    {
                        "agent_id": snapshot.agent_id,
                        "job_id": snapshot.job_id,
                        "ticks_late": ctx["late_ticks"],
                    },
                )
                ctx["late_event_emitted"] = True
            if not at_required_location:
                penalty = employment_cfg.late_tick_penalty
                if penalty:
                    snapshot.wallet = max(0.0, snapshot.wallet - penalty)
                snapshot.wages_withheld += wage_rate
            if coworkers and not ctx["late_help_event_emitted"]:
                for other_id in coworkers:
                    self.update_relationship(
                        snapshot.agent_id,
                        other_id,
                        trust=0.2,
                        familiarity=0.1,
                        rivalry=-0.1,
                        event="employment_help",
                    )
                self._emit_event(
                    "employment_helped_when_late",
                    {
                        "agent_id": snapshot.agent_id,
                        "coworkers": coworkers,
                    },
                )
                ctx["late_help_event_emitted"] = True

        if state == "absent":
            if not ctx["absence_penalty_applied"]:
                snapshot.wallet = max(
                    0.0, snapshot.wallet - employment_cfg.absence_penalty
                )
                ctx["absence_penalty_applied"] = True
            snapshot.wages_withheld += wage_rate
            if not ctx["absence_event_emitted"]:
                self._emit_event(
                    "shift_absent",
                    {
                        "agent_id": snapshot.agent_id,
                        "job_id": snapshot.job_id,
                    },
                )
                ctx["absence_event_emitted"] = True
                ctx["absence_events"].append(self.tick)
                snapshot.absent_shifts_7d = len(ctx["absence_events"])
            if coworkers and not ctx["took_shift_event_emitted"]:
                for other_id in coworkers:
                    self.update_relationship(
                        snapshot.agent_id,
                        other_id,
                        trust=-0.1,
                        familiarity=0.0,
                        rivalry=0.3,
                        event="employment_shift_taken",
                    )
                self._emit_event(
                    "employment_took_my_shift",
                    {
                        "agent_id": snapshot.agent_id,
                        "coworkers": coworkers,
                    },
                )
                ctx["took_shift_event_emitted"] = True
        else:
            # Reset absence penalty if they return during the same shift.
            if state in {"on_time", "late"}:
                ctx["absence_penalty_applied"] = False

        if eligible_for_wage and state != "absent":
            snapshot.on_shift = True
            snapshot.wallet += wage_rate
            snapshot.inventory["wages_earned"] = (
                snapshot.inventory.get("wages_earned", 0) + 1
            )
            ctx["wages_paid"] += wage_rate
        else:
            snapshot.on_shift = False
            if previous_state in {"on_time", "late"} and state not in {
                "on_time",
                "late",
            }:
                if not ctx["departure_event_emitted"] and previous_state != "absent":
                    self._emit_event(
                        "shift_departed_early",
                        {
                            "agent_id": snapshot.agent_id,
                            "job_id": snapshot.job_id,
                        },
                    )
                    ctx["departure_event_emitted"] = True

    def _employment_finalize_shift(
        self,
        *,
        snapshot: AgentSnapshot,
        ctx: dict[str, Any],
        employment_cfg: EmploymentConfig,
        job_id: str | None,
    ) -> None:
        if ctx["shift_started_tick"] is None or ctx["shift_outcome_recorded"]:
            snapshot.shift_state = "post_shift"
            snapshot.on_shift = False
            return

        scheduled = max(1, ctx["scheduled_ticks"])
        attendance_value = ctx["on_time_ticks"] / scheduled
        ctx["attendance_samples"].append(attendance_value)
        if ctx["absence_event_emitted"] or ctx["state"] == "absent":
            # absence already recorded when event emitted.
            pass
        snapshot.attendance_ratio = sum(ctx["attendance_samples"]) / len(
            ctx["attendance_samples"]
        )
        ctx["shift_outcome_recorded"] = True
        ctx["state"] = "post_shift"
        snapshot.shift_state = "post_shift"
        snapshot.on_shift = False
        # Reset per-shift counters ready for next cycle.
        ctx["shift_started_tick"] = None
        ctx["shift_end_tick"] = None
        ctx["last_present_tick"] = None
        ctx["late_penalty_applied"] = False
        ctx["absence_penalty_applied"] = False
        ctx["late_event_emitted"] = False
        ctx["absence_event_emitted"] = False
        ctx["departure_event_emitted"] = False
        ctx["late_counter_recorded"] = False
        snapshot.late_ticks_today = ctx["late_ticks"]
        ctx["late_ticks"] = 0

    def _employment_coworkers_on_shift(self, snapshot: AgentSnapshot) -> list[str]:
        job_id = snapshot.job_id
        if job_id is None:
            return []
        coworkers: list[str] = []
        for other in self.agents.values():
            if other.agent_id == snapshot.agent_id or other.job_id != job_id:
                continue
            other_ctx = self._get_employment_context(other.agent_id)
            if other_ctx["state"] in {"on_time", "late"}:
                coworkers.append(other.agent_id)
        return coworkers

    def _employment_enqueue_exit(self, agent_id: str, tick: int) -> None:
        if agent_id in self._employment_exit_queue:
            return
        self._employment_exit_queue.append(agent_id)
        self._employment_exit_queue_timestamps[agent_id] = tick
        snapshot = self.agents.get(agent_id)
        if snapshot is not None:
            snapshot.exit_pending = True
        limit = self.config.employment.exit_queue_limit
        if limit and len(self._employment_exit_queue) > limit:
            self._emit_event(
                "employment_exit_queue_overflow",
                {
                    "pending_count": len(self._employment_exit_queue),
                    "limit": limit,
                },
            )
        else:
            self._emit_event(
                "employment_exit_pending",
                {
                    "agent_id": agent_id,
                    "pending_count": len(self._employment_exit_queue),
                },
            )

    def _employment_remove_from_queue(self, agent_id: str) -> None:
        if agent_id in self._employment_exit_queue:
            self._employment_exit_queue.remove(agent_id)
        self._employment_exit_queue_timestamps.pop(agent_id, None)
        snapshot = self.agents.get(agent_id)
        if snapshot is not None:
            snapshot.exit_pending = False

    def employment_queue_snapshot(self) -> dict[str, Any]:
        return {
            "pending": list(self._employment_exit_queue),
            "pending_count": len(self._employment_exit_queue),
            "exits_today": self._employment_exits_today,
            "daily_exit_cap": self.config.employment.daily_exit_cap,
            "queue_limit": self.config.employment.exit_queue_limit,
            "review_window": self.config.employment.exit_review_window,
        }

    def employment_request_manual_exit(self, agent_id: str, tick: int) -> bool:
        if agent_id not in self.agents:
            return False
        self._employment_manual_exits.add(agent_id)
        self._emit_event(
            "employment_exit_manual_request",
            {
                "agent_id": agent_id,
                "tick": tick,
            },
        )
        return True

    def employment_defer_exit(self, agent_id: str) -> bool:
        if agent_id not in self.agents:
            return False
        self._employment_manual_exits.discard(agent_id)
        self._employment_remove_from_queue(agent_id)
        self._emit_event(
            "employment_exit_deferred",
            {
                "agent_id": agent_id,
                "pending_count": len(self._employment_exit_queue),
            },
        )
        return True

    def _update_basket_metrics(self) -> None:
        basket_cost = (
            self.config.economy.get("meal_cost", 0.0)
            + self.config.economy.get("cook_energy_cost", 0.0)
            + self.config.economy.get("cook_hygiene_cost", 0.0)
            + self.config.economy.get("ingredients_cost", 0.0)
        )
        for snapshot in self.agents.values():
            snapshot.inventory["basket_cost"] = basket_cost
        self._restock_economy()

    def _restock_economy(self) -> None:
        restock_amount = int(self.config.economy.get("stove_stock_replenish", 0))
        if restock_amount <= 0:
            return
        if self.tick % 200 != 0:
            return
        for obj in self.objects.values():
            if obj.object_type == "stove":
                before = obj.stock.get("raw_ingredients", 0)
                obj.stock["raw_ingredients"] = before + restock_amount
                self._emit_event(
                    "stock_replenish",
                    {
                        "object_id": obj.object_id,
                        "type": "stove",
                        "amount": restock_amount,
                    },
                )

    def _handle_affordance_economy_start(
        self, agent_id: str, object_id: str, spec: AffordanceSpec
    ) -> None:
        if spec.affordance_id == "eat_meal":
            self._handle_eat_meal_start(agent_id, object_id)
        elif spec.affordance_id == "cook_meal":
            self._handle_cook_meal_start(agent_id, object_id)

    def _handle_eat_meal_start(self, agent_id: str, object_id: str) -> None:
        snapshot = self.agents.get(agent_id)
        obj = self.objects.get(object_id)
        if snapshot is None or obj is None:
            return
        meal_cost = self.config.economy.get("meal_cost", 0.4)
        if obj.stock.get("meals", 0) <= 0 or snapshot.wallet < meal_cost:
            self._emit_event(
                "affordance_fail",
                {
                    "agent_id": agent_id,
                    "object_id": object_id,
                    "affordance_id": "eat_meal",
                    "reason": "insufficient_stock",
                },
            )
            self.queue_manager.release(object_id, agent_id, self.tick, success=False)
            self._sync_reservation(object_id)
            self._running_affordances.pop(object_id, None)
            return

        obj.stock["meals"] = max(0, obj.stock.get("meals", 0) - 1)
        snapshot.wallet -= meal_cost
        snapshot.inventory["meals_consumed"] = (
            snapshot.inventory.get("meals_consumed", 0) + 1
        )

        record = self._recent_meal_participants.get(object_id)
        if record and record.get("tick") == self.tick:
            participants: set[str] = record["agents"]
        else:
            participants = set()
            record = {"tick": self.tick, "agents": participants}
            self._recent_meal_participants[object_id] = record

        for other_id in participants:
            self.update_relationship(
                agent_id,
                other_id,
                trust=0.1,
                familiarity=0.25,
                event="shared_meal",
            )
        participants.add(agent_id)
        self._emit_event(
            "shared_meal",
            {
                "agents": sorted(participants),
                "object_id": object_id,
            },
        )

    def _handle_cook_meal_start(self, agent_id: str, object_id: str) -> None:
        snapshot = self.agents.get(agent_id)
        obj = self.objects.get(object_id)
        if snapshot is None or obj is None:
            return
        cost = self.config.economy.get("ingredients_cost", 0.15)
        if snapshot.wallet < cost:
            self._emit_event(
                "affordance_fail",
                {
                    "agent_id": agent_id,
                    "object_id": object_id,
                    "affordance_id": "cook_meal",
                    "reason": "insufficient_funds",
                },
            )
            self.queue_manager.release(object_id, agent_id, self.tick, success=False)
            self._sync_reservation(object_id)
            self._running_affordances.pop(object_id, None)
            return

        snapshot.wallet -= cost
        obj.stock["raw_ingredients"] = obj.stock.get("raw_ingredients", 0) - 1
        if obj.stock["raw_ingredients"] < 0:
            obj.stock["raw_ingredients"] = 0
            self._emit_event(
                "affordance_fail",
                {
                    "agent_id": agent_id,
                    "object_id": object_id,
                    "affordance_id": "cook_meal",
                    "reason": "no_ingredients",
                },
            )
            self.queue_manager.release(object_id, agent_id, self.tick, success=False)
            self._sync_reservation(object_id)
            self._running_affordances.pop(object_id, None)
            return
        snapshot.inventory["meals_cooked"] = (
            snapshot.inventory.get("meals_cooked", 0) + 1
        )
        obj.stock["meals"] = obj.stock.get("meals", 0) + 1

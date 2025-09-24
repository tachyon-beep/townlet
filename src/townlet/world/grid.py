"""Grid world representation and affordance integration."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml

from townlet.config import SimulationConfig
from townlet.observations.embedding import EmbeddingAllocator
from townlet.world.queue_manager import QueueManager


@dataclass
class AgentSnapshot:
    """Minimal agent view used for scaffolding."""

    agent_id: str
    position: tuple[int, int]
    needs: Dict[str, float]
    wallet: float = 0.0
    inventory: Dict[str, int] = field(default_factory=dict)
    job_id: str | None = None
    on_shift: bool = False
    lateness_counter: int = 0
    last_late_tick: int = -1


@dataclass
class InteractiveObject:
    """Represents an interactive world object with optional occupancy."""

    object_id: str
    object_type: str
    occupied_by: str | None = None


@dataclass
class RunningAffordance:
    """Tracks an affordance currently executing on an object."""

    agent_id: str
    affordance_id: str
    duration_remaining: int
    effects: Dict[str, float]


@dataclass
class AffordanceSpec:
    """Static affordance definition loaded from configuration."""

    affordance_id: str
    object_type: str
    duration: int
    effects: Dict[str, float]


@dataclass
class WorldState:
    """Holds mutable world state for the simulation tick."""

    config: SimulationConfig
    agents: Dict[str, AgentSnapshot] = field(default_factory=dict)
    tick: int = 0
    queue_manager: QueueManager = field(init=False)
    embedding_allocator: EmbeddingAllocator = field(init=False)
    _active_reservations: Dict[str, str] = field(init=False, default_factory=dict)
    objects: Dict[str, InteractiveObject] = field(init=False, default_factory=dict)
    affordances: Dict[str, AffordanceSpec] = field(init=False, default_factory=dict)
    _running_affordances: Dict[str, RunningAffordance] = field(init=False, default_factory=dict)
    _pending_events: Dict[int, List[Dict[str, Any]]] = field(init=False, default_factory=dict)
    store_stock: Dict[str, Dict[str, int]] = field(init=False, default_factory=dict)
    _job_keys: List[str] = field(init=False, default_factory=list)

    @classmethod
    def from_config(cls, config: SimulationConfig) -> "WorldState":
        """Bootstrap the initial world from config."""
        return cls(config=config)

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
        self._load_affordance_definitions()

    def apply_console(self, operations: Iterable[Any]) -> None:
        """Apply console operations before the tick sequence runs."""
        for operation in operations:
            # TODO(@townlet): Implement concrete console op handlers.
            _ = operation

    def register_object(self, object_id: str, object_type: str) -> None:
        """Register an interactive object in the world."""
        self.objects[object_id] = InteractiveObject(object_id=object_id, object_type=object_type)
        if object_type == "fridge":
            self.store_stock.setdefault(object_id, {"meals": 5})

    def register_affordance(
        self,
        *,
        affordance_id: str,
        object_type: str,
        duration: int,
        effects: Dict[str, float],
    ) -> None:
        """Register an affordance available in the world."""
        self.affordances[affordance_id] = AffordanceSpec(
            affordance_id=affordance_id,
            object_type=object_type,
            duration=duration,
            effects=effects,
        )

    def apply_actions(self, actions: Dict[str, Any]) -> None:
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

            if kind == "request" and object_id:
                granted = self.queue_manager.request_access(object_id, agent_id, current_tick)
                self._sync_reservation(object_id)
                if not granted and action.get("blocked"):
                    self._handle_blocked(object_id, current_tick)
            elif kind == "start" and object_id:
                affordance_id = action.get("affordance")
                if affordance_id:
                    self._start_affordance(agent_id, object_id, affordance_id)
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
                self.queue_manager.release(object_id, agent_id, current_tick, success=success)
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
            elif kind == "blocked" and object_id:
                self._handle_blocked(object_id, current_tick)
            # TODO(@townlet): Update agent snapshot based on outcomes.

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
                self.queue_manager.release(object_id, occupant, current_tick, success=False)
                self._running_affordances.pop(object_id, None)
                self._sync_reservation(object_id)
        # TODO(@townlet): Integrate with affordance registry and hook dispatch.

        for object_id, running in list(self._running_affordances.items()):
            running.duration_remaining -= 1
            if running.duration_remaining <= 0:
                self._apply_affordance_effects(running.agent_id, running.effects)
                self._running_affordances.pop(object_id, None)
                self.queue_manager.release(object_id, running.agent_id, current_tick, success=True)
                self._sync_reservation(object_id)
                self._emit_event(
                    "affordance_finish",
                    {
                        "agent_id": running.agent_id,
                        "object_id": object_id,
                        "affordance_id": running.affordance_id,
                    },
                )

        self._apply_need_decay()

    def snapshot(self) -> Dict[str, AgentSnapshot]:
        """Return a shallow copy of the agent dictionary for observers."""
        return dict(self.agents)

    @property
    def active_reservations(self) -> Dict[str, str]:
        """Expose a copy of active reservations for diagnostics/tests."""
        return dict(self._active_reservations)

    def drain_events(self) -> List[Dict[str, Any]]:
        """Return all pending events accumulated up to the current tick."""
        events: List[Dict[str, Any]] = []
        for _, batch in sorted(self._pending_events.items()):
            events.extend(batch)
        self._pending_events.clear()
        return events

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

    def _start_affordance(self, agent_id: str, object_id: str, affordance_id: str) -> None:
        if self.queue_manager.active_agent(object_id) != agent_id:
            return
        if object_id in self._running_affordances:
            return
        obj = self.objects.get(object_id)
        spec = self.affordances.get(affordance_id)
        if obj is None or spec is None:
            return
        if spec.object_type != obj.object_type:
            return

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

    def _apply_affordance_effects(self, agent_id: str, effects: Dict[str, float]) -> None:
        snapshot = self.agents.get(agent_id)
        if snapshot is None:
            return
        for key, delta in effects.items():
            if key in snapshot.needs:
                new_value = snapshot.needs[key] + delta
                snapshot.needs[key] = max(0.0, min(1.0, new_value))
            elif key == "money":
                snapshot.wallet += delta

    def _emit_event(self, event: str, payload: Dict[str, Any]) -> None:
        events = self._pending_events.setdefault(self.tick, [])
        events.append({"event": event, "tick": self.tick, **payload})

    def _load_affordance_definitions(self) -> None:
        config_path = Path(self.config.affordances.affordances_file).expanduser()
        if not config_path.exists():
            return
        data = yaml.safe_load(config_path.read_text()) or []
        for entry in data:
            entry_type = entry.get("type", "affordance")
            if entry_type == "object":
                object_id = entry.get("id")
                object_type = entry.get("object_type") or entry.get("objectType")
                if object_id and object_type:
                    self.register_object(object_id, object_type)
            else:
                affordance_id = entry.get("id")
                object_type = entry.get("object_type") or entry.get("objectType")
                duration = int(entry.get("duration", 1))
                effects = entry.get("effects", {})
                if affordance_id and object_type:
                    self.register_affordance(
                        affordance_id=affordance_id,
                        object_type=object_type,
                        duration=duration,
                        effects=effects,
                    )
        self._assign_jobs_to_agents()

    def _apply_need_decay(self) -> None:
        decay_rates = self.config.rewards.decay_rates
        for snapshot in self.agents.values():
            for need, decay in decay_rates.items():
                if need in snapshot.needs:
                    snapshot.needs[need] = max(0.0, snapshot.needs[need] - decay)
        self._apply_job_state()

    def _assign_jobs_to_agents(self) -> None:
        if not self._job_keys:
            return
        for index, snapshot in enumerate(self.agents.values()):
            if snapshot.job_id is None or snapshot.job_id not in self.config.jobs:
                snapshot.job_id = self._job_keys[index % len(self._job_keys)]

    def _apply_job_state(self) -> None:
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
            else:
                snapshot.on_shift = False

    def _handle_affordance_economy_start(
        self, agent_id: str, object_id: str, spec: AffordanceSpec
    ) -> None:
        if spec.affordance_id == "eat_meal":
            self._handle_eat_meal_start(agent_id, object_id)

    def _handle_eat_meal_start(self, agent_id: str, object_id: str) -> None:
        snapshot = self.agents.get(agent_id)
        if snapshot is None:
            return
        meal_cost = self.config.economy.get("meal_cost", 0.4)
        stock = self.store_stock.get(object_id)
        if stock is None:
            self.store_stock[object_id] = {"meals": 0}
            stock = self.store_stock[object_id]
        if stock.get("meals", 0) <= 0 or snapshot.wallet < meal_cost:
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

        stock["meals"] -= 1
        snapshot.wallet -= meal_cost
        snapshot.inventory["meals_consumed"] = snapshot.inventory.get("meals_consumed", 0) + 1

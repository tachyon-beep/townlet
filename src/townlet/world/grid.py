"""Grid world representation and affordance integration."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Deque, Dict, Iterable, List, Tuple

import yaml

from townlet.config import EmploymentConfig, SimulationConfig
from townlet.observations.embedding import EmbeddingAllocator
from townlet.world.queue_manager import QueueManager
from townlet.world.rivalry import RivalryLedger, RivalryParameters


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
    shift_state: str = "pre_shift"
    late_ticks_today: int = 0
    attendance_ratio: float = 0.0
    absent_shifts_7d: int = 0
    wages_withheld: float = 0.0
    exit_pending: bool = False


@dataclass
class InteractiveObject:
    """Represents an interactive world object with optional occupancy."""

    object_id: str
    object_type: str
    occupied_by: str | None = None
    stock: Dict[str, int] = field(default_factory=dict)


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
    _employment_state: Dict[str, Dict[str, Any]] = field(init=False, default_factory=dict)
    _employment_exit_queue: List[str] = field(init=False, default_factory=list)
    _employment_exits_today: int = field(init=False, default=0)
    _employment_exit_queue_timestamps: Dict[str, int] = field(init=False, default_factory=dict)
    _employment_manual_exits: set[str] = field(init=False, default_factory=set)

    _rivalry_ledgers: Dict[str, RivalryLedger] = field(init=False, default_factory=dict)

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
        self._employment_state = {}
        self._employment_exit_queue = []
        self._employment_exits_today = 0
        self._employment_exit_queue_timestamps = {}
        self._employment_manual_exits = set()
        self._rivalry_ledgers = {}
        self._load_affordance_definitions()

    def apply_console(self, operations: Iterable[Any]) -> None:
        """Apply console operations before the tick sequence runs."""
        for operation in operations:
            # TODO(@townlet): Implement concrete console op handlers.
            _ = operation

    def register_object(self, object_id: str, object_type: str) -> None:
        """Register an interactive object in the world."""
        obj = InteractiveObject(object_id=object_id, object_type=object_type)
        if object_type == "fridge":
            obj.stock["meals"] = 5
        if object_type == "stove":
            obj.stock["raw_ingredients"] = 3
        if object_type == "bed":
            obj.stock["sleep_slots"] = 1
        self.objects[object_id] = obj
        self.store_stock[object_id] = obj.stock

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
            elif kind == "move" and action.get("position"):
                target_pos = tuple(action["position"])
                snapshot.position = target_pos
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
                waiting = self.queue_manager.queue_snapshot(object_id)
                rival = waiting[0] if waiting else None
                self.queue_manager.release(object_id, occupant, current_tick, success=False)
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
                self.queue_manager.release(object_id, running.agent_id, current_tick, success=True)
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

    def snapshot(self) -> Dict[str, AgentSnapshot]:
        """Return a shallow copy of the agent dictionary for observers."""
        return dict(self.agents)

    def local_view(
        self,
        agent_id: str,
        radius: int,
        *,
        include_agents: bool = True,
        include_objects: bool = True,
    ) -> Dict[str, Any]:
        """Return local neighborhood information for observation builders."""
        snapshot = self.agents.get(agent_id)
        if snapshot is None:
            return {"tiles": [], "agents": [], "objects": []}
        cx, cy = snapshot.position
        tiles: List[Dict[str, Any]] = []
        seen_agents: List[Dict[str, Any]] = []
        seen_objects: List[Dict[str, Any]] = []
        for dx in range(-radius, radius + 1):
            row: List[Dict[str, Any]] = []
            for dy in range(-radius, radius + 1):
                x, y = cx + dx, cy + dy
                row.append({"position": (x, y)})
                if include_agents:
                    for other in self.agents.values():
                        if other.agent_id == agent_id:
                            continue
                        if other.position == (x, y):
                            seen_agents.append({
                                "agent_id": other.agent_id,
                                "position": other.position,
                            })
                if include_objects:
                    for object_id, obj in self.objects.items():
                        if obj.object_type and obj.object_id == object_id:
                            # Placeholder: real implementation will use object coordinates.
                            pass
            tiles.append(row)
        # TODO: integrate actual grid/object positions once world stores them.
        return {"tiles": tiles, "agents": seen_agents, "objects": seen_objects}

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
        params = self.config.conflict.rivalry
        base_intensity = intensity
        if base_intensity is None:
            boost = params.ghost_step_boost if reason == "ghost_step" else params.handover_boost
            base_intensity = boost + params.queue_length_boost * max(queue_length - 1, 0)
        clamped_intensity = min(5.0, max(0.1, base_intensity))
        self.register_rivalry_conflict(actor, rival, intensity=clamped_intensity)
        self._emit_event(
            "queue_conflict",
            {
                "object_id": object_id,
                "actor": actor,
                "rival": rival,
                "reason": reason,
                "queue_length": queue_length,
                "intensity": clamped_intensity,
            },
        )

    def register_rivalry_conflict(self, agent_a: str, agent_b: str, *, intensity: float = 1.0) -> None:
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

    def rivalry_snapshot(self) -> Dict[str, Dict[str, float]]:
        """Expose rivalry ledgers for telemetry/diagnostics."""
        snapshot: Dict[str, Dict[str, float]] = {}
        for agent_id, ledger in self._rivalry_ledgers.items():
            data = ledger.snapshot()
            if data:
                snapshot[agent_id] = data
        return snapshot

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

    def rivalry_top(self, agent_id: str, limit: int) -> List[Tuple[str, float]]:
        ledger = self._rivalry_ledgers.get(agent_id)
        if ledger is None:
            return []
        return ledger.top_rivals(limit)

    def _get_rivalry_ledger(self, agent_id: str) -> RivalryLedger:
        ledger = self._rivalry_ledgers.get(agent_id)
        if ledger is None:
            ledger = RivalryLedger(params=self._rivalry_parameters())
            self._rivalry_ledgers[agent_id] = ledger
        return ledger

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
        empty_agents: List[str] = []
        for agent_id, ledger in self._rivalry_ledgers.items():
            ledger.decay(ticks=1)
            if not ledger.snapshot():
                empty_agents.append(agent_id)
        for agent_id in empty_agents:
            self._rivalry_ledgers.pop(agent_id, None)

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
                        snapshot.inventory.get("wages_earned", 0)
                        + 1
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
    def _employment_context_defaults(self) -> Dict[str, Any]:
        window = max(1, self.config.employment.attendance_window)
        return {
            "state": "pre_shift",
            "late_penalty_applied": False,
            "absence_penalty_applied": False,
            "late_event_emitted": False,
            "absence_event_emitted": False,
            "departure_event_emitted": False,
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

    def _get_employment_context(self, agent_id: str) -> Dict[str, Any]:
        ctx = self._employment_state.get(agent_id)
        if ctx is None or ctx.get("attendance_samples") is None:
            ctx = self._employment_context_defaults()
            self._employment_state[agent_id] = ctx
        # Resize deque if window changed via config reload.
        window = max(1, self.config.employment.attendance_window)
        samples: Deque[float] = ctx["attendance_samples"]
        if samples.maxlen != window:
            new_samples: Deque[float] = deque(samples, maxlen=window)
            ctx["attendance_samples"] = new_samples
        return ctx

    def _employment_idle_state(self, snapshot: AgentSnapshot, ctx: Dict[str, Any]) -> None:
        if ctx["state"] != "pre_shift":
            ctx["state"] = "pre_shift"
            ctx["late_penalty_applied"] = False
            ctx["absence_penalty_applied"] = False
            ctx["late_event_emitted"] = False
            ctx["absence_event_emitted"] = False
            ctx["departure_event_emitted"] = False
            ctx["shift_started_tick"] = None
            ctx["shift_end_tick"] = None
            ctx["last_present_tick"] = None
            ctx["ever_on_time"] = False
            ctx["scheduled_ticks"] = 0
            ctx["on_time_ticks"] = 0
            ctx["shift_outcome_recorded"] = False
        snapshot.shift_state = "pre_shift"
        snapshot.on_shift = False

    def _employment_prepare_state(self, snapshot: AgentSnapshot, ctx: Dict[str, Any]) -> None:
        ctx["state"] = "await_start"
        snapshot.shift_state = "await_start"
        snapshot.on_shift = False

    def _employment_begin_shift(self, ctx: Dict[str, Any], start: int, end: int) -> None:
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
            ctx["shift_outcome_recorded"] = False
            ctx["ever_on_time"] = False
            ctx["last_present_tick"] = None
            ctx["late_counter_recorded"] = False

    def _employment_determine_state(
        self,
        *,
        ctx: Dict[str, Any],
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
        ctx: Dict[str, Any],
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

        if state == "on_time":
            ctx["on_time_ticks"] += 1
        if state == "late":
            ctx["late_ticks"] += 1
            snapshot.late_ticks_today += 1
            if (
                not ctx["late_penalty_applied"]
                and previous_state not in {"on_time", "late"}
            ):
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

        if state == "absent":
            if not ctx["absence_penalty_applied"]:
                snapshot.wallet = max(0.0, snapshot.wallet - employment_cfg.absence_penalty)
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
            if previous_state in {"on_time", "late"} and state not in {"on_time", "late"}:
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
        ctx: Dict[str, Any],
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
        snapshot.attendance_ratio = (
            sum(ctx["attendance_samples"]) / len(ctx["attendance_samples"])
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

    def employment_queue_snapshot(self) -> Dict[str, Any]:
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
        snapshot.inventory["meals_consumed"] = snapshot.inventory.get("meals_consumed", 0) + 1

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
        snapshot.inventory["meals_cooked"] = snapshot.inventory.get("meals_cooked", 0) + 1
        obj.stock["meals"] = obj.stock.get("meals", 0) + 1

"""Employment domain logic extracted from WorldState."""

from __future__ import annotations

import logging
from collections import deque
from collections.abc import Callable, Iterable, Mapping
from typing import TYPE_CHECKING, Any

from townlet.config import EmploymentConfig, SimulationConfig

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .grid import AgentSnapshot, WorldState


class EmploymentEngine:
    """Manages employment state, queues, and shift bookkeeping."""

    def __init__(
        self, config: SimulationConfig, emit_event: Callable[[str, dict[str, object]], None]
    ) -> None:
        self._config = config
        self._emit_event = emit_event
        self._state: dict[str, dict[str, Any]] = {}
        self._exit_queue: list[str] = []
        self._exits_today: int = 0
        self._exit_timestamps: dict[str, int] = {}
        self._manual_exits: set[str] = set()

    # -- properties -----------------------------------------------------

    @property
    def exits_today(self) -> int:
        return self._exits_today

    # -- job assignment -------------------------------------------------

    def assign_jobs_to_agents(self, world: WorldState) -> None:
        if not world._job_keys:
            return
        for index, snapshot in enumerate(world.agents.values()):
            if snapshot.job_id is None or snapshot.job_id not in self._config.jobs:
                snapshot.job_id = world._job_keys[index % len(world._job_keys)]
            snapshot.inventory.setdefault("meals_cooked", 0)
            snapshot.inventory.setdefault("meals_consumed", 0)
            snapshot.inventory.setdefault("wages_earned", 0)

    def apply_job_state(self, world: WorldState) -> None:
        if self._config.employment.enforce_job_loop:
            self._apply_job_state_enforced(world)
        else:
            self._apply_job_state_legacy(world)

    def _apply_job_state_legacy(self, world: WorldState) -> None:
        jobs = self._config.jobs
        default_job_id = world._job_keys[0] if world._job_keys else None
        for snapshot in world.agents.values():
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
            wage_rate = spec.wage_rate or self._config.economy.get("wage_income", 0.0)
            lateness_penalty = spec.lateness_penalty
            location = spec.location
            required_position = tuple(location) if location else (0, 0)

            if start <= world.tick <= end:
                snapshot.on_shift = True
                if world.tick == start and snapshot.position != required_position:
                    snapshot.lateness_counter += 1
                    if snapshot.last_late_tick != world.tick:
                        snapshot.wallet = max(0.0, snapshot.wallet - lateness_penalty)
                        snapshot.last_late_tick = world.tick
                        self._emit_event(
                            "job_late",
                            {
                                "agent_id": snapshot.agent_id,
                                "job_id": job_id,
                                "tick": world.tick,
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

    def _apply_job_state_enforced(self, world: WorldState) -> None:
        jobs = self._config.jobs
        default_job_id = world._job_keys[0] if world._job_keys else None
        employment_cfg = self._config.employment
        arrival_buffer = self._config.behavior.job_arrival_buffer
        ticks_per_day = max(1, employment_cfg.exit_review_window)
        seven_day_window = ticks_per_day * 7

        for snapshot in world.agents.values():
            ctx = self.get_employment_context(world, snapshot.agent_id)
            current_day = world.tick // ticks_per_day
            if ctx["current_day"] != current_day:
                ctx["current_day"] = current_day
                ctx["late_ticks"] = 0
                ctx["wages_paid"] = 0.0
                snapshot.late_ticks_today = 0

            job_id = snapshot.job_id
            if job_id is None or job_id not in jobs:
                if default_job_id is None:
                    self._employment_idle_state(world, snapshot, ctx)
                    continue
                job_id = default_job_id
                snapshot.job_id = job_id

            spec = jobs[job_id]
            start = spec.start_tick
            end = spec.end_tick or spec.start_tick
            if end < start:
                end = start
            wage_rate = spec.wage_rate or self._config.economy.get("wage_income", 0.0)
            lateness_penalty = spec.lateness_penalty
            required_position = tuple(spec.location) if spec.location else None
            at_required_location = (
                required_position is None or snapshot.position == required_position
            )

            while ctx["absence_events"] and (
                world.tick - ctx["absence_events"][0] > seven_day_window
            ):
                ctx["absence_events"].popleft()
            snapshot.absent_shifts_7d = len(ctx["absence_events"])

            if world.tick < start - arrival_buffer:
                self._employment_idle_state(world, snapshot, ctx)
                continue

            if start - arrival_buffer <= world.tick < start:
                self._employment_prepare_state(snapshot, ctx)
                continue

            if start <= world.tick <= end:
                self._employment_begin_shift(ctx, start, end)
                state = self._employment_determine_state(
                    ctx=ctx,
                    tick=world.tick,
                    start=start,
                    at_required_location=at_required_location,
                    employment_cfg=employment_cfg,
                )
                self._employment_apply_state_effects(
                    world=world,
                    snapshot=snapshot,
                    ctx=ctx,
                    state=state,
                    at_required_location=at_required_location,
                    wage_rate=wage_rate,
                    lateness_penalty=lateness_penalty,
                    employment_cfg=employment_cfg,
                )
                continue

            self._employment_finalize_shift(
                world=world,
                snapshot=snapshot,
                ctx=ctx,
                employment_cfg=employment_cfg,
                job_id=job_id,
            )

    # -- context helpers ------------------------------------------------

    def context_defaults(self) -> dict[str, Any]:
        window = max(1, self._config.employment.attendance_window)
        return {
            "state": "pre_shift",
            "current_day": -1,
            "late_ticks": 0,
            "wages_paid": 0.0,
            "late_penalty_applied": False,
            "absence_penalty_applied": False,
            "late_event_emitted": False,
            "absence_event_emitted": False,
            "departure_event_emitted": False,
            "late_help_event_emitted": False,
            "took_shift_event_emitted": False,
            "late_counter_recorded": False,
            "late_ticks_total": 0,
            "late_ticks_today": 0,
            "shift_started_tick": None,
            "shift_end_tick": None,
            "last_present_tick": None,
            "ever_on_time": False,
            "scheduled_ticks": 0,
            "on_time_ticks": 0,
            "shift_outcome_recorded": False,
            "attendance_samples": deque(maxlen=window),
            "absence_events": deque(),
        }

    def get_employment_context(self, world: WorldState, agent_id: str) -> dict[str, Any]:
        ctx = self._state.get(agent_id)
        if ctx is None or ctx.get("attendance_samples") is None:
            ctx = self.context_defaults()
            self._state[agent_id] = ctx
        window = max(1, self._config.employment.attendance_window)
        samples: deque[float] = ctx["attendance_samples"]
        if samples.maxlen != window:
            ctx["attendance_samples"] = deque(samples, maxlen=window)
        return ctx

    def employment_context_wages(self, agent_id: str) -> float:
        ctx = self._state.get(agent_id)
        if not ctx:
            return 0.0
        return float(ctx.get("wages_paid", 0.0))

    def employment_context_punctuality(self, agent_id: str) -> float:
        ctx = self._state.get(agent_id)
        if not ctx:
            return 0.0
        scheduled = max(1, int(ctx.get("scheduled_ticks", 0)))
        on_time = float(ctx.get("on_time_ticks", 0))
        value = on_time / scheduled
        return max(0.0, min(1.0, value))

    # -- state transitions ----------------------------------------------

    def _employment_idle_state(
        self, world: WorldState, snapshot: AgentSnapshot, ctx: dict[str, Any]
    ) -> None:
        if ctx["state"] not in {"pre_shift", "idle"}:
            self._employment_finalize_shift(
                world=world,
                snapshot=snapshot,
                ctx=ctx,
                employment_cfg=self._config.employment,
                job_id=snapshot.job_id,
            )
        ctx["state"] = "idle"
        snapshot.shift_state = "idle"
        snapshot.on_shift = False

    def _employment_prepare_state(self, snapshot: AgentSnapshot, ctx: dict[str, Any]) -> None:
        ctx["state"] = "await_start"
        snapshot.shift_state = "await_start"
        snapshot.on_shift = False

    def _employment_begin_shift(self, ctx: dict[str, Any], start: int, end: int) -> None:
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
        world: WorldState,
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
        coworkers = self._employment_coworkers_on_shift(world, snapshot)

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
                    world.update_relationship(
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
                ctx["absence_events"].append(world.tick)
                snapshot.absent_shifts_7d = len(ctx["absence_events"])
            if coworkers and not ctx["took_shift_event_emitted"]:
                for other_id in coworkers:
                    world.update_relationship(
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
            if state in {"on_time", "late"}:
                ctx["absence_penalty_applied"] = False

        if eligible_for_wage and state != "absent":
            snapshot.on_shift = True
            snapshot.wallet += wage_rate
            snapshot.inventory["wages_earned"] = snapshot.inventory.get("wages_earned", 0) + 1
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
        world: WorldState,
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
            pass
        snapshot.attendance_ratio = sum(ctx["attendance_samples"]) / len(ctx["attendance_samples"])
        ctx["shift_outcome_recorded"] = True
        ctx["state"] = "post_shift"
        snapshot.shift_state = "post_shift"
        snapshot.on_shift = False
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

    def _employment_coworkers_on_shift(
        self, world: WorldState, snapshot: AgentSnapshot
    ) -> list[str]:
        job_id = snapshot.job_id
        if job_id is None:
            return []
        coworkers: list[str] = []
        for other in world.agents.values():
            if other.agent_id == snapshot.agent_id or other.job_id != job_id:
                continue
            other_ctx = self.get_employment_context(world, other.agent_id)
            if other_ctx["state"] in {"on_time", "late"}:
                coworkers.append(other.agent_id)
        return coworkers

    # -- exit queue management -----------------------------------------

    def enqueue_exit(self, world: WorldState, agent_id: str, tick: int) -> None:
        pending_before = len(self._exit_queue)
        if agent_id in self._exit_queue:
            return
        self._exit_queue.append(agent_id)
        self._exit_timestamps[agent_id] = tick
        snapshot = world.agents.get(agent_id)
        if snapshot is not None:
            snapshot.exit_pending = True
        limit = self._config.employment.exit_queue_limit
        if limit and len(self._exit_queue) > limit:
            self._emit_event(
                "employment_exit_queue_overflow",
                {
                    "pending_count": len(self._exit_queue),
                    "limit": limit,
                },
            )
        else:
            self._emit_event(
                "employment_exit_pending",
                {
                    "agent_id": agent_id,
                    "pending_count": len(self._exit_queue),
                },
            )
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                (
                    "employment.enqueue_exit agent=%s tick=%s pending_before=%s "
                    "pending_after=%s manual=%s"
                ),
                agent_id,
                tick,
                pending_before,
                len(self._exit_queue),
                len(self._manual_exits),
            )

    def remove_from_queue(self, world: WorldState, agent_id: str) -> None:
        if agent_id in self._exit_queue:
            self._exit_queue.remove(agent_id)
        self._exit_timestamps.pop(agent_id, None)
        snapshot = world.agents.get(agent_id)
        if snapshot is not None:
            snapshot.exit_pending = False

    def queue_snapshot(self) -> dict[str, Any]:
        employment_cfg = self._config.employment
        return {
            "pending": list(self._exit_queue),
            "pending_count": len(self._exit_queue),
            "exits_today": self._exits_today,
            "daily_exit_cap": employment_cfg.daily_exit_cap,
            "queue_limit": employment_cfg.exit_queue_limit,
            "review_window": employment_cfg.exit_review_window,
        }

    def request_manual_exit(self, world: WorldState, agent_id: str, tick: int) -> bool:
        if agent_id not in world.agents:
            return False
        self._manual_exits.add(agent_id)
        self._emit_event(
            "employment_exit_manual_request",
            {
                "agent_id": agent_id,
                "tick": tick,
            },
        )
        return True

    def defer_exit(self, world: WorldState, agent_id: str) -> bool:
        if agent_id not in world.agents:
            return False
        self._manual_exits.discard(agent_id)
        self.remove_from_queue(world, agent_id)
        self._emit_event(
            "employment_exit_deferred",
            {
                "agent_id": agent_id,
                "pending_count": len(self._exit_queue),
            },
        )
        return True

    # -- persistence helpers -------------------------------------------

    def export_state(self) -> dict[str, object]:
        """Return a serialisable snapshot of the employment domain state."""

        return {
            "exit_queue": list(self._exit_queue),
            "queue_timestamps": dict(self._exit_timestamps),
            "manual_exits": list(self._manual_exits),
            "exits_today": int(self._exits_today),
        }

    def import_state(self, payload: Mapping[str, object]) -> None:
        """Restore employment state from a snapshot payload."""

        exit_queue = payload.get("exit_queue", [])
        self._exit_queue.clear()
        if isinstance(exit_queue, Iterable) and not isinstance(exit_queue, (str, bytes)):
            self._exit_queue.extend(str(agent_id) for agent_id in exit_queue)

        timestamps = payload.get("queue_timestamps", {})
        self._exit_timestamps.clear()
        if isinstance(timestamps, Mapping):
            for agent_id, tick in timestamps.items():
                self._exit_timestamps[str(agent_id)] = int(tick)

        manual = payload.get("manual_exits", [])
        self._manual_exits.clear()
        if isinstance(manual, Iterable) and not isinstance(manual, (str, bytes)):
            self._manual_exits.update(str(agent_id) for agent_id in manual)

        exits_today = payload.get("exits_today", 0)
        self.set_exits_today(int(exits_today))

    def reset_exits_today(self) -> None:
        self._exits_today = 0

    def set_exits_today(self, value: int) -> None:
        self._exits_today = max(0, int(value))

    def increment_exits_today(self) -> None:
        self._exits_today += 1

"""Agent lifecycle enforcement (exits, spawns, cooldowns)."""

from __future__ import annotations

from typing import Dict

from townlet.config import SimulationConfig
from townlet.world.grid import WorldState


class LifecycleManager:
    """Centralises lifecycle checks described in docs/program_management/snapshots/CONCEPTUAL_DESIGN.md#18."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.exits_today = 0
        self._employment_day = -1

    def evaluate(self, world: WorldState, tick: int) -> Dict[str, bool]:
        """Return a map of agent_id -> terminated flag."""
        terminated: Dict[str, bool] = {}
        if self.config.employment.enforce_job_loop:
            employment_terminated = self._evaluate_employment(world, tick)
            terminated.update(employment_terminated)
        for agent_id, snapshot in world.agents.items():
            hunger = snapshot.needs.get("hunger", 0.0)
            if hunger <= 0.03:
                terminated[agent_id] = True
            else:
                terminated.setdefault(agent_id, False)
        return terminated

    def export_state(self) -> Dict[str, int]:
        return {
            "exits_today": int(self.exits_today),
            "employment_day": int(self._employment_day),
        }

    def import_state(self, payload: Dict[str, object]) -> None:
        self.exits_today = int(payload.get("exits_today", 0))
        self._employment_day = int(payload.get("employment_day", -1))

    def reset_state(self) -> None:
        self.exits_today = 0
        self._employment_day = -1

    def _evaluate_employment(self, world: WorldState, tick: int) -> Dict[str, bool]:
        results: Dict[str, bool] = {}
        cfg = self.config.employment
        day_index = tick // max(1, cfg.exit_review_window)
        if day_index != self._employment_day:
            self._employment_day = day_index
            world._employment_exits_today = 0

        for agent_id in list(world._employment_manual_exits):
            if self._employment_execute_exit(
                world, agent_id, tick, reason="manual_approve"
            ):
                results[agent_id] = True
            world._employment_manual_exits.discard(agent_id)

        for agent_id, snapshot in world.agents.items():
            if snapshot.absent_shifts_7d >= cfg.max_absent_shifts:
                world._employment_enqueue_exit(agent_id, tick)

        # Forced exits when pending beyond review window.
        for agent_id in list(world._employment_exit_queue):
            enqueue_tick = world._employment_exit_queue_timestamps.get(agent_id, tick)
            if tick - enqueue_tick >= cfg.exit_review_window:
                if self._employment_execute_exit(
                    world, agent_id, tick, reason="auto_review"
                ):
                    results[agent_id] = True

        # Process daily cap for remaining queue entries.
        while world._employment_exit_queue and (
            cfg.daily_exit_cap == 0
            or world._employment_exits_today < cfg.daily_exit_cap
        ):
            agent_id = world._employment_exit_queue[0]
            if self._employment_execute_exit(world, agent_id, tick, reason="daily_cap"):
                results[agent_id] = True
            else:
                break

        return results

    def _employment_execute_exit(
        self,
        world: WorldState,
        agent_id: str,
        tick: int,
        *,
        reason: str,
    ) -> bool:
        snapshot = world.agents.get(agent_id)
        world._employment_remove_from_queue(agent_id)
        world._employment_manual_exits.discard(agent_id)
        if snapshot is None:
            return False
        world._employment_exits_today += 1
        snapshot.absent_shifts_7d = 0
        snapshot.exit_pending = False
        world._emit_event(
            "employment_exit_processed",
            {
                "agent_id": agent_id,
                "job_id": snapshot.job_id,
                "reason": reason,
                "tick": tick,
            },
        )
        return True

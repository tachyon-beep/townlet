"""Agent lifecycle enforcement (exits, spawns, cooldowns)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from townlet.config import SimulationConfig
from townlet.world.grid import WorldState


@dataclass
class _RespawnTicket:
    agent_id: str
    scheduled_tick: int
    blueprint: dict[str, Any]


class LifecycleManager:
    """Centralises lifecycle checks as outlined in the conceptual design snapshot."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.exits_today = 0
        self._employment_day = -1
        self.mortality_enabled = True
        self.respawn_delay_ticks = max(0, int(getattr(config.lifecycle, "respawn_delay_ticks", 0)))
        self._pending_respawns: list[_RespawnTicket] = []
        self._termination_reasons: dict[str, str] = {}

    def evaluate(self, world: WorldState, tick: int) -> dict[str, bool]:
        """Return a map of agent_id -> terminated flag."""
        terminated: dict[str, bool] = {}
        self._termination_reasons = {}
        if self.config.employment.enforce_job_loop:
            employment_terminated = self._evaluate_employment(world, tick)
            terminated.update(employment_terminated)
        for agent_id, snapshot in world.agents.items():
            hunger = snapshot.needs.get("hunger", 0.0)
            if self.mortality_enabled and hunger <= 0.03:
                terminated[agent_id] = True
                self._termination_reasons.setdefault(agent_id, "faint")
            else:
                terminated.setdefault(agent_id, False)
        return terminated

    def finalize(self, world: WorldState, tick: int, terminated: dict[str, bool]) -> None:
        for agent_id, flag in terminated.items():
            if not flag:
                continue
            blueprint = world.remove_agent(agent_id, tick)
            if blueprint is None:
                continue
            origin = str(blueprint.get("origin_agent_id") or blueprint.get("agent_id") or agent_id)
            new_agent_id = world.generate_agent_id(origin)
            blueprint["origin_agent_id"] = origin
            blueprint["agent_id"] = new_agent_id
            delay = max(0, int(self.respawn_delay_ticks))
            scheduled_tick = tick + delay
            self._pending_respawns.append(
                _RespawnTicket(
                    agent_id=agent_id,
                    scheduled_tick=scheduled_tick,
                    blueprint=blueprint,
                )
            )

    def process_respawns(self, world: WorldState, tick: int) -> None:
        if not self._pending_respawns:
            return
        remaining: list[_RespawnTicket] = []
        for ticket in self._pending_respawns:
            if tick >= ticket.scheduled_tick:
                world.respawn_agent(ticket.blueprint)
            else:
                remaining.append(ticket)
        self._pending_respawns = remaining

    def set_respawn_delay(self, ticks: int) -> None:
        self.respawn_delay_ticks = max(0, int(ticks))
        self.config.lifecycle.respawn_delay_ticks = self.respawn_delay_ticks

    def set_mortality_enabled(self, enabled: bool) -> None:
        self.mortality_enabled = bool(enabled)

    def export_state(self) -> dict[str, int]:
        return {
            "exits_today": int(self.exits_today),
            "employment_day": int(self._employment_day),
        }

    def import_state(self, payload: dict[str, object]) -> None:
        self.exits_today = int(payload.get("exits_today", 0))
        self._employment_day = int(payload.get("employment_day", -1))

    def reset_state(self) -> None:
        self.exits_today = 0
        self._employment_day = -1
        self._termination_reasons = {}

    def termination_reasons(self) -> dict[str, str]:
        """Return termination reasons captured during the last evaluation."""
        return dict(self._termination_reasons)

    def _evaluate_employment(self, world: WorldState, tick: int) -> dict[str, bool]:
        results: dict[str, bool] = {}
        cfg = self.config.employment
        day_index = tick // max(1, cfg.exit_review_window)
        if day_index != self._employment_day:
            self._employment_day = day_index
            world.reset_employment_exits_today()

        for agent_id in world.employment.manual_exit_agents():
            if self._employment_execute_exit(world, agent_id, tick, reason="manual_approve"):
                results[agent_id] = True

        for agent_id, snapshot in world.agents.items():
            if snapshot.absent_shifts_7d >= cfg.max_absent_shifts:
                world.employment.enqueue_exit(world, agent_id, tick)

        # Forced exits when pending beyond review window.
        for agent_id in world.employment.exit_queue_members():
            enqueue_tick = world.employment.exit_queue_enqueue_tick(agent_id) or tick
            if tick - enqueue_tick >= cfg.exit_review_window:
                if self._employment_execute_exit(world, agent_id, tick, reason="auto_review"):
                    results[agent_id] = True

        # Process daily cap for remaining queue entries.
        while (
            world.employment.exit_queue_length() > 0
            and (
            cfg.daily_exit_cap == 0
            or world.employment_exits_today() < cfg.daily_exit_cap
            )
        ):
            agent_id = world.employment.exit_queue_head()
            if agent_id is None:
                break
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
        world.employment.remove_from_queue(world, agent_id)
        world.employment.discard_manual_exit(agent_id)
        if snapshot is None:
            return False
        world.increment_employment_exits_today()
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
        self._termination_reasons[agent_id] = "eviction"
        return True

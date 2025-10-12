"""Nightly reset helpers extracted from the world grid module."""

from __future__ import annotations

from collections.abc import Callable, MutableMapping
from dataclasses import dataclass

from townlet.world.agents.employment import EmploymentService
from townlet.world.agents.registry import AgentRegistry
from townlet.world.queue import QueueManager


@dataclass(slots=True)
class NightlyResetService:
    """Apply nightly upkeep to agents while keeping queue/employment state tidy."""

    agents: AgentRegistry
    queue_manager: QueueManager
    active_reservations: MutableMapping[str, str | None]
    employment_service: EmploymentService
    emit_event: Callable[[str, dict[str, object]], None]
    sync_reservation: Callable[[str], None]
    sync_reservation_for_agent: Callable[[str], None]
    is_tile_blocked: Callable[[tuple[int, int]], bool]

    def apply(self, tick: int) -> list[str]:
        """Return agents home, refill needs, and reset employment context."""

        if not self.agents:
            return []

        reset_agents: list[str] = []
        for snapshot in list(self.agents.values()):
            previous_position = snapshot.position
            home = snapshot.home_position or snapshot.position
            target = home
            if target is not None and target != snapshot.position:
                occupied = any(
                    other.agent_id != snapshot.agent_id and other.position == target
                    for other in self.agents.values()
                )
                blocked = self.is_tile_blocked(target)
                if not occupied and not blocked:
                    self._release_queue_membership(snapshot.agent_id, tick)
                    snapshot.position = target
                    self.sync_reservation_for_agent(snapshot.agent_id)

            for need_name, value in snapshot.needs.items():
                snapshot.needs[need_name] = max(0.5, min(1.0, float(value)))

            snapshot.exit_pending = False
            snapshot.on_shift = False
            snapshot.shift_state = "pre_shift"
            snapshot.late_ticks_today = 0

            ctx = self.employment_service.get_context(snapshot.agent_id)
            ctx.update(
                {
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
                    "late_ticks": 0,
                    "shift_outcome_recorded": False,
                    "ever_on_time": False,
                    "late_counter_recorded": False,
                }
            )

            reset_agents.append(snapshot.agent_id)
            self.emit_event(
                "agent_nightly_reset",
                {
                    "agent_id": snapshot.agent_id,
                    "moved": snapshot.position != previous_position,
                    "home_position": list(snapshot.home_position)
                    if snapshot.home_position
                    else None,
                },
            )

        return reset_agents

    def _release_queue_membership(self, agent_id: str, tick: int) -> None:
        self.queue_manager.remove_agent(agent_id, tick)
        for object_id, occupant in list(self.active_reservations.items()):
            if occupant == agent_id:
                self.sync_reservation(object_id)


__all__ = ["NightlyResetService"]

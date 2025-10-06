"""Employment façade bridging coordinator and runtime services."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from townlet.world.employment_runtime import EmploymentRuntime
from townlet.world.employment_service import EmploymentCoordinator


@dataclass(slots=True)
class EmploymentService:
    """Simple façade bundling the employment coordinator and runtime."""

    coordinator: EmploymentCoordinator
    runtime: EmploymentRuntime

    def request_manual_exit(self, agent_id: str, tick: int) -> bool:
        return bool(self.runtime.request_manual_exit(agent_id, tick))

    def defer_exit(self, agent_id: str) -> bool:
        return bool(self.runtime.defer_exit(agent_id))

    def exits_today(self) -> int:
        return int(self.runtime.exits_today())

    def reset_exits_today(self) -> None:
        self.runtime.reset_exits_today()

    def increment_exits_today(self) -> None:
        self.runtime.increment_exits_today()

    def queue_snapshot(self) -> Mapping[str, object]:
        return self.runtime.queue_snapshot()

    def apply_job_state(self) -> None:
        self.runtime.apply_job_state()

    def assign_jobs_to_agents(self) -> None:
        self.runtime.assign_jobs_to_agents()

    def import_state(self, payload: Mapping[str, object]) -> None:
        self.coordinator.import_state(payload)

    def pending_agents(self) -> Iterable[str]:
        return self.runtime.pending_agents()


__all__ = ["EmploymentService"]

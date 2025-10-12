"""Employment façade bridging coordinator and runtime services."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from townlet.config import EmploymentConfig
from townlet.world.agents.snapshot import AgentSnapshot
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

    def set_exits_today(self, value: int) -> None:
        self.runtime.set_exits_today(value)

    def queue_snapshot(self) -> Mapping[str, object]:
        return self.runtime.queue_snapshot()

    def apply_job_state(self) -> None:
        self.runtime.apply_job_state()

    def assign_jobs_to_agents(self) -> None:
        self.runtime.assign_jobs_to_agents()

    def assign_job_if_missing(
        self,
        snapshot: AgentSnapshot,
        *,
        job_index: int | None = None,
    ) -> None:
        self.runtime.assign_job_if_missing(
            snapshot,
            job_index=job_index,
        )

    # Context helpers -------------------------------------------------
    def context_defaults(self) -> dict[str, Any]:
        return self.runtime.context_defaults()

    def get_context(self, agent_id: str) -> dict[str, Any]:
        return self.runtime.get_context(agent_id)

    def reset_context(self, agent_id: str) -> dict[str, Any]:
        return self.runtime.reset_context(agent_id)

    def context_wages(self, agent_id: str) -> float:
        return self.runtime.context_wages(agent_id)

    def context_punctuality(self, agent_id: str) -> float:
        return self.runtime.context_punctuality(agent_id)

    def remove_agent(self, agent_id: str) -> None:
        self.runtime.remove_agent(agent_id)

    # Shift lifecycle helpers ----------------------------------------
    def idle_state(self, snapshot: AgentSnapshot, ctx: dict[str, Any]) -> None:
        self.runtime.idle_state(snapshot, ctx)

    def prepare_state(self, snapshot: AgentSnapshot, ctx: dict[str, Any]) -> None:
        self.runtime.prepare_state(snapshot, ctx)

    def begin_shift(self, ctx: dict[str, Any], start: int, end: int) -> None:
        self.runtime.begin_shift(ctx, start, end)

    def determine_state(
        self,
        *,
        ctx: dict[str, Any],
        tick: int,
        start: int,
        at_required_location: bool,
        employment_cfg: EmploymentConfig,
    ) -> str:
        return self.runtime.determine_state(
            ctx=ctx,
            tick=tick,
            start=start,
            at_required_location=at_required_location,
            employment_cfg=employment_cfg,
        )

    def apply_state_effects(
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
        self.runtime.apply_state_effects(
            snapshot=snapshot,
            ctx=ctx,
            state=state,
            at_required_location=at_required_location,
            wage_rate=wage_rate,
            lateness_penalty=lateness_penalty,
            employment_cfg=employment_cfg,
        )

    def finalize_shift(
        self,
        *,
        snapshot: AgentSnapshot,
        ctx: dict[str, Any],
        employment_cfg: EmploymentConfig,
        job_id: str | None,
    ) -> None:
        self.runtime.finalize_shift(
            snapshot=snapshot,
            ctx=ctx,
            employment_cfg=employment_cfg,
            job_id=job_id,
        )

    def coworkers_on_shift(self, snapshot: AgentSnapshot) -> list[str]:
        return self.runtime.coworkers_on_shift(snapshot)

    def import_state(self, payload: Mapping[str, object]) -> None:
        self.coordinator.import_state(payload)

    def pending_agents(self) -> Iterable[str]:
        return self.runtime.pending_agents()


__all__ = ["EmploymentService"]

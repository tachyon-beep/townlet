"""Employment runtime facade for WorldState."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from townlet.config import EmploymentConfig
from townlet.world.employment_service import EmploymentCoordinator


@dataclass
class EmploymentRuntime:
    """Coordinates employment lifecycle and queue management for a world."""

    world: Any
    coordinator: EmploymentCoordinator
    emit_event: Callable[[str, dict[str, object]], None]

    # ------------------------------------------------------------------
    # High-level orchestration
    # ------------------------------------------------------------------
    def assign_jobs_to_agents(self) -> None:
        self.coordinator.assign_jobs_to_agents(self.world)

    def apply_job_state(self) -> None:
        self.coordinator.apply_job_state(self.world)

    # ------------------------------------------------------------------
    # Context helpers
    # ------------------------------------------------------------------
    def context_defaults(self) -> dict[str, Any]:
        return self.coordinator.context_defaults()

    def get_context(self, agent_id: str) -> dict[str, Any]:
        return self.coordinator.get_context(self.world, agent_id)

    def reset_context(self, agent_id: str) -> dict[str, Any]:
        return self.coordinator.reset_context(agent_id)

    def context_wages(self, agent_id: str) -> float:
        return self.coordinator.employment_context_wages(agent_id)

    def context_punctuality(self, agent_id: str) -> float:
        return self.coordinator.employment_context_punctuality(agent_id)

    def remove_agent(self, agent_id: str) -> None:
        self.coordinator.remove_agent(self.world, agent_id)

    # ------------------------------------------------------------------
    # Shift lifecycle helpers (delegating to EmploymentEngine internals)
    # ------------------------------------------------------------------
    def idle_state(self, snapshot: Any, ctx: dict[str, Any]) -> None:
        self.coordinator._employment_idle_state(self.world, snapshot, ctx)

    def prepare_state(self, snapshot: Any, ctx: dict[str, Any]) -> None:
        self.coordinator._employment_prepare_state(snapshot, ctx)

    def begin_shift(self, ctx: dict[str, Any], start: int, end: int) -> None:
        self.coordinator._employment_begin_shift(ctx, start, end)

    def determine_state(
        self,
        *,
        ctx: dict[str, Any],
        tick: int,
        start: int,
        at_required_location: bool,
        employment_cfg: EmploymentConfig,
    ) -> str:
        return self.coordinator._employment_determine_state(
            ctx=ctx,
            tick=tick,
            start=start,
            at_required_location=at_required_location,
            employment_cfg=employment_cfg,
        )

    def apply_state_effects(
        self,
        *,
        snapshot: Any,
        ctx: dict[str, Any],
        state: str,
        at_required_location: bool,
        wage_rate: float,
        lateness_penalty: float,
        employment_cfg: EmploymentConfig,
    ) -> None:
        self.coordinator._employment_apply_state_effects(
            world=self.world,
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
        snapshot: Any,
        ctx: dict[str, Any],
        employment_cfg: EmploymentConfig,
        job_id: str | None,
    ) -> None:
        self.coordinator._employment_finalize_shift(
            self.world,
            snapshot,
            ctx,
            employment_cfg,
            job_id,
        )

    def coworkers_on_shift(self, snapshot: Any) -> list[str]:
        return self.coordinator._employment_coworkers_on_shift(self.world, snapshot)

    # ------------------------------------------------------------------
    # Queue & exit helpers
    # ------------------------------------------------------------------
    def queue_snapshot(self) -> dict[str, Any]:
        return self.coordinator.queue_snapshot()

    def request_manual_exit(self, agent_id: str, tick: int) -> bool:
        return self.coordinator.request_manual_exit(self.world, agent_id, tick)

    def defer_exit(self, agent_id: str) -> bool:
        return self.coordinator.defer_exit(self.world, agent_id)

    def exits_today(self) -> int:
        return self.coordinator.exits_today

    def set_exits_today(self, value: int) -> None:
        self.coordinator.set_exits_today(value)

    def reset_exits_today(self) -> None:
        self.coordinator.reset_exits_today()

    def increment_exits_today(self) -> None:
        self.coordinator.increment_exits_today()

    def exit_queue_length(self) -> int:
        return self.coordinator.exit_queue_length()

    def exit_queue_members(self) -> list[str]:
        return self.coordinator.exit_queue_members()

    def assign_job_if_missing(
        self,
        snapshot: Any,
        *,
        job_index: int | None = None,
    ) -> None:
        self.coordinator.assign_job_if_missing(
            self.world,
            snapshot,
            job_index=job_index,
        )

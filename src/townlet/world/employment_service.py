"""Employment service abstraction extracted from WorldState."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from townlet.config import EmploymentConfig, SimulationConfig
from townlet.world.employment import EmploymentEngine


@dataclass
class EmploymentCoordinator:
    """Thin façade around the employment engine to simplify WorldState."""

    engine: EmploymentEngine

    def enqueue_exit(self, world: Any, agent_id: str, tick: int) -> None:
        self.engine.enqueue_exit(world, agent_id, tick)

    def remove_from_queue(self, world: Any, agent_id: str) -> None:
        self.engine.remove_from_queue(world, agent_id)

    def queue_snapshot(self) -> dict[str, Any]:
        return self.engine.queue_snapshot()

    def request_manual_exit(self, world: Any, agent_id: str, tick: int) -> bool:
        return self.engine.request_manual_exit(world, agent_id, tick)

    def defer_exit(self, world: Any, agent_id: str) -> bool:
        return self.engine.defer_exit(world, agent_id)

    def assign_jobs_to_agents(self, world: Any) -> None:
        self.engine.assign_jobs_to_agents(world)

    def apply_job_state(self, world: Any) -> None:
        self.engine.apply_job_state(world)

    def assign_job_if_missing(
        self,
        world: Any,
        snapshot: Any,
        *,
        job_index: int | None = None,
    ) -> None:
        self.engine.assign_job_if_missing(
            world,
            snapshot,
            job_index=job_index,
        )

    @property
    def exits_today(self) -> int:
        return self.engine.exits_today

    def set_exits_today(self, value: int) -> None:
        self.engine.set_exits_today(value)

    def reset_exits_today(self) -> None:
        self.engine.reset_exits_today()

    def increment_exits_today(self) -> None:
        self.engine.increment_exits_today()

    def get_context(self, world: Any, agent_id: str) -> dict[str, Any]:
        return self.engine.get_employment_context(world, agent_id)

    def context_defaults(self) -> dict[str, Any]:
        return self.engine.context_defaults()

    def remove_agent(self, world: Any, agent_id: str) -> None:
        self.engine.remove_from_queue(world, agent_id)
        self.engine.discard_manual_exit(agent_id)
        self.engine.clear_context(agent_id)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.engine, name)

    # -- queue & manual exit helpers -----------------------------------

    def manual_exit_agents(self) -> set[str]:
        return self.engine.manual_exit_agents()

    def discard_manual_exit(self, agent_id: str) -> None:
        self.engine.discard_manual_exit(agent_id)

    def exit_queue_members(self) -> list[str]:
        return self.engine.exit_queue_members()

    def exit_queue_head(self) -> str | None:
        return self.engine.exit_queue_head()

    def exit_queue_contains(self, agent_id: str) -> bool:
        return self.engine.exit_queue_contains(agent_id)

    def exit_queue_length(self) -> int:
        return self.engine.exit_queue_length()

    def exit_queue_enqueue_tick(self, agent_id: str) -> int | None:
        return self.engine.exit_queue_enqueue_tick(agent_id)

    def clear_context(self, agent_id: str) -> None:
        self.engine.clear_context(agent_id)

    def reset_context(self, agent_id: str) -> dict[str, Any]:
        return self.engine.reset_context(agent_id)

    def has_context(self, agent_id: str) -> bool:
        return self.engine.has_context(agent_id)

    def employment_context_wages(self, agent_id: str) -> float:
        return self.engine.employment_context_wages(agent_id)

    def employment_context_punctuality(self, agent_id: str) -> float:
        return self.engine.employment_context_punctuality(agent_id)

    # -- typed bridges for engine internals ---------------------------

    def employment_idle_state(
        self,
        world: Any,
        snapshot: Any,
        ctx: dict[str, Any],
    ) -> None:
        self.engine._employment_idle_state(world, snapshot, ctx)

    def employment_prepare_state(
        self,
        snapshot: Any,
        ctx: dict[str, Any],
    ) -> None:
        self.engine._employment_prepare_state(snapshot, ctx)

    def employment_begin_shift(
        self,
        ctx: dict[str, Any],
        start: int,
        end: int,
    ) -> None:
        self.engine._employment_begin_shift(ctx, start, end)

    def employment_determine_state(
        self,
        *,
        ctx: dict[str, Any],
        tick: int,
        start: int,
        at_required_location: bool,
        employment_cfg: EmploymentConfig,
    ) -> str:
        return self.engine._employment_determine_state(
            ctx=ctx,
            tick=tick,
            start=start,
            at_required_location=at_required_location,
            employment_cfg=employment_cfg,
        )

    def employment_apply_state_effects(
        self,
        *,
        world: Any,
        snapshot: Any,
        ctx: dict[str, Any],
        state: str,
        at_required_location: bool,
        wage_rate: float,
        lateness_penalty: float,
        employment_cfg: EmploymentConfig,
    ) -> None:
        self.engine._employment_apply_state_effects(
            world=world,
            snapshot=snapshot,
            ctx=ctx,
            state=state,
            at_required_location=at_required_location,
            wage_rate=wage_rate,
            lateness_penalty=lateness_penalty,
            employment_cfg=employment_cfg,
        )

    def employment_finalize_shift(
        self,
        *,
        world: Any,
        snapshot: Any,
        ctx: dict[str, Any],
        employment_cfg: EmploymentConfig,
        job_id: str | None,
    ) -> None:
        self.engine._employment_finalize_shift(
            world=world,
            snapshot=snapshot,
            ctx=ctx,
            employment_cfg=employment_cfg,
            job_id=job_id,
        )

    def employment_coworkers_on_shift(self, world: Any, snapshot: Any) -> list[str]:
        return self.engine._employment_coworkers_on_shift(world, snapshot)


def create_employment_coordinator(
    config: SimulationConfig,
    emit_event: Callable[[str, dict[str, object]], None],
) -> EmploymentCoordinator:
    engine = EmploymentEngine(config, emit_event)
    return EmploymentCoordinator(engine=engine)

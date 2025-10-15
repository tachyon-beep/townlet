"""Employment and nightly reset helpers."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from townlet.config import EmploymentConfig
from townlet.world.agents.employment import EmploymentService
from townlet.world.agents.nightly_reset import NightlyResetService
from townlet.world.agents.snapshot import AgentSnapshot

from .base import SystemContext

logger = logging.getLogger(__name__)


def step(ctx: SystemContext) -> None:
    """Advance employment scheduling and wage bookkeeping."""

    state = ctx.state
    service = getattr(state, "_employment_service", None)

    if service is None:
        coordinator = getattr(state, "employment", None)
        if coordinator is not None:
            apply_fn = getattr(coordinator, "apply_job_state", None)
            if callable(apply_fn):
                apply_fn(state)
                return
        logger.debug(
            "employment_step_skipped service_missing state=%s",
            type(state).__name__,
        )
        return

    assign_jobs(service)
    apply_job_state(service)


def nightly_reset(service: NightlyResetService, tick: int) -> list[str]:
    return service.apply(tick)


def assign_jobs(service: EmploymentService) -> None:
    service.assign_jobs_to_agents()


def apply_job_state(service: EmploymentService) -> None:
    service.apply_job_state()


def context_defaults(service: EmploymentService) -> dict[str, Any]:
    return service.context_defaults()


def get_context(service: EmploymentService, agent_id: str) -> dict[str, Any]:
    return service.get_context(agent_id)


def context_wages(service: EmploymentService, agent_id: str) -> float:
    return service.context_wages(agent_id)


def context_punctuality(service: EmploymentService, agent_id: str) -> float:
    return service.context_punctuality(agent_id)


def idle_state(service: EmploymentService, snapshot: AgentSnapshot, ctx: dict[str, Any]) -> None:
    service.idle_state(snapshot, ctx)


def prepare_state(service: EmploymentService, snapshot: AgentSnapshot, ctx: dict[str, Any]) -> None:
    service.prepare_state(snapshot, ctx)


def begin_shift(service: EmploymentService, ctx: dict[str, Any], start: int, end: int) -> None:
    service.begin_shift(ctx, start, end)


def determine_state(
    service: EmploymentService,
    *,
    ctx: dict[str, Any],
    tick: int,
    start: int,
    at_required_location: bool,
    employment_cfg: EmploymentConfig,
) -> str:
    return service.determine_state(
        ctx=ctx,
        tick=tick,
        start=start,
        at_required_location=at_required_location,
        employment_cfg=employment_cfg,
    )


def apply_state_effects(
    service: EmploymentService,
    *,
    snapshot: AgentSnapshot,
    ctx: dict[str, Any],
    state: str,
    at_required_location: bool,
    wage_rate: float,
    lateness_penalty: float,
    employment_cfg: EmploymentConfig,
) -> None:
    service.apply_state_effects(
        snapshot=snapshot,
        ctx=ctx,
        state=state,
        at_required_location=at_required_location,
        wage_rate=wage_rate,
        lateness_penalty=lateness_penalty,
        employment_cfg=employment_cfg,
    )


def finalize_shift(
    service: EmploymentService,
    *,
    snapshot: AgentSnapshot,
    ctx: dict[str, Any],
    employment_cfg: EmploymentConfig,
    job_id: str | None,
) -> None:
    service.finalize_shift(
        snapshot=snapshot,
        ctx=ctx,
        employment_cfg=employment_cfg,
        job_id=job_id,
    )


def coworkers_on_shift(service: EmploymentService, snapshot: AgentSnapshot) -> list[str]:
    return service.coworkers_on_shift(snapshot)


def queue_snapshot(service: EmploymentService) -> Mapping[str, object]:
    return service.queue_snapshot()


def request_manual_exit(service: EmploymentService, agent_id: str, tick: int) -> bool:
    return service.request_manual_exit(agent_id, tick)


def defer_exit(service: EmploymentService, agent_id: str) -> bool:
    return service.defer_exit(agent_id)


def exits_today(service: EmploymentService) -> int:
    return service.exits_today()


def set_exits_today(service: EmploymentService, value: int) -> None:
    service.set_exits_today(value)


def reset_exits_today(service: EmploymentService) -> None:
    service.reset_exits_today()


def increment_exits_today(service: EmploymentService) -> None:
    service.increment_exits_today()


__all__ = [
    "apply_job_state",
    "apply_state_effects",
    "assign_jobs",
    "begin_shift",
    "context_defaults",
    "context_punctuality",
    "context_wages",
    "coworkers_on_shift",
    "defer_exit",
    "determine_state",
    "exits_today",
    "finalize_shift",
    "get_context",
    "idle_state",
    "increment_exits_today",
    "nightly_reset",
    "prepare_state",
    "queue_snapshot",
    "request_manual_exit",
    "reset_exits_today",
    "set_exits_today",
    "step",
]

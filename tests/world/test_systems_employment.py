from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from townlet.world.systems import employment


class FakeEmploymentService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []

    def assign_jobs_to_agents(self) -> None:
        self.calls.append(("assign_jobs", (), {}))

    def apply_job_state(self) -> None:
        self.calls.append(("apply_job_state", (), {}))

    def context_defaults(self) -> dict[str, int]:
        self.calls.append(("context_defaults", (), {}))
        return {"foo": 1}

    def get_context(self, agent_id: str) -> dict[str, int]:
        self.calls.append(("get_context", (agent_id,), {}))
        return {"agent": agent_id}

    def context_wages(self, agent_id: str) -> float:
        self.calls.append(("context_wages", (agent_id,), {}))
        return 1.23

    def context_punctuality(self, agent_id: str) -> float:
        self.calls.append(("context_punctuality", (agent_id,), {}))
        return 0.5

    def idle_state(self, snapshot, ctx):
        self.calls.append(("idle_state", (snapshot, ctx), {}))

    def prepare_state(self, snapshot, ctx):
        self.calls.append(("prepare_state", (snapshot, ctx), {}))

    def begin_shift(self, ctx, start: int, end: int):
        self.calls.append(("begin_shift", (ctx, start, end), {}))

    def determine_state(self, **kwargs) -> str:
        self.calls.append(("determine_state", (), kwargs))
        return "pre_shift"

    def apply_state_effects(self, **kwargs) -> None:
        self.calls.append(("apply_state_effects", (), kwargs))

    def finalize_shift(self, **kwargs) -> None:
        self.calls.append(("finalize_shift", (), kwargs))

    def coworkers_on_shift(self, snapshot) -> list[str]:
        self.calls.append(("coworkers_on_shift", (snapshot,), {}))
        return ["bob"]

    def queue_snapshot(self) -> dict[str, int]:
        self.calls.append(("queue_snapshot", (), {}))
        return {"stall": 1}

    def request_manual_exit(self, agent_id: str, tick: int) -> bool:
        self.calls.append(("request_manual_exit", (agent_id, tick), {}))
        return True

    def defer_exit(self, agent_id: str) -> bool:
        self.calls.append(("defer_exit", (agent_id,), {}))
        return False

    def exits_today(self) -> int:
        self.calls.append(("exits_today", (), {}))
        return 2

    def set_exits_today(self, value: int) -> None:
        self.calls.append(("set_exits_today", (value,), {}))

    def reset_exits_today(self) -> None:
        self.calls.append(("reset_exits_today", (), {}))

    def increment_exits_today(self) -> None:
        self.calls.append(("increment_exits_today", (), {}))


class FakeNightlyReset:
    def __init__(self) -> None:
        self.calls: list[int] = []

    def apply(self, tick: int) -> list[str]:
        self.calls.append(tick)
        return ["alice"]


class FakeSnapshot(SimpleNamespace):
    pass


def test_nightly_reset_delegates() -> None:
    service = FakeNightlyReset()
    result = employment.nightly_reset(service, 42)

    assert result == ["alice"]
    assert service.calls == [42]


def test_assign_and_apply_job_state_delegate() -> None:
    service = FakeEmploymentService()
    employment.assign_jobs(service)
    employment.apply_job_state(service)

    assert service.calls[:2] == [("assign_jobs", (), {}), ("apply_job_state", (), {})]


def test_context_helpers_delegate() -> None:
    service = FakeEmploymentService()
    assert employment.context_defaults(service) == {"foo": 1}
    assert employment.get_context(service, "alice") == {"agent": "alice"}
    assert employment.context_wages(service, "alice") == 1.23
    assert employment.context_punctuality(service, "alice") == 0.5


def test_shift_helpers_delegate() -> None:
    service = FakeEmploymentService()
    snapshot = FakeSnapshot(agent_id="alice")
    ctx: dict[str, Any] = {}
    employment.idle_state(service, snapshot, ctx)
    employment.prepare_state(service, snapshot, ctx)
    employment.begin_shift(service, ctx, 1, 2)
    state = employment.determine_state(
        service,
        ctx=ctx,
        tick=5,
        start=1,
        at_required_location=True,
        employment_cfg=SimpleNamespace(),
    )
    employment.apply_state_effects(
        service,
        snapshot=snapshot,
        ctx=ctx,
        state=state,
        at_required_location=True,
        wage_rate=1.0,
        lateness_penalty=0.0,
        employment_cfg=SimpleNamespace(),
    )
    employment.finalize_shift(
        service,
        snapshot=snapshot,
        ctx=ctx,
        employment_cfg=SimpleNamespace(),
        job_id="chef",
    )
    coworkers = employment.coworkers_on_shift(service, snapshot)

    assert coworkers == ["bob"]


def test_queue_and_exit_helpers_delegate() -> None:
    service = FakeEmploymentService()
    employment.queue_snapshot(service)
    employment.request_manual_exit(service, "alice", 10)
    employment.defer_exit(service, "alice")
    employment.exits_today(service)
    employment.set_exits_today(service, 3)
    employment.reset_exits_today(service)
    employment.increment_exits_today(service)

    calls = [name for name, _, _ in service.calls[-7:]]
    assert calls == [
        "queue_snapshot",
        "request_manual_exit",
        "defer_exit",
        "exits_today",
        "set_exits_today",
        "reset_exits_today",
        "increment_exits_today",
    ]


__all__ = []

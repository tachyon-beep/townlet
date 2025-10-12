from __future__ import annotations

from types import SimpleNamespace

from townlet.world.events import EventDispatcher
from townlet.world.rng import RngStreamManager
from townlet.world.systems import SystemContext, employment


def _make_context(state: object) -> SystemContext:
    return SystemContext(
        state=state,  # type: ignore[arg-type]
        rng=RngStreamManager.from_seed(123),
        events=EventDispatcher(),
    )


def test_step_calls_service_methods() -> None:
    calls: list[str] = []

    class DummyService:
        def assign_jobs_to_agents(self) -> None:
            calls.append("assign")

        def apply_job_state(self) -> None:
            calls.append("apply")

    state = SimpleNamespace(_employment_service=DummyService())

    employment.step(_make_context(state))

    assert calls == ["assign", "apply"]


def test_step_falls_back_to_legacy_method() -> None:
    calls: list[str] = []

    class LegacyState:
        def __init__(self) -> None:
            self._employment_service = None
            self.employment = SimpleNamespace(
                apply_job_state=lambda world: calls.append("legacy")
            )

    state = LegacyState()

    employment.step(_make_context(state))

    assert calls == ["legacy"]

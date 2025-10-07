from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world.core.runtime_adapter import WorldRuntimeAdapter


def _make_world():
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.world.agents.clear()
    return loop.world


def test_apply_nightly_reset_delegates_to_service() -> None:
    world = _make_world()
    sentinel = Mock(return_value=["alice"])
    world._nightly_reset_service = Mock(apply=sentinel)  # type: ignore[attr-defined]
    world.tick = 42

    result = world.apply_nightly_reset()

    sentinel.assert_called_once_with(42)
    assert result == ["alice"]


def test_assign_jobs_uses_employment_service() -> None:
    world = _make_world()
    world._employment_service = Mock(wraps=world._employment_service)  # type: ignore[attr-defined]

    world.assign_jobs_to_agents()

    world._employment_service.assign_jobs_to_agents.assert_called_once()  # type: ignore[attr-defined]


def test_employment_queue_and_exit_helpers_delegate() -> None:
    world = _make_world()
    service = Mock()
    service.queue_snapshot.return_value = {"pending_count": 0}
    service.request_manual_exit.return_value = True
    service.defer_exit.return_value = False
    service.exits_today.return_value = 3
    world._employment_service = service  # type: ignore[attr-defined]

    assert world.employment_queue_snapshot() == {"pending_count": 0}
    service.queue_snapshot.assert_called_once()

    assert world.employment_request_manual_exit("bob", 10)
    service.request_manual_exit.assert_called_once_with("bob", 10)

    assert world.employment_defer_exit("bob") is False
    service.defer_exit.assert_called_once_with("bob")

    assert world.employment_exits_today() == 3
    service.exits_today.assert_called_once()

    world.set_employment_exits_today(4)
    service.set_exits_today.assert_called_once_with(4)

    world.reset_employment_exits_today()
    service.reset_exits_today.assert_called_once()

    world.increment_employment_exits_today()
    service.increment_exits_today.assert_called_once()


def test_runtime_adapter_employment_hooks_delegate() -> None:
    world = _make_world()
    service = Mock()
    service.context_wages.return_value = 1.23
    service.context_punctuality.return_value = 0.45
    world._employment_service = service  # type: ignore[attr-defined]

    adapter = WorldRuntimeAdapter(world)

    assert adapter._employment_context_wages("alice") == 1.23
    service.context_wages.assert_called_once_with("alice")

    assert adapter._employment_context_punctuality("alice") == 0.45
    service.context_punctuality.assert_called_once_with("alice")

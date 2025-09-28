from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.console.handlers import ConsoleCommand, create_console_router
from townlet.core.sim_loop import SimulationLoop


@pytest.fixture()
def admin_router() -> tuple[SimulationLoop, object]:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    router = create_console_router(
        loop.telemetry,
        loop.world,
        promotion=loop.promotion,
        scheduler=loop.perturbations,
        mode="admin",
        config=config,
    )
    return loop, router


def make_ready(loop: SimulationLoop) -> None:
    loop.promotion.update_from_metrics(
        {
            "promotion": {
                "pass_streak": 2,
                "required_passes": 2,
                "candidate_ready": True,
                "last_result": "pass",
                "last_evaluated_tick": loop.tick,
            }
        },
        tick=loop.tick,
    )


def test_promotion_status_command(admin_router: tuple[SimulationLoop, object]) -> None:
    loop, router = admin_router
    response = router.dispatch(ConsoleCommand(name="promotion_status", args=(), kwargs={}))
    assert "promotion" in response


def test_promote_and_rollback_commands(admin_router: tuple[SimulationLoop, object]) -> None:
    loop, router = admin_router
    make_ready(loop)
    promote_response = router.dispatch(
        ConsoleCommand(
            name="promote_policy",
            args=("checkpoint.pt",),
            kwargs={"cmd_id": "42", "policy_hash": "abc123"},
        )
    )
    assert promote_response["cmd_id"] == "42"
    assert promote_response["promoted"] is True
    promoted_state = promote_response["promotion"]
    assert promoted_state["state"] == "promoted"
    assert promoted_state["current_release"]["policy_hash"] == "abc123"

    rollback_response = router.dispatch(
        ConsoleCommand(
            name="rollback_policy",
            args=(),
            kwargs={"reason": "canary_trigger"},
        )
    )
    assert rollback_response["rolled_back"] is True
    rolled_back_state = rollback_response["promotion"]
    assert rolled_back_state["state"] == "monitoring"
    assert rolled_back_state["current_release"].get("reason") == "canary_trigger"


@pytest.fixture()
def viewer_router() -> object:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    return create_console_router(
        loop.telemetry,
        loop.world,
        promotion=loop.promotion,
        scheduler=loop.perturbations,
        mode="viewer",
        config=config,
    )


def test_viewer_mode_forbidden(viewer_router: object) -> None:
    response = viewer_router.dispatch(ConsoleCommand(name="promote_policy", args=(), kwargs={}))
    assert response["error"] == "forbidden"

from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import (
    ConsoleAuthConfig,
    ConsoleAuthTokenConfig,
    load_config,
)
from townlet.console.handlers import ConsoleCommand, create_console_router
from townlet.core.sim_loop import SimulationLoop
from townlet.world.grid import AgentSnapshot

ADMIN_TOKEN = "admin-token"
VIEWER_TOKEN = "viewer-token"


@pytest.fixture()
def employment_loop() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.employment.enforce_job_loop = True
    config = config.model_copy(
        update={
            "console_auth": ConsoleAuthConfig(
                enabled=True,
                require_auth_for_viewer=False,
                tokens=[
                    ConsoleAuthTokenConfig(token=VIEWER_TOKEN, role="viewer", label="viewer"),
                    ConsoleAuthTokenConfig(token=ADMIN_TOKEN, role="admin", label="admin"),
                ],
            )
        }
    )
    loop = SimulationLoop(config)
    loop.world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    loop.world._assign_jobs_to_agents()  # type: ignore[attr-defined]
    return loop


def _queue_command(loop: SimulationLoop, payload: dict[str, object]) -> None:
    if "auth" not in payload:
        token = VIEWER_TOKEN
        if payload.get("mode") == "admin":
            token = ADMIN_TOKEN
        payload = {**payload, "auth": {"token": token}}
    loop.telemetry.queue_console_command(payload)


def test_dispatcher_processes_employment_review(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    loop.world._employment_enqueue_exit("alice", loop.world.tick)
    _queue_command(
        loop,
        {
            "name": "employment_exit",
            "args": ["review"],
            "mode": "admin",
            "cmd_id": "cmd-1",
        },
    )
    loop.step()
    results = loop.telemetry.latest_console_results()
    assert results, "expected command result"
    review = results[-1]
    assert review["status"] == "ok"
    assert review["result"].get("pending_count") == 1


def test_dispatcher_idempotency_reuses_history(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    payload = {
        "name": "employment_exit",
        "args": ["defer", "alice"],
        "mode": "admin",
        "cmd_id": "repeat-1",
    }
    loop.world._employment_enqueue_exit("alice", loop.world.tick)
    _queue_command(loop, payload)
    _queue_command(loop, payload)
    loop.step()
    results = loop.telemetry.latest_console_results()
    assert len(results) == 2
    # first command dequeues agent
    assert results[0]["status"] == "ok"
    assert results[0]["result"]["deferred"] is True
    # duplicate should not enqueue a second defer action
    assert results[1]["status"] == "ok"
    assert loop.world.employment_queue_snapshot()["pending_count"] == 0


def test_dispatcher_requires_admin_mode(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    loop.world._employment_enqueue_exit("alice", loop.world.tick)
    _queue_command(
        loop,
        {
            "name": "employment_exit",
            "args": ["review"],
            "mode": "viewer",
            "cmd_id": "cmd-viewer",
        },
    )
    loop.step()
    results = loop.telemetry.latest_console_results()
    assert results
    error = results[-1]
    assert error["status"] == "error"
    assert error["error"]["code"] == "forbidden"


def test_dispatcher_enforces_cmd_id_for_destructive_ops(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    _queue_command(
        loop,
        {
            "name": "employment_exit",
            "args": ["approve", "alice"],
            "mode": "admin",
        },
    )
    loop.step()
    results = loop.telemetry.latest_console_results()
    assert results
    error = results[-1]
    assert error["status"] == "error"
    assert error["error"]["code"] == "usage"


def test_spawn_command_creates_agent(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    payload = {
        "name": "spawn",
        "mode": "admin",
        "cmd_id": "spawn-1",
        "kwargs": {
            "payload": {
                "agent_id": "carol",
                "position": [5, 2],
                "wallet": 3.5,
            }
        },
    }
    _queue_command(loop, payload)
    loop.step()
    results = loop.telemetry.latest_console_results()
    assert results[-1]["status"] == "ok"
    assert loop.world.agents["carol"].position == (5, 2)
    assert loop.world.agents["carol"].wallet == 3.5


def test_spawn_rejects_duplicate_id(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    _queue_command(
        loop,
        {
            "name": "spawn",
            "mode": "admin",
            "cmd_id": "spawn-dup",
            "kwargs": {"payload": {"agent_id": "alice", "position": [0, 1]}},
        },
    )
    loop.step()
    error = loop.telemetry.latest_console_results()[-1]
    assert error["status"] == "error"
    assert error["error"]["code"] == "conflict"


def test_teleport_moves_agent(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    payload = {
        "name": "teleport",
        "mode": "admin",
        "cmd_id": "teleport-1",
        "kwargs": {"payload": {"agent_id": "alice", "position": [3, 4]}},
    }
    _queue_command(loop, payload)
    loop.step()
    result = loop.telemetry.latest_console_results()[-1]
    assert result["status"] == "ok"
    assert loop.world.agents["alice"].position == (3, 4)


def test_teleport_rejects_blocked_tile(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    loop.world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(1, 1),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=0.0,
    )
    payload = {
        "name": "teleport",
        "mode": "admin",
        "cmd_id": "teleport-block",
        "kwargs": {"payload": {"agent_id": "alice", "position": [1, 1]}},
    }
    _queue_command(loop, payload)
    loop.step()
    result = loop.telemetry.latest_console_results()[-1]
    assert result["status"] == "error"
    assert result["error"]["code"] == "invalid_args"


def test_setneed_updates_needs(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    payload = {
        "name": "setneed",
        "mode": "admin",
        "cmd_id": "setneed-1",
        "kwargs": {
            "payload": {
                "agent_id": "alice",
                "needs": {"hunger": 0.9, "energy": -0.2},
            }
        },
    }
    _queue_command(loop, payload)
    loop.step()
    result = loop.telemetry.latest_console_results()[-1]
    assert result["status"] == "ok"
    needs = result["result"]["needs"]
    assert needs["hunger"] == pytest.approx(0.9)
    assert needs["energy"] == pytest.approx(0.0)
    assert loop.world.agents["alice"].needs["energy"] == pytest.approx(0.0)


def test_setneed_rejects_unknown_need(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    payload = {
        "name": "setneed",
        "mode": "admin",
        "cmd_id": "setneed-bad",
        "kwargs": {
            "payload": {
                "agent_id": "alice",
                "needs": {"unknown": 0.5},
            }
        },
    }
    _queue_command(loop, payload)
    loop.step()
    result = loop.telemetry.latest_console_results()[-1]
    assert result["status"] == "error"
    assert result["error"]["code"] == "invalid_args"


def test_price_updates_economy_and_basket(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    payload = {
        "name": "price",
        "mode": "admin",
        "cmd_id": "price-1",
        "kwargs": {"payload": {"key": "meal_cost", "value": 0.8}},
    }
    _queue_command(loop, payload)
    loop.step()
    result = loop.telemetry.latest_console_results()[-1]
    assert result["status"] == "ok"
    assert loop.config.economy["meal_cost"] == pytest.approx(0.8)
    basket = loop.world.agents["alice"].inventory.get("basket_cost")
    assert basket == pytest.approx(
        loop.config.economy["meal_cost"]
        + loop.config.economy["cook_energy_cost"]
        + loop.config.economy["cook_hygiene_cost"]
        + loop.config.economy["ingredients_cost"]
    )


def test_price_rejects_unknown_key(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    payload = {
        "name": "price",
        "mode": "admin",
        "cmd_id": "price-bad",
        "kwargs": {"payload": {"key": "invalid", "value": 1.0}},
    }
    _queue_command(loop, payload)
    loop.step()
    result = loop.telemetry.latest_console_results()[-1]
    assert result["status"] == "error"
    assert result["error"]["code"] == "not_found"


def test_force_chat_updates_relationship(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    payload = {
        "name": "force_chat",
        "mode": "admin",
        "cmd_id": "chat-1",
        "kwargs": {
            "payload": {
                "speaker": "alice",
                "listener": "alice2",
                "quality": 0.6,
            }
        },
    }
    loop.world.agents["alice2"] = AgentSnapshot(
        agent_id="alice2",
        position=(2, 2),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=0.0,
    )
    _queue_command(loop, payload)
    loop.step()
    result = loop.telemetry.latest_console_results()[-1]
    assert result["status"] == "ok"
    tie = loop.world.relationship_tie("alice", "alice2")
    assert tie is not None
    assert tie.trust > 0
    assert result["result"]["speaker_tie"]["trust"] == pytest.approx(tie.trust)


def test_force_chat_requires_distinct_agents(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    payload = {
        "name": "force_chat",
        "mode": "admin",
        "cmd_id": "chat-err",
        "kwargs": {"payload": {"speaker": "alice", "listener": "alice"}},
    }
    _queue_command(loop, payload)
    loop.step()
    result = loop.telemetry.latest_console_results()[-1]
    assert result["status"] == "error"
    assert result["error"]["code"] == "invalid_args"


def test_set_rel_updates_ties(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    loop.world.agents["carol"] = AgentSnapshot(
        agent_id="carol",
        position=(2, 3),
        needs={"hunger": 0.6, "hygiene": 0.6, "energy": 0.6},
        wallet=0.0,
    )
    payload = {
        "name": "set_rel",
        "mode": "admin",
        "cmd_id": "rel-1",
        "kwargs": {
            "payload": {
                "agent_a": "alice",
                "agent_b": "carol",
                "trust": 0.4,
                "rivalry": 0.2,
            }
        },
    }
    _queue_command(loop, payload)
    loop.step()
    result = loop.telemetry.latest_console_results()[-1]
    assert result["status"] == "ok"
    tie = loop.world.relationship_tie("alice", "carol")
    assert tie is not None
    assert tie.trust == pytest.approx(0.4)
    assert tie.rivalry == pytest.approx(0.2)


def test_possess_acquire_and_release(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    router = create_console_router(
        loop.telemetry,
        loop.world,
        loop.perturbations,
        policy=loop.policy,
        config=loop.config,
        mode="admin",
        lifecycle=loop.lifecycle,
    )
    acquire = router.dispatch(
        ConsoleCommand(
            name="possess",
            args=(),
            kwargs={"payload": {"agent_id": "alice", "action": "acquire"}},
        )
    )
    assert acquire["possessed"] is True
    assert loop.policy.is_possessed("alice")

    release = router.dispatch(
        ConsoleCommand(
            name="possess",
            args=(),
            kwargs={"payload": {"agent_id": "alice", "action": "release"}},
        )
    )
    assert release["possessed"] is False
    assert not loop.policy.is_possessed("alice")


def test_possess_errors_on_duplicate_or_missing(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    router = create_console_router(
        loop.telemetry,
        loop.world,
        loop.perturbations,
        policy=loop.policy,
        config=loop.config,
        mode="admin",
        lifecycle=loop.lifecycle,
    )
    router.dispatch(
        ConsoleCommand(
            name="possess",
            args=(),
            kwargs={"payload": {"agent_id": "alice", "action": "acquire"}},
        )
    )
    duplicate = router.dispatch(
        ConsoleCommand(
            name="possess",
            args=(),
            kwargs={"payload": {"agent_id": "alice", "action": "acquire"}},
        )
    )
    assert duplicate["error"] == "conflict"

    router.dispatch(
        ConsoleCommand(
            name="possess",
            args=(),
            kwargs={"payload": {"agent_id": "alice", "action": "release"}},
        )
    )
    release_err = router.dispatch(
        ConsoleCommand(
            name="possess",
            args=(),
            kwargs={"payload": {"agent_id": "alice", "action": "release"}},
        )
    )
    assert release_err["error"] == "invalid_args"


def test_kill_command_removes_agent(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    router = create_console_router(
        loop.telemetry,
        loop.world,
        loop.perturbations,
        policy=loop.policy,
        config=loop.config,
        mode="admin",
        lifecycle=loop.lifecycle,
    )
    result = router.dispatch(
        ConsoleCommand(
            name="kill",
            args=(),
            kwargs={"payload": {"agent_id": "alice", "reason": "test"}},
        )
    )
    assert result["killed"] is True
    assert "alice" not in loop.world.agents


def test_toggle_mortality_updates_flag(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    router = create_console_router(
        loop.telemetry,
        loop.world,
        loop.perturbations,
        policy=loop.policy,
        config=loop.config,
        mode="admin",
        lifecycle=loop.lifecycle,
    )
    result = router.dispatch(
        ConsoleCommand(
            name="toggle_mortality",
            args=(),
            kwargs={"payload": {"enabled": False}},
        )
    )
    assert result["enabled"] is False
    assert loop.lifecycle.mortality_enabled is False


def test_set_exit_cap_updates_config(employment_loop: SimulationLoop) -> None:
    loop = employment_loop
    router = create_console_router(
        loop.telemetry,
        loop.world,
        loop.perturbations,
        policy=loop.policy,
        config=loop.config,
        mode="admin",
        lifecycle=loop.lifecycle,
    )
    result = router.dispatch(
        ConsoleCommand(
            name="set_exit_cap",
            args=(),
            kwargs={"payload": {"daily_exit_cap": 5}},
        )
    )
    assert loop.config.employment.daily_exit_cap == 5
    assert result["metrics"]["daily_exit_cap"] == 5

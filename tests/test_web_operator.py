from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from pathlib import Path

from townlet.config import load_config
from townlet.console.handlers import ConsoleCommand, create_console_router
from townlet.core.sim_loop import SimulationLoop
from townlet.web.gateway import create_app


@pytest.fixture()
def simulation_loop() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    return SimulationLoop(config)


def _dispatch_factory(loop: SimulationLoop) -> dict[str, Any]:
    router = create_console_router(loop.telemetry, loop.world, policy=loop.policy, promotion=loop.promotion, config=loop.config)

    def dispatch(payload: dict[str, Any]) -> dict[str, Any]:
        command = ConsoleCommand(
            name=str(payload.get("name")),
            args=tuple(payload.get("args", ())),
            kwargs=dict(payload.get("kwargs", {}))
        )
        result = router.dispatch(command)
        return {"result": result}

    def status_provider() -> dict[str, Any]:
        snapshot = router.dispatch(ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={}))
        history = snapshot.get("console_results", [])
        return {
            "history": history[-5:],
            "commands": list(snapshot.get("console_commands", {}).keys()),
        }

    return {
        "dispatch": dispatch,
        "status_provider": status_provider,
    }


def _empty_stream() -> AsyncIterator[dict[str, Any]]:
    async def _gen() -> AsyncIterator[dict[str, Any]]:
        if False:
            yield {}
    return _gen()


def _token_validator(expected: str):
    return lambda token: token == expected


def test_operator_requires_token(simulation_loop: SimulationLoop) -> None:
    config = _dispatch_factory(simulation_loop)
    app = create_app(
        _empty_stream,
        operator_config={
            "token_validator": _token_validator("secret"),
            "dispatch": config["dispatch"],
            "status_provider": config["status_provider"],
        },
    )
    client = TestClient(app)

    with pytest.raises(Exception):
        with client.websocket_connect("/ws/operator?token=wrong"):
            pass


def test_operator_dispatches_command(simulation_loop: SimulationLoop) -> None:
    config = _dispatch_factory(simulation_loop)
    app = create_app(
        _empty_stream,
        operator_config={
            "token_validator": _token_validator("secret"),
            "dispatch": config["dispatch"],
            "status_provider": config["status_provider"],
        },
    )
    client = TestClient(app)

    with client.websocket_connect("/ws/operator?token=secret") as ws:
        initial = ws.receive_json()
        assert initial["type"] == "status"
        ws.send_json(
            {
                "type": "command",
                "payload": {
                    "name": "relationship_summary",
                    "args": (),
                    "kwargs": {},
                },
            }
        )
        ack = ws.receive_json()
        assert ack["type"] == "command_ack"
        assert ack["status"] == "ok"
        status = ws.receive_json()
        assert status["type"] == "status"
        assert "history" in status

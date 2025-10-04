from __future__ import annotations

import logging
from dataclasses import dataclass

import pytest

from townlet.console.command import ConsoleCommandError, ConsoleCommandResult
from townlet.world.console_bridge import ConsoleBridge


@dataclass
class _StubWorld:
    tick: int = 0


@pytest.fixture()
def bridge() -> ConsoleBridge:
    return ConsoleBridge(world=_StubWorld(), history_limit=4, buffer_limit=8)


def _result_ok(envelope) -> ConsoleCommandResult:
    return ConsoleCommandResult.ok(envelope, {"echo": envelope.name})


def test_unknown_command_returns_error(bridge: ConsoleBridge) -> None:
    bridge.apply([{"name": "not_registered"}])
    results = bridge.consume_results()
    assert len(results) == 1
    error = results[0]
    assert error.status == "error"
    assert error.error == {
        "code": "unsupported",
        "message": "Unknown console command 'not_registered'",
    }


def test_admin_mode_required(caplog: pytest.LogCaptureFixture, bridge: ConsoleBridge) -> None:
    bridge.register_handler("secure", _result_ok, mode="admin")
    bridge.apply([
        {
            "name": "secure",
            "mode": "viewer",
        }
    ])
    results = bridge.consume_results()
    assert results and results[0].error["code"] == "forbidden"
    assert not caplog.records  # no unexpected logging


def test_handler_exception_emits_internal_error(caplog: pytest.LogCaptureFixture, bridge: ConsoleBridge) -> None:
    def boom(_envelope):
        raise RuntimeError("boom")

    bridge.register_handler("fail", boom)
    with caplog.at_level(logging.ERROR, logger="townlet.world.console_bridge"):
        bridge.apply([{"name": "fail"}])
    records = [record for record in caplog.records if record.name == "townlet.world.console_bridge"]
    assert records and "failed" in records[0].message
    results = bridge.consume_results()
    assert results[0].error["code"] == "internal"
    assert "boom" in results[0].error["details"]["exception"]


def test_console_command_error_propagates_details(bridge: ConsoleBridge) -> None:
    def oops(_envelope):
        raise ConsoleCommandError("usage", "bad args", details={"hint": "fix"})

    bridge.register_handler("oops", oops)
    bridge.apply([{"name": "oops"}])
    result = bridge.consume_results()[0]
    assert result.error == {
        "code": "usage",
        "message": "bad args",
        "details": {"hint": "fix"},
    }


def test_require_cmd_id_enforced(bridge: ConsoleBridge) -> None:
    bridge.register_handler("danger", _result_ok, mode="admin", require_cmd_id=True)
    bridge.apply([
        {
            "name": "danger",
            "mode": "admin",
        }
    ])
    result = bridge.consume_results()[0]
    assert result.error["code"] == "usage"


def test_cached_result_reuses_latest_tick(bridge: ConsoleBridge) -> None:
    bridge.register_handler("noop", _result_ok, mode="admin")
    payload = {"name": "noop", "mode": "admin", "cmd_id": "repeat"}
    bridge.apply([payload])
    first = bridge.consume_results()[0]
    assert first.status == "ok"

    stub_world = bridge._world
    stub_world.tick = 42
    bridge.apply([payload])
    cached = bridge.consume_results()[0]
    assert cached.status == "ok"
    assert cached.tick == 42
    assert cached.cmd_id == "repeat"


def test_record_result_limits_history(bridge: ConsoleBridge) -> None:
    bridge.register_handler("hist", _result_ok)
    for index in range(6):
        cmd_id = f"cmd-{index}"
        bridge.apply([
            {
                "name": "hist",
                "cmd_id": cmd_id,
            }
        ])
        bridge.consume_results()
    assert len(bridge._cmd_history) <= 4
    # newest entry retained
    assert bridge.cached_result("cmd-5") is not None

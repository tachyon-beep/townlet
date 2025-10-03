from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from townlet.web.gateway import ReplayStreamFactory, create_app

FIXTURE_DIR = Path("tests/data/web_telemetry")


def _load(name: str) -> dict:
    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _normalize(message: dict) -> dict:
    result = dict(message)
    result.pop("payload_type", None)
    return result


def test_gateway_streams_snapshot_and_diff() -> None:
    snapshot = _load("snapshot.json")
    diff = _load("diff.json")
    stream = ReplayStreamFactory([snapshot, diff], repeat_last=False)
    app = create_app(stream)
    client = TestClient(app)

    with client.websocket_connect("/ws/telemetry") as ws:
        first = ws.receive_json()
        second = ws.receive_json()

    assert _normalize(first) == _normalize(snapshot)
    assert _normalize(second) == _normalize(diff)

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "townlet_web_ws_messages_total" in metrics.text


def test_gateway_skips_stale_ticks() -> None:
    snapshot = _load("snapshot.json")
    diff = _load("diff.json")
    snapshot_with_tick = dict(snapshot)
    snapshot_with_tick["tick"] = 100
    current_diff = dict(diff)
    current_diff["tick"] = 101
    stale = dict(diff)
    stale["tick"] = 90
    stream = ReplayStreamFactory([snapshot_with_tick, stale, current_diff], repeat_last=False)
    app = create_app(stream)
    client = TestClient(app)

    with client.websocket_connect("/ws/telemetry") as ws:
        first = ws.receive_json()
        second = ws.receive_json()

    assert _normalize(first) == _normalize(snapshot_with_tick)
    # stale payload should have been ignored, so the next message equals the non-stale diff
    assert _normalize(second) == _normalize(current_diff)


def test_gateway_handles_multiple_connections() -> None:
    snapshot = _load("snapshot.json")
    diff = _load("diff.json")
    stream = ReplayStreamFactory([snapshot, diff])
    app = create_app(stream)
    client = TestClient(app)

    for _ in range(2):
        with client.websocket_connect("/ws/telemetry") as ws:
            ws.receive_json()
            ws.receive_json()

    metrics = client.get("/metrics")
    assert metrics.status_code == 200


def test_gateway_rejects_operator_mode_without_auth() -> None:
    snapshot = _load("snapshot.json")
    diff = _load("diff.json")
    stream = ReplayStreamFactory([snapshot, diff])
    app = create_app(stream)
    client = TestClient(app)

    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/telemetry?mode=operator"):
            pass

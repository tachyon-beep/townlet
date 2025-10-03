"""FastAPI WebSocket gateway that streams telemetry snapshots/diffs to web clients."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Callable
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest

from townlet_ui.telemetry import TelemetryClient

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

CONNECTED_CLIENTS = Gauge(
    "townlet_web_ws_connections",
    "Number of active telemetry WebSocket connections",
)
MESSAGES_SENT = Counter(
    "townlet_web_ws_messages_total",
    "Count of telemetry messages sent to web clients",
    labelnames=("type",),
)


class TelemetryGateway:
    """WebSocket handler that streams telemetry snapshots and diffs."""

    def __init__(
        self,
        stream_factory: Callable[[], AsyncIterator[dict[str, Any]]],
        *,
        heartbeat_interval: float = 30.0,
    ) -> None:
        self._stream_factory = stream_factory
        # Parameter kept for future compatibility; currently no-op until heartbeat support lands.
        self._heartbeat_interval = heartbeat_interval

    async def websocket_handler(self, websocket: WebSocket) -> None:
        mode = websocket.query_params.get("mode", "spectator")
        _token = websocket.query_params.get("token")  # placeholder for future auth integration
        if mode != "spectator":
            await websocket.close(code=4403)
            return

        await websocket.accept()
        CONNECTED_CLIENTS.inc()
        stream = self._stream_factory()
        last_tick: int | None = None
        try:
            async for message in stream:
                if not isinstance(message, dict):
                    raise TypeError("Telemetry stream must yield dict payloads")

                payload = dict(message)
                payload.setdefault("payload_type", "snapshot")
                tick = payload.get("tick")
                if isinstance(tick, (int, float)):
                    tick_int = int(tick)
                    if last_tick is not None and tick_int < last_tick:
                        # drop stale payloads but continue streaming
                        continue
                    last_tick = tick_int

                await websocket.send_json(payload)
                MESSAGES_SENT.labels(type=payload["payload_type"]).inc()
        except WebSocketDisconnect:
            pass
        finally:
            CONNECTED_CLIENTS.dec()
            await self._close_stream(stream)

    async def metrics_endpoint(self) -> Response:
        payload = generate_latest()
        return Response(payload, media_type=CONTENT_TYPE_LATEST)

    @staticmethod
    async def _close_stream(stream: AsyncIterator[dict[str, Any]]) -> None:
        close = getattr(stream, "aclose", None)
        if close is None:
            return
        await close()


def create_app(
    stream_factory: Callable[[], AsyncIterator[dict[str, Any]]],
    *,
    heartbeat_interval: float = 30.0,
) -> FastAPI:
    """Construct a FastAPI app exposing telemetry over WebSocket."""

    gateway = TelemetryGateway(stream_factory, heartbeat_interval=heartbeat_interval)
    app = FastAPI()

    @app.websocket("/ws/telemetry")
    async def _telemetry_ws(websocket: WebSocket) -> None:  # pragma: no cover - wrapper
        await gateway.websocket_handler(websocket)

    @app.get("/metrics")
    async def _metrics() -> Response:  # pragma: no cover - wrapper
        return await gateway.metrics_endpoint()

    @app.get("/health")
    async def _health() -> dict[str, str]:
        return {"status": "ok"}

    app.state.telemetry_gateway = gateway
    return app


class ReplayStreamFactory:
    """Utility factory that replays stored telemetry payloads for testing/dev."""

    def __init__(self, messages: list[dict[str, Any]], *, repeat_last: bool = True) -> None:
        self._messages = [json.loads(json.dumps(message)) for message in messages]
        self._repeat_last = repeat_last

    def __call__(self) -> AsyncIterator[dict[str, Any]]:
        async def _iterator() -> AsyncIterator[dict[str, Any]]:
            for message in self._messages:
                yield json.loads(json.dumps(message))
                await asyncio.sleep(0)
            if self._repeat_last and self._messages:
                while True:
                    await asyncio.sleep(self._heartbeat_sleep())
                    yield json.loads(json.dumps(self._messages[-1]))

        return _iterator()

    def _heartbeat_sleep(self) -> float:
        # small delay to avoid busy loops when repeating the last diff
        return 0.05


__all__ = ["TelemetryGateway", "create_app", "ReplayStreamFactory"]

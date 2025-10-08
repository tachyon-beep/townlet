"""Telemetry adapter that streams payloads to stdout."""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from typing import Any

from townlet.factories.registry import register
from townlet.ports.telemetry import TelemetrySink
from townlet.telemetry.transport import StdoutTransport


class StdoutTelemetryAdapter(TelemetrySink):
    """Adapter that serialises events/metrics to stdout using the legacy transport."""

    def __init__(self, cfg: Any, **_: Any) -> None:
        self._cfg = cfg
        self._transport = StdoutTransport()
        self._started = False

    def start(self) -> None:
        self._transport.start()
        self._started = True

    def stop(self) -> None:
        self._transport.stop()
        self._started = False

    def emit_event(self, name: str, payload: Mapping[str, Any] | None = None) -> None:
        record = {"type": "event", "name": name, "timestamp": time.time(), "payload": payload or {}}
        self._send(record)

    def emit_metric(self, name: str, value: float, **tags: Any) -> None:
        record = {
            "type": "metric",
            "name": name,
            "value": float(value),
            "tags": tags,
            "timestamp": time.time(),
        }
        self._send(record)

    def _send(self, record: Mapping[str, Any]) -> None:
        if not self._started:
            raise RuntimeError("StdoutTelemetryAdapter.start() must be called before emitting data")
        payload = json.dumps(record, sort_keys=True).encode("utf-8") + b"\n"
        self._transport.send(payload)


@register("telemetry", "stdout")
def _build_stdout_telemetry(*, cfg: Any, **options: Any) -> StdoutTelemetryAdapter:
    return StdoutTelemetryAdapter(cfg, **options)

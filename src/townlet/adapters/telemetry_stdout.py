"""Stdout telemetry adapter implementing :class:`TelemetrySink`."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from townlet.factories.registry import register
from townlet.ports.telemetry import TelemetrySink


class StdoutTelemetryAdapter(TelemetrySink):
    """Telemetry sink that records events and metrics in-memory."""

    def __init__(self, stream: Any | None = None) -> None:
        self._stream = stream
        self._events: list[tuple[str, Mapping[str, Any] | None]] = []
        self._metrics: list[tuple[str, float, dict[str, Any]]] = []
        self._started = False

    def start(self) -> None:
        self._started = True

    def stop(self) -> None:
        self._started = False

    def emit_event(self, name: str, payload: Mapping[str, Any] | None = None) -> None:
        if not self._started:
            raise RuntimeError("Telemetry sink must be started before emitting events")
        self._events.append((name, dict(payload) if payload is not None else None))
        if self._stream is not None:
            print(f"event:{name}:{payload}", file=self._stream)

    def emit_metric(self, name: str, value: float, **tags: Any) -> None:
        if not self._started:
            raise RuntimeError("Telemetry sink must be started before emitting metrics")
        self._metrics.append((name, float(value), dict(tags)))
        if self._stream is not None:
            print(f"metric:{name}:{value}:{tags}", file=self._stream)

    @property
    def events(self) -> list[tuple[str, Mapping[str, Any] | None]]:
        return list(self._events)

    @property
    def metrics(self) -> list[tuple[str, float, dict[str, Any]]]:
        return list(self._metrics)


@register("telemetry", "stdout")
def _build_stdout_telemetry(**kwargs: Any) -> TelemetrySink:
    return StdoutTelemetryAdapter(**kwargs)


@register("telemetry", "stub")
def _build_stub_telemetry(**kwargs: Any) -> TelemetrySink:
    return StdoutTelemetryAdapter(**kwargs)


@register("telemetry", "dummy")
def _build_dummy_telemetry(**kwargs: Any) -> TelemetrySink:
    return StdoutTelemetryAdapter(**kwargs)

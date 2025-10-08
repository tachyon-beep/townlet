"""Factories for creating telemetry sink adapters."""

from __future__ import annotations

from typing import Any

from townlet.adapters.telemetry_stdout import StdoutTelemetryAdapter
from townlet.telemetry.fallback import StubTelemetrySink
from townlet.telemetry.publisher import TelemetryPublisher

from .registry import register, resolve


def create_telemetry(provider: str = "stdout", **kwargs: Any):
    return resolve("telemetry", provider, **kwargs)


@register("telemetry", "stdout")
@register("telemetry", "default")
def _build_stdout_telemetry(*, publisher: TelemetryPublisher) -> StdoutTelemetryAdapter:
    return StdoutTelemetryAdapter(publisher)


@register("telemetry", "stub")
def _build_stub_telemetry(**kwargs: Any) -> StubTelemetrySink:
    return StubTelemetrySink(**kwargs)


__all__ = ["create_telemetry"]

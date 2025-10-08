"""Factory helpers for telemetry sinks."""

from __future__ import annotations

import importlib
from typing import Any

from townlet.factories._utils import extract_provider
from townlet.factories.registry import resolve
from townlet.ports.telemetry import TelemetrySink


def create_telemetry(cfg: Any) -> TelemetrySink:
    """Create a telemetry sink from configuration."""

    importlib.import_module("townlet.adapters.telemetry_stdout")
    importlib.import_module("townlet.testing.dummies")
    provider, options = extract_provider(cfg, "telemetry", "stdout")
    factory = resolve("telemetry", provider)
    telemetry = factory(cfg=cfg, **dict(options))
    return telemetry  # type: ignore[return-value]


__all__ = ["create_telemetry"]

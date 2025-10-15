"""Core orchestration utilities and shared simulation interfaces."""

from __future__ import annotations

from .factory_registry import (
    policy_registry,
    resolve_policy,
    resolve_telemetry,
    resolve_world,
    telemetry_registry,
)
from .interfaces import (
    PolicyBackendProtocol,
    TelemetrySinkProtocol,
)
from .utils import (
    policy_provider_name,
    telemetry_provider_name,
)

__all__ = [
    "PolicyBackendProtocol",
    "SimulationLoop",
    "TelemetrySinkProtocol",
    "policy_provider_name",
    "policy_registry",
    "resolve_policy",
    "resolve_telemetry",
    "resolve_world",
    "telemetry_provider_name",
    "telemetry_registry",
]


def __getattr__(name: str) -> object:  # pragma: no cover - lazy import glue
    if name == "SimulationLoop":
        from .sim_loop import SimulationLoop as _SimulationLoop

        return _SimulationLoop
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:  # pragma: no cover - module reflection helper
    return sorted(__all__)

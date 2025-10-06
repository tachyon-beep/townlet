"""Affordance runtime package."""

from __future__ import annotations

from .core import (
    AffordanceEnvironment,
    AffordanceOutcome,
    AffordanceRuntimeContext,
    DefaultAffordanceRuntime,
    HookPayload,
    RunningAffordanceState,
    apply_affordance_outcome,
    build_hook_payload,
)
from .runtime import AffordanceCoordinator
from .service import AffordanceRuntimeService

__all__ = [
    "AffordanceCoordinator",
    "AffordanceEnvironment",
    "AffordanceOutcome",
    "AffordanceRuntimeContext",
    "AffordanceRuntimeService",
    "DefaultAffordanceRuntime",
    "HookPayload",
    "RunningAffordanceState",
    "apply_affordance_outcome",
    "build_hook_payload",
]

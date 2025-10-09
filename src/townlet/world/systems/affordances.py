"""Affordance runtime helpers."""

from __future__ import annotations

from typing import Mapping, MutableMapping

from townlet.world.affordance_runtime_service import AffordanceRuntimeService
from townlet.world.affordances import AffordanceOutcome, apply_affordance_outcome
from townlet.world.agents.snapshot import AgentSnapshot

from .base import SystemContext

def step(ctx: SystemContext) -> None:
    """Execute affordance runtime updates (implementation pending)."""

    return


def start(
    runtime: AffordanceRuntimeService,
    *,
    agent_id: str,
    object_id: str,
    affordance_id: str,
    tick: int,
) -> tuple[bool, Mapping[str, object]]:
    """Start an affordance via the runtime."""

    return runtime.start(agent_id, object_id, affordance_id, tick=tick)


def release(
    runtime: AffordanceRuntimeService,
    *,
    agent_id: str,
    object_id: str,
    success: bool,
    reason: str | None,
    requested_affordance_id: str | None,
    tick: int,
) -> tuple[str | None, Mapping[str, object] | None]:
    """Release an affordance via the runtime."""

    return runtime.release(
        agent_id,
        object_id,
        success=success,
        reason=reason,
        requested_affordance_id=requested_affordance_id,
        tick=tick,
    )


def handle_blocked(runtime: AffordanceRuntimeService, object_id: str, tick: int) -> None:
    """Notify the runtime of a blocked affordance."""

    runtime.handle_blocked(object_id, tick)


def resolve(runtime: AffordanceRuntimeService, tick: int) -> None:
    """Advance the runtime resolution loop."""

    runtime.resolve(tick=tick)


def apply_outcome(
    snapshot: AgentSnapshot,
    *,
    kind: str,
    success: bool,
    duration: int,
    object_id: str | None,
    affordance_id: str | None,
    tick: int,
    metadata: Mapping[str, object] | None = None,
) -> None:
    """Apply an affordance outcome to an agent snapshot."""

    outcome = AffordanceOutcome(
        agent_id=snapshot.agent_id,
        kind=kind,
        success=success,
        duration=duration,
        object_id=object_id,
        affordance_id=affordance_id,
        tick=tick,
        metadata=dict(metadata or {}),
    )
    apply_affordance_outcome(snapshot, outcome)


__all__ = [
    "apply_outcome",
    "handle_blocked",
    "release",
    "resolve",
    "start",
    "step",
]

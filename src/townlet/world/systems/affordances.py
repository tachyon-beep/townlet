"""Affordance runtime helpers."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping

from townlet.world.affordance_runtime_service import AffordanceRuntimeService
from townlet.world.affordances import AffordanceOutcome, apply_affordance_outcome
from townlet.world.affordances.core import advance_running_affordances as _advance_runtime
from townlet.world.agents.snapshot import AgentSnapshot
from townlet.world.systems import queues as queue_system

from .base import SystemContext


def step(ctx: SystemContext) -> None:
    """Resolve running affordances and dispatch hooks."""

    state = ctx.state
    runtime = getattr(state, "_affordance_service", None)
    if runtime is not None:
        resolve(runtime, tick=state.tick)
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
    runtime_getter = getattr(runtime, "runtime", None)
    runtime_obj = runtime_getter() if callable(runtime_getter) else runtime_getter
    if runtime_obj is not None:
        _advance_runtime(runtime_obj, tick=tick)
    elif hasattr(runtime, "resolve"):
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


def process_actions(state: Any, actions: Mapping[str, Any], tick: int) -> None:
    """Apply raw action payloads to the world state."""

    if not actions:
        return

    runtime = getattr(state, "_affordance_service", None)
    if runtime is None:
        return

    queue_manager = getattr(state, "queue_manager", None)
    objects = getattr(state, "objects", {})
    active_reservations = getattr(state, "_active_reservations", {})
    spatial_index = getattr(state, "_spatial_index", None)
    agents = getattr(state, "agents", {})

    rivalry_should_avoid = getattr(state, "rivalry_should_avoid", None)
    record_chat_failure = getattr(state, "record_chat_failure", None)
    record_chat_success = getattr(state, "record_chat_success", None)

    for agent_id, action in actions.items():
        snapshot = agents.get(agent_id)
        if snapshot is None:
            continue
        if not isinstance(action, Mapping):
            continue

        kind = action.get("kind")
        object_id = action.get("object")
        action_success = False
        action_duration = int(action.get("duration", 1))
        outcome_affordance_id: str | None = None
        outcome_metadata: dict[str, object] = {}

        if kind == "request" and object_id and queue_manager is not None:
            granted = queue_system.request_access(
                manager=queue_manager,
                objects=objects,
                active_reservations=active_reservations,
                spatial_index=spatial_index,
                object_id=object_id,
                agent_id=agent_id,
                tick=tick,
            )
            if not granted and action.get("blocked"):
                handle_blocked(runtime, object_id, tick)
            action_success = bool(granted)
        elif kind == "move" and action.get("position"):
            position = tuple(action["position"])
            if spatial_index is not None:
                spatial_index.move_agent(snapshot.agent_id, position)
            snapshot.position = position
            action_success = True
        elif kind == "chat":
            target_id = action.get("target") or action.get("listener")
            if isinstance(target_id, str) and callable(rivalry_should_avoid):
                listener = agents.get(target_id)
                if listener is None:
                    continue
                if rivalry_should_avoid(agent_id, target_id):
                    if callable(record_chat_failure):
                        record_chat_failure(agent_id, target_id)
                    continue
                if listener.position != snapshot.position:
                    if callable(record_chat_failure):
                        record_chat_failure(agent_id, target_id)
                    continue
                quality_value = action.get("quality", 0.5)
                try:
                    quality = float(quality_value)
                except (TypeError, ValueError):
                    quality = 0.5
                if callable(record_chat_success):
                    record_chat_success(agent_id, target_id, quality)
                action_success = True
        elif kind == "start" and object_id:
            affordance_id = action.get("affordance")
            if affordance_id:
                affordance_id_str = str(affordance_id)
                action_success, start_metadata = start(
                    runtime,
                    agent_id=agent_id,
                    object_id=object_id,
                    affordance_id=affordance_id_str,
                    tick=tick,
                )
                outcome_affordance_id = affordance_id_str
                if start_metadata:
                    outcome_metadata.update(start_metadata)
        elif kind == "release" and object_id:
            success = bool(action.get("success", True))
            affordance_hint = action.get("affordance")
            reason_value = action.get("reason")
            outcome_affordance_id, release_metadata = release(
                runtime,
                agent_id=agent_id,
                object_id=object_id,
                success=success,
                reason=str(reason_value) if reason_value is not None else None,
                requested_affordance_id=str(affordance_hint)
                if affordance_hint is not None
                else None,
                tick=tick,
            )
            action_success = success
            if release_metadata:
                outcome_metadata.update(release_metadata)
        elif kind == "blocked" and object_id:
            handle_blocked(runtime, object_id, tick)

        if kind:
            apply_outcome(
                snapshot,
                kind=str(kind),
                success=action_success,
                duration=action_duration,
                object_id=str(object_id) if isinstance(object_id, str) else None,
                affordance_id=str(outcome_affordance_id)
                if outcome_affordance_id
                else None,
                tick=tick,
                metadata=dict(outcome_metadata) if outcome_metadata else {},
            )


__all__ = [
    "apply_outcome",
    "handle_blocked",
    "process_actions",
    "release",
    "resolve",
    "start",
    "step",
]

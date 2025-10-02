"""Affordance runtime scaffolding pending extraction from `world.grid`."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Mapping, Protocol, TypedDict
from typing import Literal

from townlet.world.queue_manager import QueueManager
from townlet.world.preconditions import evaluate_preconditions


logger = logging.getLogger("townlet.world.grid")


if TYPE_CHECKING:  # pragma: no cover - type hint guard
    from townlet.world.grid import AgentSnapshot, WorldState


@dataclass(slots=True)
class AffordanceRuntimeContext:
    """Shared services supplied by `WorldState` during affordance resolution."""

    queue_manager: QueueManager
    emit_event: Callable[[str, dict[str, object]], None]
    register_hook: Callable[[str, Callable[[dict[str, object]], None]], None]
    # TODO(@townlet): Extend with RNG, telemetry, and promotion handles as extraction progresses.


@dataclass(slots=True)
class RunningAffordanceState:
    """Serialized view of a running affordance for telemetry/tests."""

    agent_id: str
    object_id: str
    affordance_id: str
    duration_remaining: int
    effects: dict[str, float] = field(default_factory=dict)


class HookPayload(TypedDict, total=False):
    """Structured affordance hook payload shared across stages."""

    stage: Literal["before", "after", "fail"]
    hook: str
    tick: int
    agent_id: str
    object_id: str
    affordance_id: str
    world: "WorldState"
    spec: Any
    effects: dict[str, float]
    reason: str
    condition: str
    context: dict[str, object]


def snapshot_running_affordance(
    *,
    object_id: str,
    agent_id: str,
    affordance_id: str,
    duration_remaining: int,
    effects: Mapping[str, float] | None = None,
) -> RunningAffordanceState:
    """Create a serializable snapshot for a running affordance entry."""

    return RunningAffordanceState(
        agent_id=agent_id,
        object_id=object_id,
        affordance_id=affordance_id,
        duration_remaining=duration_remaining,
        effects=dict(effects or {}),
    )


def build_hook_payload(
    *,
    stage: Literal["before", "after", "fail"],
    hook: str,
    tick: int,
    agent_id: str,
    object_id: str,
    affordance_id: str,
    world: "WorldState",
    spec: Any,
    extra: Mapping[str, object] | None = None,
) -> HookPayload:
    """Compose the base payload forwarded to affordance hook handlers."""

    payload: HookPayload = HookPayload(
        stage=stage,
        hook=hook,
        tick=tick,
        agent_id=agent_id,
        object_id=object_id,
        affordance_id=affordance_id,
        world=world,
        spec=spec,
    )
    if extra:
        payload.update(extra)
    return payload


@dataclass(slots=True)
class AffordanceOutcome:
    """Represents the result of an affordance-related agent action."""

    agent_id: str
    kind: str
    success: bool
    duration: int
    object_id: str | None = None
    affordance_id: str | None = None
    tick: int | None = None
    metadata: dict[str, object] = field(default_factory=dict)


def apply_affordance_outcome(
    snapshot: "AgentSnapshot",
    outcome: AffordanceOutcome,
) -> None:
    """Update agent snapshot bookkeeping based on the supplied outcome."""

    snapshot.last_action_id = outcome.kind
    snapshot.last_action_success = outcome.success
    snapshot.last_action_duration = outcome.duration
    # TODO(@townlet): Persist richer outcome metadata (e.g., affordance/object ids) once
    # snapshot schema evolves; keep attachments scoped to metadata until the refactor lands.
    if outcome.metadata:
        outcome_log = snapshot.inventory.setdefault("_affordance_outcomes", [])
        outcome_log.append(outcome.metadata)
        if len(outcome_log) > 10:
            del outcome_log[0]
        if len(outcome_log) > 10:
            del outcome_log[0]


class AffordanceRuntime(Protocol):
    """Protocol for the future affordance runtime implementation."""

    # TODO(@townlet): Bind runtime to world collections (agents/objects/affordances) on init.
    def bind(self, *, context: AffordanceRuntimeContext) -> None: ...

    # TODO(@townlet): Accept agent action payloads and enqueue affordance starts.
    def apply_actions(self, actions: Mapping[str, dict[str, object]], *, tick: int) -> None: ...

    # TODO(@townlet): Tick running affordances, dispatch hooks, and emit telemetry events.
    def resolve(self, *, tick: int) -> None: ...

    # TODO(@townlet): Provide deterministic state for snapshots and tests.
    def running_snapshot(self) -> dict[str, RunningAffordanceState]: ...

    # TODO(@townlet): Reset runtime state during world resets / snapshot loads.
    def clear(self) -> None: ...


# TODO(@townlet): Implement concrete `DefaultAffordanceRuntime` once responsibilities migrate from `world.grid`.


class DefaultAffordanceRuntime:
    """Default affordance runtime bound to an existing `WorldState`."""

    def __init__(
        self,
        world: "WorldState",
        *,
        running_cls: type,
    ) -> None:
        self._world = world
        self._running_cls = running_cls

    @property
    def world(self) -> "WorldState":
        return self._world

    @property
    def running_affordances(self) -> dict[str, Any]:
        return self._world._running_affordances  # pylint: disable=protected-access

    def remove_agent(self, agent_id: str) -> None:
        """Drop any running affordances owned by `agent_id`."""

        world = self._world
        for object_id, running in list(self.running_affordances.items()):
            if running.agent_id != agent_id:
                continue
            self.running_affordances.pop(object_id, None)
            obj = world.objects.get(object_id)
            if obj is not None and obj.occupied_by == agent_id:
                obj.occupied_by = None

    def start(
        self,
        agent_id: str,
        object_id: str,
        affordance_id: str,
        *,
        tick: int,
    ) -> tuple[bool, dict[str, object]]:
        world = self._world
        metadata: dict[str, object] = {}
        if world.queue_manager.active_agent(object_id) != agent_id:
            return False, metadata
        if object_id in self.running_affordances:
            return False, metadata
        obj = world.objects.get(object_id)
        spec = world.affordances.get(affordance_id)
        if obj is None or spec is None:
            return False, metadata
        if spec.object_type != obj.object_type:
            return False, metadata

        if spec.compiled_preconditions:
            context = world._build_precondition_context(  # pylint: disable=protected-access
                agent_id=agent_id,
                object_id=object_id,
                spec=spec,
            )
            ok, failed = evaluate_preconditions(spec.compiled_preconditions, context)
            if not ok:
                context_snapshot = world._snapshot_precondition_context(context)  # pylint: disable=protected-access
                payload = {
                    "agent_id": agent_id,
                    "object_id": object_id,
                    "affordance_id": affordance_id,
                    "condition": failed.source if failed else None,
                    "context": context_snapshot,
                }
                logger.debug(
                    "Precondition failed for affordance '%s' (agent=%s, object=%s, condition=%s)",
                    affordance_id,
                    agent_id,
                    object_id,
                    payload["condition"],
                )
                world._dispatch_affordance_hooks(  # pylint: disable=protected-access
                    "fail",
                    spec.hooks.get("fail", ()),
                    agent_id=agent_id,
                    object_id=object_id,
                    spec=spec,
                    extra={
                        "reason": "precondition_failed",
                        "condition": payload["condition"],
                        "context": context_snapshot,
                    },
                )
                world._emit_event("affordance_precondition_fail", payload)  # pylint: disable=protected-access
                world._emit_event(  # pylint: disable=protected-access
                    "affordance_fail",
                    {
                        **payload,
                        "reason": "precondition_failed",
                    },
                )
                if world.queue_manager.active_agent(object_id) == agent_id:
                    world.queue_manager.release(object_id, agent_id, tick, success=False)
                    world._sync_reservation(object_id)  # pylint: disable=protected-access
                metadata["reason"] = "precondition_failed"
                return False, metadata

        running = self._running_cls(
            agent_id=agent_id,
            affordance_id=affordance_id,
            duration_remaining=max(spec.duration, 1),
            effects=spec.effects,
        )
        self.running_affordances[object_id] = running
        obj.occupied_by = agent_id
        continue_start = world._dispatch_affordance_hooks(  # pylint: disable=protected-access
            "before",
            spec.hooks.get("before", ()),
            agent_id=agent_id,
            object_id=object_id,
            spec=spec,
        )
        if not continue_start:
            self.running_affordances.pop(object_id, None)
            if obj.occupied_by == agent_id:
                obj.occupied_by = None
            if world.queue_manager.active_agent(object_id) == agent_id:
                world.queue_manager.release(object_id, agent_id, tick, success=False)
                world._sync_reservation(object_id)  # pylint: disable=protected-access
            metadata["reason"] = "hook_cancelled"
            return False, metadata
        world._emit_event(  # pylint: disable=protected-access
            "affordance_start",
            {
                "agent_id": agent_id,
                "object_id": object_id,
                "affordance_id": affordance_id,
                "duration": spec.duration,
            },
        )
        return True, metadata

    def release(
        self,
        agent_id: str,
        object_id: str,
        *,
        success: bool,
        reason: str | None,
        requested_affordance_id: str | None,
        tick: int,
    ) -> tuple[str | None, dict[str, object]]:
        world = self._world
        metadata: dict[str, object] = {}
        running = self.running_affordances.pop(object_id, None)
        affordance_id = requested_affordance_id
        if running is not None:
            affordance_id = running.affordance_id
            if success:
                world._apply_affordance_effects(running.agent_id, running.effects)  # pylint: disable=protected-access
                spec = world.affordances.get(running.affordance_id)
                world._dispatch_affordance_hooks(  # pylint: disable=protected-access
                    "after",
                    spec.hooks.get("after", ()) if spec else (),
                    agent_id=running.agent_id,
                    object_id=object_id,
                    spec=spec,
                    extra={"effects": dict(running.effects)},
                )
                world._emit_event(  # pylint: disable=protected-access
                    "affordance_finish",
                    {
                        "agent_id": running.agent_id,
                        "object_id": object_id,
                        "affordance_id": running.affordance_id,
                    },
                )
                obj = world.objects.get(object_id)
                if obj is not None:
                    obj.occupied_by = None
        world.queue_manager.release(object_id, agent_id, tick, success=success)
        world._sync_reservation(object_id)  # pylint: disable=protected-access
        if not success:
            if reason:
                metadata["reason"] = reason
            if running is not None:
                spec = world.affordances.get(running.affordance_id)
                world._dispatch_affordance_hooks(  # pylint: disable=protected-access
                    "fail",
                    spec.hooks.get("fail", ()) if spec else (),
                    agent_id=agent_id,
                    object_id=object_id,
                    spec=spec,
                    extra={"reason": reason},
                )
                world._emit_event(  # pylint: disable=protected-access
                    "affordance_fail",
                    {
                        "agent_id": agent_id,
                        "object_id": object_id,
                        "affordance_id": running.affordance_id,
                    },
                )
        return affordance_id, metadata

    def handle_blocked(self, object_id: str, tick: int) -> None:
        world = self._world
        if world.queue_manager.record_blocked_attempt(object_id):
            occupant = world.queue_manager.active_agent(object_id)
            running = self.running_affordances.pop(object_id, None)
            spec = None
            if running is not None:
                spec = world.affordances.get(running.affordance_id)
                world._dispatch_affordance_hooks(  # pylint: disable=protected-access
                    "fail",
                    spec.hooks.get("fail", ()) if spec else (),
                    agent_id=running.agent_id,
                    object_id=object_id,
                    spec=spec,
                    extra={"reason": "ghost_step"},
                )
            if occupant is not None:
                world.queue_manager.release(object_id, occupant, tick, success=False)
            world._sync_reservation(object_id)  # pylint: disable=protected-access

    def resolve(self, *, tick: int) -> None:
        world = self._world
        debug_enabled = logger.isEnabledFor(logging.DEBUG)
        entry_running = 0
        entry_queued = 0
        if debug_enabled:
            entry_running = len(self.running_affordances)
            entry_queued = sum(
                len(world.queue_manager.queue_snapshot(object_id))
                for object_id in world.objects.keys()
            )
            logger.debug(
                "world.resolve_affordances.start tick=%s running=%s queued_agents=%s",
                tick,
                entry_running,
                entry_queued,
            )
        start_time = time.perf_counter()
        world.queue_manager.on_tick(tick)
        for object_id, occupant in list(world._active_reservations.items()):  # pylint: disable=protected-access
            queue = world.queue_manager.queue_snapshot(object_id)
            if not queue:
                continue
            if world.queue_manager.record_blocked_attempt(object_id):
                waiting = world.queue_manager.queue_snapshot(object_id)
                rival = waiting[0] if waiting else None
                world.queue_manager.release(object_id, occupant, tick, success=False)
                world.queue_manager.requeue_to_tail(object_id, occupant, tick)
                if rival is not None:
                    world._record_queue_conflict(  # pylint: disable=protected-access
                        object_id=object_id,
                        actor=occupant,
                        rival=rival,
                        reason="ghost_step",
                        queue_length=len(waiting),
                        intensity=None,
                    )
                self.running_affordances.pop(object_id, None)
                world._sync_reservation(object_id)  # pylint: disable=protected-access

        for object_id, running in list(self.running_affordances.items()):
            running.duration_remaining -= 1
            if running.duration_remaining <= 0:
                world._apply_affordance_effects(running.agent_id, running.effects)  # pylint: disable=protected-access
                self.running_affordances.pop(object_id, None)
                waiting = world.queue_manager.queue_snapshot(object_id)
                spec = world.affordances.get(running.affordance_id)
                hook_names = tuple(spec.hooks.get("after", ())) if spec else ()
                if debug_enabled:
                    hook_start = time.perf_counter()
                world._dispatch_affordance_hooks(  # pylint: disable=protected-access
                    "after",
                    hook_names,
                    agent_id=running.agent_id,
                    object_id=object_id,
                    spec=spec,
                    extra={"effects": dict(running.effects)},
                )
                if debug_enabled:
                    hook_duration_ms = (time.perf_counter() - hook_start) * 1000.0
                    logger.debug(
                        "world.resolve_affordances.hook tick=%s stage=%s object=%s agent=%s duration_ms=%.2f hooks=%s",
                        tick,
                        "after",
                        object_id,
                        running.agent_id,
                        hook_duration_ms,
                        len(hook_names),
                    )
                world.queue_manager.release(object_id, running.agent_id, tick, success=True)
                world._sync_reservation(object_id)  # pylint: disable=protected-access
                if waiting:
                    next_agent = waiting[0]
                    world._record_queue_conflict(  # pylint: disable=protected-access
                        object_id=object_id,
                        actor=running.agent_id,
                        rival=next_agent,
                        reason="handover",
                        queue_length=len(waiting),
                        intensity=0.5,
                    )
                world._emit_event(  # pylint: disable=protected-access
                    "affordance_finish",
                    {
                        "agent_id": running.agent_id,
                        "object_id": object_id,
                        "affordance_id": running.affordance_id,
                    },
                )

        if debug_enabled:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            running_count = len(self.running_affordances)
            queued_agents = sum(
                len(world.queue_manager.queue_snapshot(object_id))
                for object_id in world.objects.keys()
            )
            logger.debug(
                "world.resolve_affordances.end tick=%s duration_ms=%.2f running=%s queued_agents=%s running_delta=%s queued_delta=%s",
                tick,
                duration_ms,
                running_count,
                queued_agents,
                running_count - entry_running,
                queued_agents - entry_queued,
            )

        world._apply_need_decay()  # pylint: disable=protected-access

    def running_snapshot(self) -> dict[str, RunningAffordanceState]:
        world = self._world
        return {
            object_id: snapshot_running_affordance(
                object_id=object_id,
                agent_id=running.agent_id,
                affordance_id=running.affordance_id,
                duration_remaining=running.duration_remaining,
                effects=running.effects,
            )
            for object_id, running in self.running_affordances.items()
        }

    def clear(self) -> None:
        self.running_affordances.clear()

"""Affordance runtime scaffolding pending extraction from `world.grid`."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Iterable, Mapping, MutableMapping, Protocol, TypedDict
from typing import Literal

from townlet.world.queue_manager import QueueManager
from townlet.world.preconditions import evaluate_preconditions


logger = logging.getLogger("townlet.world.grid")


if TYPE_CHECKING:  # pragma: no cover - type hint guard
    from townlet.world.grid import AgentSnapshot, WorldState


@dataclass(slots=True)
class AffordanceRuntimeContext:
    """Dependencies supplied to the affordance runtime."""

    world: "WorldState"
    queue_manager: QueueManager
    objects: MutableMapping[str, Any]
    affordances: MutableMapping[str, Any]
    running_affordances: MutableMapping[str, Any]
    active_reservations: MutableMapping[str, str]
    emit_event: Callable[[str, dict[str, object]], None]
    sync_reservation: Callable[[str], None]
    apply_affordance_effects: Callable[[str, dict[str, float]], None]
    dispatch_hooks: Callable[[str, Iterable[str]], bool]
    record_queue_conflict: Callable[..., None]
    apply_need_decay: Callable[[], None]
    build_precondition_context: Callable[..., dict[str, Any]]
    snapshot_precondition_context: Callable[[Mapping[str, Any]], dict[str, Any]]


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
    # TODO(@townlet-backlog): Persist richer outcome metadata (affordance/object ids)
    # once the snapshot schema evolves; keep attachments scoped to metadata until the
    # schema extension is scheduled.
    if outcome.metadata:
        outcome_log = snapshot.inventory.setdefault("_affordance_outcomes", [])
        outcome_log.append(outcome.metadata)
        if len(outcome_log) > 10:
            del outcome_log[0]
        if len(outcome_log) > 10:
            del outcome_log[0]


class AffordanceRuntime(Protocol):
    """Protocol describing the affordance runtime contract."""

    def bind(self, *, context: AffordanceRuntimeContext) -> None:
        """Attach the runtime to the provided world context."""

    def apply_actions(
        self, actions: Mapping[str, dict[str, object]], *, tick: int
    ) -> None:
        """Process agent actions that may start or queue affordances."""

    def resolve(self, *, tick: int) -> None:
        """Advance running affordances and emit telemetry/hook events."""

    def running_snapshot(self) -> dict[str, RunningAffordanceState]:
        """Return the serialisable state of all running affordances."""

    def clear(self) -> None:
        """Reset runtime state (used on snapshot restore or world reset)."""


class DefaultAffordanceRuntime:
    """Default affordance runtime bound to an injected context."""

    def __init__(
        self,
        context: AffordanceRuntimeContext,
        *,
        running_cls: type,
        instrumentation: str = "off",
        options: Mapping[str, object] | None = None,
    ) -> None:
        self._ctx = context
        self._running_cls = running_cls
        self._instrumentation_level = instrumentation
        self._options = dict(options or {})

    @property
    def context(self) -> AffordanceRuntimeContext:
        return self._ctx

    @property
    def world(self) -> "WorldState":
        return self._ctx.world

    @property
    def running_affordances(self) -> MutableMapping[str, Any]:
        return self._ctx.running_affordances

    @property
    def instrumentation_level(self) -> str:
        return self._instrumentation_level

    @property
    def options(self) -> dict[str, object]:
        return dict(self._options)

    def remove_agent(self, agent_id: str) -> None:
        """Drop any running affordances owned by `agent_id`."""

        ctx = self._ctx
        world = ctx.world
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
        ctx = self._ctx
        world = ctx.world
        queue_manager = ctx.queue_manager
        objects = ctx.objects
        affordances = ctx.affordances
        metadata: dict[str, object] = {}
        if queue_manager.active_agent(object_id) != agent_id:
            return False, metadata
        if object_id in self.running_affordances:
            return False, metadata
        obj = objects.get(object_id)
        spec = affordances.get(affordance_id)
        if obj is None or spec is None:
            logger.error(
                "affordance.start.missing_spec object=%s affordance=%s agent=%s",
                object_id,
                affordance_id,
                agent_id,
            )
            if queue_manager.active_agent(object_id) == agent_id:
                queue_manager.release(object_id, agent_id, tick, success=False)
                ctx.sync_reservation(object_id)
            ctx.emit_event(
                "affordance_fail",
                {
                    "agent_id": agent_id,
                    "object_id": object_id,
                    "affordance_id": affordance_id,
                    "reason": "missing_spec",
                },
            )
            metadata["reason"] = "missing_spec"
            return False, metadata
        if spec.object_type != obj.object_type:
            raise RuntimeError(
                f"Affordance '{affordance_id}' incompatible with object '{object_id}'"
            )

        if spec.compiled_preconditions:
            context = ctx.build_precondition_context(
                agent_id=agent_id,
                object_id=object_id,
                spec=spec,
            )
            ok, failed = evaluate_preconditions(spec.compiled_preconditions, context)
            if not ok:
                context_snapshot = ctx.snapshot_precondition_context(context)
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
                ctx.dispatch_hooks(
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
                ctx.emit_event("affordance_precondition_fail", payload)
                ctx.emit_event(
                    "affordance_fail",
                    {
                        **payload,
                        "reason": "precondition_failed",
                    },
                )
                if queue_manager.active_agent(object_id) == agent_id:
                    queue_manager.release(object_id, agent_id, tick, success=False)
                    ctx.sync_reservation(object_id)
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
        continue_start = ctx.dispatch_hooks(
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
            if queue_manager.active_agent(object_id) == agent_id:
                queue_manager.release(object_id, agent_id, tick, success=False)
                ctx.sync_reservation(object_id)
            metadata["reason"] = "hook_cancelled"
            return False, metadata
        ctx.emit_event(
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
        ctx = self._ctx
        world = ctx.world
        queue_manager = ctx.queue_manager
        metadata: dict[str, object] = {}
        running = self.running_affordances.pop(object_id, None)
        affordance_id = requested_affordance_id
        if running is not None:
            affordance_id = running.affordance_id
            if success:
                ctx.apply_affordance_effects(running.agent_id, running.effects)
                spec = ctx.affordances.get(running.affordance_id)
                assert (
                    spec is not None
                ), f"Missing spec for running affordance '{running.affordance_id}'"
                ctx.dispatch_hooks(
                    "after",
                    spec.hooks.get("after", ()) if spec else (),
                    agent_id=running.agent_id,
                    object_id=object_id,
                    spec=spec,
                    extra={"effects": dict(running.effects)},
                )
                ctx.emit_event(
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
        queue_manager.release(object_id, agent_id, tick, success=success)
        ctx.sync_reservation(object_id)
        if not success:
            if reason:
                metadata["reason"] = reason
            if running is not None:
                spec = ctx.affordances.get(running.affordance_id)
                assert (
                    spec is not None
                ), f"Missing spec for running affordance '{running.affordance_id}'"
                ctx.dispatch_hooks(
                    "fail",
                    spec.hooks.get("fail", ()) if spec else (),
                    agent_id=agent_id,
                    object_id=object_id,
                    spec=spec,
                    extra={"reason": reason},
                )
                ctx.emit_event(
                    "affordance_fail",
                    {
                        "agent_id": agent_id,
                        "object_id": object_id,
                        "affordance_id": running.affordance_id,
                    },
                )
        return affordance_id, metadata

    def handle_blocked(self, object_id: str, tick: int) -> None:
        ctx = self._ctx
        queue_manager = ctx.queue_manager
        world = ctx.world
        if queue_manager.record_blocked_attempt(object_id):
            occupant = queue_manager.active_agent(object_id)
            running = self.running_affordances.pop(object_id, None)
            spec = None
            if running is not None:
                spec = ctx.affordances.get(running.affordance_id)
                assert (
                    spec is not None
                ), f"Missing spec for running affordance '{running.affordance_id}'"
                ctx.dispatch_hooks(
                    "fail",
                    spec.hooks.get("fail", ()) if spec else (),
                    agent_id=running.agent_id,
                    object_id=object_id,
                    spec=spec,
                    extra={"reason": "ghost_step"},
                )
            if occupant is not None:
                queue_manager.release(object_id, occupant, tick, success=False)
            ctx.sync_reservation(object_id)

    def _select_handover_candidate(
        self,
        world: "WorldState",
        source_agent: str,
        waiting: list[str],
    ) -> str | None:
        if not waiting:
            return None
        best_id: str | None = None
        best_score = float("-inf")
        for index, candidate in enumerate(waiting):
            tie = world.relationship_tie(source_agent, candidate)
            trust = float(getattr(tie, "trust", 0.0)) if tie else 0.0
            familiarity = float(getattr(tie, "familiarity", 0.0)) if tie else 0.0
            rivalry = world.rivalry_value(source_agent, candidate)
            score = trust + familiarity - rivalry - 0.05 * index
            if score > best_score:
                best_score = score
                best_id = candidate
        if best_id is None or best_score <= 0.0:
            return None
        return best_id

    def resolve(self, *, tick: int) -> None:
        ctx = self._ctx
        world = ctx.world
        queue_manager = ctx.queue_manager
        objects = ctx.objects
        active_reservations = ctx.active_reservations
        record_queue_conflict = ctx.record_queue_conflict
        debug_enabled = self._instrumentation_enabled()
        entry_running = 0
        entry_queued = 0
        if debug_enabled:
            entry_running = len(self.running_affordances)
            entry_queued = sum(
                len(queue_manager.queue_snapshot(object_id))
                for object_id in objects.keys()
            )
            logger.debug(
                "world.resolve_affordances.start tick=%s running=%s queued_agents=%s",
                tick,
                entry_running,
                entry_queued,
            )
        start_time = time.perf_counter()
        queue_manager.on_tick(tick)
        for object_id, occupant in list(active_reservations.items()):
            queue = queue_manager.queue_snapshot(object_id)
            if not queue:
                continue
            if queue_manager.record_blocked_attempt(object_id):
                waiting = queue_manager.queue_snapshot(object_id)
                rival = waiting[0] if waiting else None
                queue_manager.release(object_id, occupant, tick, success=False)
                queue_manager.requeue_to_tail(object_id, occupant, tick)
                if rival is not None:
                    record_queue_conflict(
                        object_id=object_id,
                        actor=occupant,
                        rival=rival,
                        reason="ghost_step",
                        queue_length=len(waiting),
                        intensity=None,
                    )
                self.running_affordances.pop(object_id, None)
                ctx.sync_reservation(object_id)

        for object_id, running in list(self.running_affordances.items()):
            running.duration_remaining -= 1
            if running.duration_remaining <= 0:
                ctx.apply_affordance_effects(running.agent_id, running.effects)
                self.running_affordances.pop(object_id, None)
                waiting = queue_manager.queue_snapshot(object_id)
                spec = ctx.affordances.get(running.affordance_id)
                hook_names = tuple(spec.hooks.get("after", ())) if spec else ()
                if debug_enabled:
                    hook_start = time.perf_counter()
                ctx.dispatch_hooks(
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
                preferred = self._select_handover_candidate(world, running.agent_id, waiting)
                if preferred is not None:
                    queue_manager.promote_agent(object_id, preferred)
                queue_manager.release(object_id, running.agent_id, tick, success=True)
                ctx.sync_reservation(object_id)
                if waiting:
                    next_agent = preferred if preferred is not None else waiting[0]
                    record_queue_conflict(
                        object_id=object_id,
                        actor=running.agent_id,
                        rival=next_agent,
                        reason="handover",
                        queue_length=len(waiting),
                        intensity=0.5,
                    )
                ctx.emit_event(
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
                len(queue_manager.queue_snapshot(object_id))
                for object_id in objects.keys()
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

        ctx.apply_need_decay()

    def _instrumentation_enabled(self) -> bool:
        return self._instrumentation_level == "timings" or logger.isEnabledFor(logging.DEBUG)

    def running_snapshot(self) -> dict[str, RunningAffordanceState]:
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

    def export_state(self) -> dict[str, object]:
        state: dict[str, object] = {}
        for object_id, running in self.running_affordances.items():
            state[object_id] = {
                "agent_id": running.agent_id,
                "affordance_id": running.affordance_id,
                "duration_remaining": int(running.duration_remaining),
                "effects": {key: float(value) for key, value in running.effects.items()},
            }
        return state

    def import_state(self, payload: Mapping[str, Mapping[str, object]]) -> None:
        ctx = self._ctx
        objects = ctx.objects
        queue_manager = ctx.queue_manager
        self.clear()
        for object_id, entry in payload.items():
            agent_id = str(entry.get("agent_id", ""))
            affordance_id = str(entry.get("affordance_id", ""))
            if not agent_id or not affordance_id:
                continue
            duration = int(entry.get("duration_remaining", 0))
            effects_payload = entry.get("effects", {})
            if isinstance(effects_payload, Mapping):
                effects = {str(k): float(v) for k, v in effects_payload.items()}
            else:
                effects = {}
            running = self._running_cls(
                agent_id=agent_id,
                affordance_id=affordance_id,
                duration_remaining=max(0, duration),
                effects=effects,
            )
            self.running_affordances[object_id] = running
            obj = objects.get(object_id)
            if obj is not None:
                obj.occupied_by = agent_id
            # Ensure queue manager active reservation aligns with imported state.
            if queue_manager.active_agent(object_id) != agent_id and agent_id:
                ctx.active_reservations[object_id] = agent_id

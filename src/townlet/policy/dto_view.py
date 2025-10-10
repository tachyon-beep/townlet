"""DTO-backed view exposing world data for policy behaviours."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Callable, Iterable, Iterator, Mapping, Sequence

from townlet.world.dto.observation import AgentObservationDTO, ObservationEnvelope

logger = logging.getLogger(__name__)


def _normalize_agent_id(agent: Any) -> str | None:
    if agent is None:
        return None
    identifier = str(agent)
    if "#" in identifier:
        base = identifier.split("#", 1)[0].strip()
        if base:
            return base
    return identifier if identifier else None

def _as_tuple(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    return (value,)


@dataclass(slots=True)
class DTOQueueManagerView:
    queues: Mapping[str, Any]
    fallback: Any | None = None

    def active_agent(self, object_id: str) -> str | None:
        queue_info = self.queues.get("active", {})
        active = queue_info.get(object_id)
        if active is None and self.fallback is not None:
            value = self.fallback.active_agent(object_id)
            normalized = _normalize_agent_id(value)
            return normalized if normalized is not None else value
        normalized = _normalize_agent_id(active)
        return normalized if normalized is not None else active

    def queue_snapshot(self, object_id: str) -> tuple[Any, ...]:
        queues_dict = self.queues.get("queues", {})
        entries = queues_dict.get(object_id)
        if entries is None and self.fallback is not None:
            try:
                return tuple(self.fallback.queue_snapshot(object_id))
            except Exception:  # pragma: no cover - defensive
                return ()
        if isinstance(entries, Mapping):
            data = entries.get("queue") or entries.get("pending") or []
        else:
            data = entries

        cleaned: list[Any] = []
        for item in _as_tuple(data):
            if isinstance(item, Mapping):
                candidate = item.get("agent_id") or item.get("agent")
                if isinstance(candidate, str):
                    cleaned.append(candidate)
                    continue
            cleaned.append(item)
        return tuple(cleaned)


@dataclass(slots=True)
class DTOAffordanceRuntimeView:
    running: Mapping[str, Any]
    fallback: Any | None = None

    @property
    def running_affordances(self) -> Mapping[str, Any]:
        if self.running:
            converted: dict[str, Any] = {}
            for object_id, payload in self.running.items():
                if isinstance(payload, Mapping):
                    converted[object_id] = SimpleNamespace(**payload)
            if converted:
                return converted
        if self.fallback is not None:
            return getattr(self.fallback, "running_affordances", {})
        return {}


@dataclass(slots=True)
class DTORelationshipView:
    snapshot: Mapping[str, Any]
    metrics: Mapping[str, Any]
    fallback: Any | None = None

    def relationship_tie(self, agent_id: str, other_id: str) -> Any:
        ties = self.snapshot.get(agent_id, {})
        payload = ties.get(other_id)
        if isinstance(payload, Mapping):
            return SimpleNamespace(**payload)
        if self.fallback is not None:
            return self.fallback.relationship_tie(agent_id, other_id)
        return None

    def rivalry_value(self, agent_id: str, other_id: str) -> float:
        metrics = self.metrics.get(agent_id, {})
        rivalry = metrics.get("rivalry", {})
        if isinstance(rivalry, Mapping) and other_id in rivalry:
            try:
                return float(rivalry[other_id])
            except (TypeError, ValueError):  # pragma: no cover - defensive
                pass
        if self.fallback is not None:
            return float(self.fallback.rivalry_value(agent_id, other_id))
        return 0.0

    def rivalry_should_avoid(self, agent_id: str, other_id: str) -> bool:
        metrics = self.metrics.get(agent_id, {})
        avoid = metrics.get("should_avoid", {})
        if isinstance(avoid, Mapping) and other_id in avoid:
            return bool(avoid[other_id])
        if self.fallback is not None:
            return bool(self.fallback.rivalry_should_avoid(agent_id, other_id))
        return False


class DTOWorldView:
    """Facade exposing DTO-backed world data with legacy fallbacks."""

    def __init__(
        self,
        *,
        envelope: ObservationEnvelope,
        world: Any | None = None,
        guardrail_emitter: Callable[[str, Mapping[str, Any]], None] | None = None,
    ) -> None:
        global_ctx = envelope.global_context
        queues = global_ctx.queues or {}
        running = global_ctx.running_affordances or {}
        relationships = global_ctx.relationship_snapshot or {}
        relationship_metrics = global_ctx.relationship_metrics or {}

        queue_fallback = getattr(world, "queue_manager", None)
        affordance_fallback = getattr(world, "affordance_runtime", None)
        relationship_fallback = world

        self.queue_manager = DTOQueueManagerView(queues, queue_fallback)
        self.affordance_runtime = DTOAffordanceRuntimeView(
            running, affordance_fallback
        )
        self._relationships = DTORelationshipView(
            relationships, relationship_metrics, relationship_fallback
        )
        self._world = world
        self.tick = int(getattr(world, "tick", envelope.tick))
        self._guardrail_emitter = guardrail_emitter
        self._fallback_agent_warning_emitted = False
        self._agent_snapshots = self._build_agent_snapshots(
            envelope.agents, world_agent_lookup=getattr(world, "agents", None)
        )
        self._queue_affinity_metrics = global_ctx.queue_affinity_metrics or {}

    # ------------------------------------------------------------------
    # Agent helpers
    # ------------------------------------------------------------------
    def agent_snapshot(self, agent_id: str) -> SimpleNamespace | None:
        snapshot = self._agent_snapshots.get(agent_id)
        if snapshot is not None:
            return snapshot
        world_agents = getattr(self._world, "agents", None)
        if world_agents is None:
            return None
        getter = getattr(world_agents, "get", None)
        if callable(getter):
            if not self._fallback_agent_warning_emitted:
                logger.warning(
                    "DTOWorldView falling back to legacy world agents for '%s'.",
                    agent_id,
                )
                self._fallback_agent_warning_emitted = True
            return getter(agent_id)
        return None

    def iter_agent_snapshots(self) -> Iterator[tuple[str, SimpleNamespace]]:
        if self._agent_snapshots:
            for agent_id in sorted(self._agent_snapshots.keys()):
                yield agent_id, self._agent_snapshots[agent_id]
            return
        world_agents = getattr(self._world, "agents", None)
        if world_agents is None:
            return
        items = getattr(world_agents, "items", None)
        if callable(items):
            if not self._fallback_agent_warning_emitted:
                logger.warning(
                    "DTOWorldView iterating legacy world agents due to missing DTO data."
                )
                self._fallback_agent_warning_emitted = True
            for agent_id, snapshot in items():
                yield str(agent_id), snapshot

    def agent_ids(self) -> tuple[str, ...]:
        if self._agent_snapshots:
            return tuple(sorted(self._agent_snapshots.keys()))
        world_agents = getattr(self._world, "agents", None)
        if world_agents is None:
            return ()
        keys = getattr(world_agents, "keys", None)
        if callable(keys):
            return tuple(sorted(map(str, keys())))
        return ()

    def agent_position(self, agent_id: str) -> tuple[int, int] | None:
        snapshot = self.agent_snapshot(agent_id)
        if snapshot is None:
            return None
        return getattr(snapshot, "position", None)

    def agent_needs(self, agent_id: str) -> Mapping[str, float]:
        snapshot = self.agent_snapshot(agent_id)
        if snapshot is None:
            return {}
        needs = getattr(snapshot, "needs", {})
        return dict(needs) if isinstance(needs, Mapping) else {}

    def pending_intent(self, agent_id: str) -> Mapping[str, Any] | None:
        snapshot = self.agent_snapshot(agent_id)
        if snapshot is None:
            return None
        pending = getattr(snapshot, "pending_intent", None)
        if pending is None:
            return None
        return dict(pending) if isinstance(pending, Mapping) else None

    def agents_at_position(self, position: Sequence[int]) -> tuple[str, ...]:
        target = tuple(position) if position is not None else None
        if target is None:
            return ()
        matches: list[str] = []
        for agent_id, snapshot in self.iter_agent_snapshots():
            if getattr(snapshot, "position", None) == target:
                matches.append(agent_id)
        return tuple(matches)

    def queue_affinity_metrics(self) -> Mapping[str, Any]:
        return dict(self._queue_affinity_metrics)

    # ------------------------------------------------------------------
    # Relationship helpers
    # ------------------------------------------------------------------
    def relationship_tie(self, agent_id: str, other_id: str) -> Any:
        return self._relationships.relationship_tie(agent_id, other_id)

    def rivalry_value(self, agent_id: str, other_id: str) -> float:
        return self._relationships.rivalry_value(agent_id, other_id)

    def rivalry_should_avoid(self, agent_id: str, other_id: str) -> bool:
        return self._relationships.rivalry_should_avoid(agent_id, other_id)

    # ------------------------------------------------------------------
    # Mutation hooks (fallback to legacy world until event pipeline replaces them)
    # ------------------------------------------------------------------
    def record_chat_failure(self, speaker: str, listener: str) -> None:
        payload = {"speaker": speaker, "listener": listener}
        self._emit_guardrail_request("chat_failure", payload)

    def record_relationship_guard_block(
        self,
        *,
        agent_id: str,
        reason: str,
        target_agent: str | None = None,
        object_id: str | None = None,
    ) -> None:
        payload = {
            "agent_id": agent_id,
            "reason": reason,
            "target_agent": target_agent,
            "object_id": object_id,
        }
        self._emit_guardrail_request("relationship_block", payload)

    def _emit_guardrail_request(
        self,
        variant: str,
        payload: Mapping[str, Any],
    ) -> None:
        request = {"variant": variant}
        for key, value in payload.items():
            if value is not None:
                request[key] = value

        emitter = self._guardrail_emitter
        if callable(emitter):
            emitter("policy.guardrail.request", request)
            return

        world = self._world
        if world is not None and hasattr(world, "emit_event"):
            world.emit_event("policy.guardrail.request", request)
            return

        # Fallback for legacy contexts lacking emit_event (should be temporary).
        if (
            variant == "chat_failure"
            and world is not None
            and hasattr(world, "record_chat_failure")
        ):
            world.record_chat_failure(
                payload.get("speaker"),
                payload.get("listener"),
            )
        elif (
            variant == "relationship_block"
            and world is not None
            and hasattr(world, "record_relationship_guard_block")
        ):
                world.record_relationship_guard_block(
                    agent_id=payload.get("agent_id"),
                    reason=payload.get("reason"),
                    target_agent=payload.get("target_agent"),
                    object_id=payload.get("object_id"),
                )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_agent_snapshots(
        self,
        agents: Sequence[AgentObservationDTO],
        *,
        world_agent_lookup: Any,
    ) -> dict[str, SimpleNamespace]:
        if not agents:
            return {}
        lookup: dict[str, SimpleNamespace] = {}
        for agent in agents:
            agent_id = str(agent.agent_id)
            needs = dict(agent.needs or {})
            wallet = float(agent.wallet) if agent.wallet is not None else None
            inventory = dict(agent.inventory or {})
            job_payload = dict(agent.job or {})
            metadata = dict(agent.metadata or {})
            pending_intent = (
                dict(agent.pending_intent) if agent.pending_intent else None
            )
            position = None
            if agent.position and len(agent.position) >= 2:
                try:
                    position = (int(agent.position[0]), int(agent.position[1]))
                except Exception:  # pragma: no cover - defensive
                    position = None
            personality_ns = None
            if agent.personality and isinstance(agent.personality, Mapping):
                personality_ns = SimpleNamespace(**agent.personality)
            snapshot = SimpleNamespace(
                agent_id=agent_id,
                needs=needs,
                wallet=wallet,
                inventory=inventory,
                job=job_payload,
                job_id=job_payload.get("job_id"),
                on_shift=bool(job_payload.get("on_shift", False)),
                shift_state=job_payload.get("shift_state"),
                lateness_counter=int(job_payload.get("lateness_counter", 0)),
                attendance_ratio=float(job_payload.get("attendance_ratio", 0.0)),
                exit_pending=bool(job_payload.get("exit_pending", False)),
                position=position,
                personality=personality_ns,
                personality_profile=metadata.get("personality_profile"),
                metadata=metadata,
                pending_intent=pending_intent,
                queue_state=dict(agent.queue_state or {}),
            )
            lookup[agent_id] = snapshot
        return lookup


__all__ = [
    "DTOQueueManagerView",
    "DTOAffordanceRuntimeView",
    "DTORelationshipView",
    "DTOWorldView",
]

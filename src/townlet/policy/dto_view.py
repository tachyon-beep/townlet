"""DTO-backed view exposing world data for policy behaviours."""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Callable, Mapping

from townlet.world.dto.observation import ObservationEnvelope


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
        self.tick = getattr(world, "tick", envelope.tick)
        self._guardrail_emitter = guardrail_emitter

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


__all__ = [
    "DTOQueueManagerView",
    "DTOAffordanceRuntimeView",
    "DTORelationshipView",
    "DTOWorldView",
]

"""Queue conflict and rivalry event tracking."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from typing import Any


class QueueConflictTracker:
    """Tracks queue conflict outcomes and rivalry/chat events."""

    def __init__(
        self,
        *,
        world: Any,
        record_rivalry_conflict: Callable[..., None],
    ) -> None:
        self._world = world
        self._record_rivalry_conflict_cb = record_rivalry_conflict
        self._rivalry_events: deque[dict[str, object]] = deque(maxlen=256)
        self._chat_events: list[dict[str, object]] = []
        self._avoidance_events: list[dict[str, object]] = []

    def record_queue_conflict(
        self,
        *,
        object_id: str,
        actor: str,
        rival: str,
        reason: str,
        queue_length: int,
        intensity: float | None = None,
    ) -> None:
        if actor == rival:
            return
        world = self._world
        payload = {
            "object_id": object_id,
            "actor": actor,
            "rival": rival,
            "reason": reason,
            "queue_length": queue_length,
        }
        if reason == "handover":
            world.update_relationship(
                actor,
                rival,
                trust=0.05,
                familiarity=0.05,
                rivalry=-0.05,
                event="queue_polite",
            )
            world._emit_event("queue_interaction", {**payload, "variant": "handover"})
            return

        params = world.config.conflict.rivalry
        base_intensity = intensity
        if base_intensity is None:
            boost = params.ghost_step_boost if reason == "ghost_step" else params.handover_boost
            base_intensity = boost + params.queue_length_boost * max(queue_length - 1, 0)
        clamped_intensity = min(5.0, max(0.1, base_intensity))
        self._record_rivalry_conflict_cb(
            actor,
            rival,
            intensity=clamped_intensity,
            reason=reason,
        )
        world.update_relationship(
            actor,
            rival,
            rivalry=0.05 * clamped_intensity,
            event="conflict",
        )
        world._emit_event(
            "queue_conflict",
            {
                **payload,
                "intensity": clamped_intensity,
            },
        )
        self.record_rivalry_event(
            tick=world.tick,
            agent_a=actor,
            agent_b=rival,
            intensity=clamped_intensity,
            reason=reason,
        )

    def record_chat_event(self, payload: dict[str, object]) -> None:
        self._chat_events.append(payload)

    def consume_chat_events(self) -> list[dict[str, object]]:
        events = list(self._chat_events)
        self._chat_events.clear()
        return events

    def record_avoidance_event(self, payload: dict[str, object]) -> None:
        self._avoidance_events.append(payload)

    def consume_avoidance_events(self) -> list[dict[str, object]]:
        events = list(self._avoidance_events)
        self._avoidance_events.clear()
        return events

    def record_rivalry_event(
        self,
        *,
        tick: int,
        agent_a: str,
        agent_b: str,
        intensity: float,
        reason: str,
    ) -> None:
        self._rivalry_events.append(
            {
                "tick": int(tick),
                "agent_a": agent_a,
                "agent_b": agent_b,
                "intensity": float(intensity),
                "reason": reason,
            }
        )

    def consume_rivalry_events(self) -> list[dict[str, object]]:
        if not self._rivalry_events:
            return []
        events = list(self._rivalry_events)
        self._rivalry_events.clear()
        return events

    def reset(self) -> None:
        self._rivalry_events.clear()
        self._chat_events.clear()
        self._avoidance_events.clear()

    def remove_agent(self, agent_id: str) -> None:
        self._chat_events = [
            entry
            for entry in self._chat_events
            if entry.get("agent") != agent_id
            and entry.get("speaker") != agent_id
            and entry.get("listener") != agent_id
        ]
        self._avoidance_events = [
            entry for entry in self._avoidance_events if entry.get("agent") != agent_id
        ]
        filtered = (
            event
            for event in self._rivalry_events
            if agent_id not in (event.get("agent_a"), event.get("agent_b"))
        )
        self._rivalry_events = deque(filtered, maxlen=self._rivalry_events.maxlen)

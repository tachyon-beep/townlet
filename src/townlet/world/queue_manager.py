"""Queue management with fairness guardrails.

This module implements the queue semantics described in docs/REQUIREMENTS.md#5.
Queues are maintained per interactive object, and fairness is controlled through
cooldowns, queue-age prioritisation, and a ghost-step breaker that prevents
long-lived deadlocks.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from townlet.config import QueueFairnessConfig, SimulationConfig


@dataclass
class QueueEntry:
    """Represents an agent waiting to access an interactive object."""

    agent_id: str
    joined_tick: int


class QueueManager:
    """Coordinates reservations and fairness across interactive queues."""

    def __init__(self, config: SimulationConfig) -> None:
        self._settings: QueueFairnessConfig = config.queue_fairness
        self._queues: dict[str, list[QueueEntry]] = {}
        self._active: dict[str, str] = {}
        self._cooldowns: dict[tuple[str, str], int] = {}
        self._stall_counts: dict[str, int] = {}
        self._metrics: dict[str, int] = {
            "cooldown_events": 0,
            "ghost_step_events": 0,
        }
        self._perf_metrics: dict[str, int] = {
            "request_ns": 0,
            "release_ns": 0,
            "assign_ns": 0,
            "blocked_ns": 0,
            "requests": 0,
            "releases": 0,
            "assign_calls": 0,
            "blocked_calls": 0,
        }

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def on_tick(self, tick: int) -> None:
        """Expire cooldown entries whose window has elapsed."""
        expired = [key for key, expiry in self._cooldowns.items() if expiry <= tick]
        for key in expired:
            del self._cooldowns[key]

    def request_access(self, object_id: str, agent_id: str, tick: int) -> bool:
        """Attempt to reserve the object for the agent.

        Returns True if the agent is granted the reservation immediately,
        otherwise the agent is queued and False is returned.
        """
        start = time.perf_counter_ns()
        self._perf_metrics["requests"] += 1
        try:
            cooldown_key = (object_id, agent_id)
            expiry = self._cooldowns.get(cooldown_key)
            if expiry is not None and tick < expiry:
                self._metrics["cooldown_events"] += 1
                return False

            current = self._active.get(object_id)
            if current == agent_id:
                return True

            queue = self._queues.setdefault(object_id, [])
            if any(entry.agent_id == agent_id for entry in queue):
                return False

            queue.append(QueueEntry(agent_id=agent_id, joined_tick=tick))
            granted = self._assign_next(object_id, tick)
            return granted == agent_id
        finally:
            self._perf_metrics["request_ns"] += time.perf_counter_ns() - start

    def release(
        self, object_id: str, agent_id: str, tick: int, *, success: bool = True
    ) -> None:
        """Release the reservation and optionally apply cooldown."""
        start = time.perf_counter_ns()
        self._perf_metrics["releases"] += 1
        try:
            if self._active.get(object_id) != agent_id:
                return

            del self._active[object_id]
            if success:
                self._cooldowns[(object_id, agent_id)] = (
                    tick + self._settings.cooldown_ticks
                )
            else:
                self._cooldowns.pop((object_id, agent_id), None)
            self._stall_counts.pop(object_id, None)
            self._assign_next(object_id, tick)
        finally:
            self._perf_metrics["release_ns"] += time.perf_counter_ns() - start

    def record_blocked_attempt(self, object_id: str) -> bool:
        """Register that the current head was blocked.

        Returns True if a ghost-step should be triggered for the head agent.
        """
        start = time.perf_counter_ns()
        self._perf_metrics["blocked_calls"] += 1
        try:
            limit = self._settings.ghost_step_after
            if limit == 0:
                return False

            count = self._stall_counts.get(object_id, 0) + 1
            if count >= limit:
                self._stall_counts[object_id] = 0
                self._metrics["ghost_step_events"] += 1
                return True

            self._stall_counts[object_id] = count
            return False
        finally:
            self._perf_metrics["blocked_ns"] += time.perf_counter_ns() - start

    def active_agent(self, object_id: str) -> str | None:
        """Return the agent currently holding the reservation, if any."""
        return self._active.get(object_id)

    def queue_snapshot(self, object_id: str) -> list[str]:
        """Return the queue as an ordered list of agent IDs for debugging."""
        return [entry.agent_id for entry in self._queues.get(object_id, [])]

    def metrics(self) -> dict[str, int]:
        """Expose counters useful for telemetry."""
        return dict(self._metrics)

    def performance_metrics(self) -> dict[str, int]:
        """Expose aggregated nanosecond timings and call counts."""
        return dict(self._perf_metrics)

    def reset_performance_metrics(self) -> None:
        for key in self._perf_metrics:
            self._perf_metrics[key] = 0

    def export_state(self) -> dict[str, object]:
        """Serialise queue activity for snapshot persistence."""

        return {
            "active": dict(self._active),
            "queues": {
                object_id: [
                    {"agent_id": entry.agent_id, "joined_tick": entry.joined_tick}
                    for entry in entries
                ]
                for object_id, entries in self._queues.items()
            },
            "cooldowns": [
                {
                    "object_id": object_id,
                    "agent_id": agent_id,
                    "expiry": expiry,
                }
                for (object_id, agent_id), expiry in self._cooldowns.items()
            ],
            "stall_counts": dict(self._stall_counts),
        }

    def import_state(self, payload: dict[str, object]) -> None:
        """Restore queue activity from persisted snapshot data."""

        active = payload.get("active", {})
        if isinstance(active, dict):
            self._active = {
                str(obj_id): str(agent_id) for obj_id, agent_id in active.items()
            }
        else:
            self._active = {}

        queues_payload = payload.get("queues", {})
        queues: dict[str, list[QueueEntry]] = {}
        if isinstance(queues_payload, dict):
            for object_id, entries in queues_payload.items():
                object_entries: list[QueueEntry] = []
                for entry in entries or []:
                    agent_id = str(entry.get("agent_id"))
                    joined_tick = int(entry.get("joined_tick", 0))
                    object_entries.append(
                        QueueEntry(agent_id=agent_id, joined_tick=joined_tick)
                    )
                queues[str(object_id)] = object_entries
        self._queues = queues

        cooldown_payload = payload.get("cooldowns", [])
        self._cooldowns = {}
        for entry in cooldown_payload or []:
            object_id = str(entry.get("object_id"))
            agent_id = str(entry.get("agent_id"))
            expiry = int(entry.get("expiry", 0))
            self._cooldowns[(object_id, agent_id)] = expiry

        stall_payload = payload.get("stall_counts", {})
        if isinstance(stall_payload, dict):
            self._stall_counts = {
                str(obj_id): int(count) for obj_id, count in stall_payload.items()
            }
        else:
            self._stall_counts = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _assign_next(self, object_id: str, tick: int) -> str | None:
        start = time.perf_counter_ns()
        self._perf_metrics["assign_calls"] += 1
        try:
            if self._active.get(object_id) is not None:
                return None

            queue = self._queues.get(object_id)
            if not queue:
                return None

            best_index: int | None = None
            best_priority: float | None = None
            for index, entry in enumerate(queue):
                wait_time = tick - entry.joined_tick
                priority = float(index) - self._settings.age_priority_weight * float(
                    wait_time
                )
                if best_priority is None or priority < best_priority:
                    best_priority = priority
                    best_index = index

            if best_index is None:
                return None

            entry = queue.pop(best_index)
            self._active[object_id] = entry.agent_id
            self._stall_counts.pop(object_id, None)
            return entry.agent_id
        finally:
            self._perf_metrics["assign_ns"] += time.perf_counter_ns() - start

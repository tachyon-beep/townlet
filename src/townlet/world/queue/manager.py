"""Queue management with fairness guardrails."""

from __future__ import annotations

import time
from collections.abc import Mapping
from dataclasses import dataclass

from townlet.config import QueueFairnessConfig, SimulationConfig


@dataclass
class QueueEntry:
    agent_id: str
    joined_tick: int


class QueueManager:
    def __init__(self, config: SimulationConfig) -> None:
        self._settings: QueueFairnessConfig = config.queue_fairness
        self._queues: dict[str, list[QueueEntry]] = {}
        self._active: dict[str, str] = {}
        self._cooldowns: dict[tuple[str, str], int] = {}
        self._stall_counts: dict[str, int] = {}
        self._metrics: dict[str, int] = {
            "cooldown_events": 0,
            "ghost_step_events": 0,
            "rotation_events": 0,
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

    def on_tick(self, tick: int) -> None:
        expired = [key for key, expiry in self._cooldowns.items() if expiry <= tick]
        for key in expired:
            del self._cooldowns[key]

    def request_access(self, object_id: str, agent_id: str, tick: int) -> bool:
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

    def release(self, object_id: str, agent_id: str, tick: int, *, success: bool = True) -> None:
        start = time.perf_counter_ns()
        self._perf_metrics["releases"] += 1
        try:
            if self._active.get(object_id) != agent_id:
                return

            del self._active[object_id]
            if success:
                self._cooldowns[(object_id, agent_id)] = tick + self._settings.cooldown_ticks
            else:
                self._cooldowns.pop((object_id, agent_id), None)
            self._stall_counts.pop(object_id, None)
            self._assign_next(object_id, tick)
        finally:
            self._perf_metrics["release_ns"] += time.perf_counter_ns() - start

    def record_blocked_attempt(self, object_id: str) -> bool:
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
        return self._active.get(object_id)

    def queue_snapshot(self, object_id: str) -> list[str]:
        return [entry.agent_id for entry in self._queues.get(object_id, [])]

    def metrics(self) -> dict[str, int]:
        return dict(self._metrics)

    def performance_metrics(self) -> dict[str, int]:
        return dict(self._perf_metrics)

    def reset_performance_metrics(self) -> None:
        for key in self._perf_metrics:
            self._perf_metrics[key] = 0

    def requeue_to_tail(self, object_id: str, agent_id: str, tick: int) -> None:
        queue = self._queues.setdefault(object_id, [])
        if any(entry.agent_id == agent_id for entry in queue):
            return
        queue.append(QueueEntry(agent_id=agent_id, joined_tick=tick))
        self._metrics["rotation_events"] += 1

    def promote_agent(self, object_id: str, agent_id: str) -> None:
        queue = self._queues.get(object_id)
        if not queue:
            return
        for index, entry in enumerate(queue):
            if entry.agent_id == agent_id:
                if index == 0:
                    return
                queue.insert(0, queue.pop(index))
                self._metrics["rotation_events"] += 1
                break

    def remove_agent(self, agent_id: str, tick: int) -> None:
        for object_id, current in list(self._active.items()):
            if current == agent_id:
                self.release(object_id, agent_id, tick, success=False)

        for object_id, entries in list(self._queues.items()):
            filtered = [entry for entry in entries if entry.agent_id != agent_id]
            if len(filtered) != len(entries):
                self._queues[object_id] = filtered
            if not filtered:
                self._queues.pop(object_id, None)

    def export_state(self) -> dict[str, object]:
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
        active = payload.get("active", {})
        if isinstance(active, dict):
            self._active = {str(obj_id): str(agent_id) for obj_id, agent_id in active.items()}
        else:
            self._active = {}

        queues_payload = payload.get("queues", {})
        queues: dict[str, list[QueueEntry]] = {}
        if isinstance(queues_payload, dict):
            for object_id, entries in queues_payload.items():
                object_entries: list[QueueEntry] = []
                entries_list = entries if isinstance(entries, list) else []
                for entry in entries_list:
                    if not isinstance(entry, Mapping):
                        continue
                    agent_raw = entry.get("agent_id")
                    if agent_raw is None:
                        continue
                    agent_id = str(agent_raw)
                    joined_tick = int(entry.get("joined_tick", 0))
                    object_entries.append(
                        QueueEntry(agent_id=agent_id, joined_tick=joined_tick)
                    )
                queues[str(object_id)] = object_entries
        self._queues = queues

        cooldown_payload = payload.get("cooldowns", [])
        self._cooldowns = {}
        if isinstance(cooldown_payload, list):
            for entry in cooldown_payload:
                if not isinstance(entry, Mapping):
                    continue
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
                priority = float(index) - self._settings.age_priority_weight * float(wait_time)
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

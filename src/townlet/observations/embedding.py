"""Embedding slot allocation with cooldown logging."""

from __future__ import annotations

from dataclasses import dataclass

from townlet.config import EmbeddingAllocatorConfig, SimulationConfig


@dataclass
class _SlotState:
    """Tracks release metadata for a slot."""

    released_at_tick: int | None = None


class EmbeddingAllocator:
    """Assigns stable embedding slots to agents with a reuse cooldown."""

    def __init__(self, config: SimulationConfig) -> None:
        self._settings: EmbeddingAllocatorConfig = config.embedding_allocator
        self._assignments: dict[str, int] = {}
        self._slot_state: dict[int, _SlotState] = {
            slot: _SlotState() for slot in range(self._settings.max_slots)
        }
        self._available: set[int] = set(self._slot_state)
        self._metrics: dict[str, float] = {
            "allocations_total": 0,
            "forced_reuse_count": 0,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def allocate(self, agent_id: str, tick: int) -> int:
        """Return the embedding slot for the agent, allocating if necessary."""
        existing = self._assignments.get(agent_id)
        if existing is not None:
            return existing

        slot, forced = self._select_slot(tick)
        self._assignments[agent_id] = slot
        self._available.discard(slot)
        self._metrics["allocations_total"] += 1
        if forced:
            self._metrics["forced_reuse_count"] += 1
        return slot

    def release(self, agent_id: str, tick: int) -> None:
        """Release the slot held by the agent."""
        slot = self._assignments.pop(agent_id, None)
        if slot is None:
            return
        self._available.add(slot)
        self._slot_state[slot].released_at_tick = tick

    def has_assignment(self, agent_id: str) -> bool:
        """Return whether the allocator still tracks the agent."""
        return agent_id in self._assignments

    def metrics(self) -> dict[str, float]:
        """Expose allocation metrics for telemetry."""
        total = self._metrics["allocations_total"] or 1.0
        forced = self._metrics["forced_reuse_count"]
        rate = forced / total
        warning_threshold = self._settings.reuse_warning_threshold
        return {
            "allocations_total": self._metrics["allocations_total"],
            "forced_reuse_count": forced,
            "forced_reuse_rate": rate,
            "reuse_warning": bool(warning_threshold and rate > warning_threshold),
        }

    def export_state(self) -> dict[str, object]:
        """Serialise allocator bookkeeping for snapshot persistence."""

        return {
            "assignments": dict(self._assignments),
            "available": sorted(self._available),
            "slot_state": {
                slot: state.released_at_tick for slot, state in self._slot_state.items()
            },
            "metrics": dict(self._metrics),
        }

    def import_state(self, payload: dict[str, object]) -> None:
        """Restore allocator bookkeeping from snapshot data."""

        assignments = payload.get("assignments", {})
        if isinstance(assignments, dict):
            self._assignments = {
                str(agent_id): int(slot) for agent_id, slot in assignments.items()
            }
        else:
            self._assignments = {}

        available = payload.get("available", [])
        if isinstance(available, list):
            self._available = {int(slot) for slot in available}
        else:
            self._available = set(self._slot_state)
        # Assigned slots should not remain in the available set.
        for slot in self._assignments.values():
            self._available.discard(slot)

        slot_state = payload.get("slot_state", {})
        if isinstance(slot_state, dict):
            for slot, state in self._slot_state.items():
                released = slot_state.get(str(slot))
                state.released_at_tick = None if released is None else int(released)
        else:
            for state in self._slot_state.values():
                state.released_at_tick = None

        metrics = payload.get("metrics", {})
        if isinstance(metrics, dict):
            self._metrics = {
                "allocations_total": float(metrics.get("allocations_total", 0.0)),
                "forced_reuse_count": float(metrics.get("forced_reuse_count", 0.0)),
            }
        else:
            self._metrics = {
                "allocations_total": 0.0,
                "forced_reuse_count": 0.0,
            }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _select_slot(self, tick: int) -> tuple[int, bool]:
        cooldown = self._settings.cooldown_ticks
        ready_slot: int | None = None
        ready_priority: tuple[int, int] | None = None

        for slot in sorted(self._available):
            released_at = self._slot_state[slot].released_at_tick
            if released_at is None:
                return slot, False
            wait_time = tick - released_at
            key = (released_at, slot)
            if wait_time >= cooldown:
                if ready_priority is None or key < ready_priority:
                    ready_slot = slot
                    ready_priority = key

        if ready_slot is not None:
            return ready_slot, False

        # Forced reuse: pick the slot with oldest release time.
        if not self._available:
            raise RuntimeError("No embedding slots available; increase max_slots")

        forced_slot = min(
            self._available,
            key=lambda slot: (
                self._slot_state[slot].released_at_tick or float("inf"),
                slot,
            ),
        )
        return forced_slot, True

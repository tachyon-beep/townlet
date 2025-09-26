"""Telemetry pipelines and console bridge."""
from __future__ import annotations

from typing import Callable, Dict, Iterable, List, TYPE_CHECKING

from townlet.config import SimulationConfig

if TYPE_CHECKING:
    from townlet.world.grid import WorldState


class TelemetryPublisher:
    """Publishes observer snapshots and consumes console commands."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.schema_version = "0.6.0"
        self._console_buffer: List[object] = []
        self._latest_queue_metrics: Dict[str, int] | None = None
        self._latest_embedding_metrics: Dict[str, float] | None = None
        self._latest_events: List[Dict[str, object]] = []
        self._event_subscribers: List[Callable[[List[Dict[str, object]]], None]] = []
        self._latest_employment_metrics: Dict[str, object] = {}
        self._latest_conflict_snapshot: Dict[str, object] = {
            "queues": {"cooldown_events": 0, "ghost_step_events": 0},
            "rivalry": {},
        }
        self._latest_relationship_metrics: Dict[str, object] | None = None
        self._latest_job_snapshot: Dict[str, object] = {}
        self._latest_economy_snapshot: Dict[str, object] = {}
        self._latest_relationship_snapshot: Dict[str, Dict[str, Dict[str, float]]] = {}
        self._latest_relationship_updates: List[Dict[str, object]] = []
        self._previous_relationship_snapshot: Dict[str, Dict[str, Dict[str, float]]] = {}

    def queue_console_command(self, command: object) -> None:
        self._console_buffer.append(command)

    def drain_console_buffer(self) -> Iterable[object]:
        drained = list(self._console_buffer)
        self._console_buffer.clear()
        return drained

    def export_state(self) -> Dict[str, object]:
        state: Dict[str, object] = {
            "queue_metrics": dict(self._latest_queue_metrics or {}),
            "embedding_metrics": dict(self._latest_embedding_metrics or {}),
            "conflict_snapshot": dict(self._latest_conflict_snapshot),
            "relationship_metrics": dict(self._latest_relationship_metrics or {}),
            "job_snapshot": dict(getattr(self, "_latest_job_snapshot", {})),
            "economy_snapshot": dict(getattr(self, "_latest_economy_snapshot", {})),
            "employment_metrics": dict(self._latest_employment_metrics or {}),
            "events": list(self._latest_events),
            "relationship_snapshot": self._copy_relationship_snapshot(
                self._latest_relationship_snapshot
            ),
            "relationship_updates": [dict(update) for update in self._latest_relationship_updates],
        }
        return state

    def import_state(self, payload: Dict[str, object]) -> None:
        self._latest_queue_metrics = payload.get("queue_metrics") or None
        if self._latest_queue_metrics is not None:
            self._latest_queue_metrics = dict(self._latest_queue_metrics)

        self._latest_embedding_metrics = payload.get("embedding_metrics") or None
        if self._latest_embedding_metrics is not None:
            self._latest_embedding_metrics = dict(self._latest_embedding_metrics)

        conflict_snapshot = payload.get("conflict_snapshot") or {}
        self._latest_conflict_snapshot = dict(conflict_snapshot)

        relationship_metrics = payload.get("relationship_metrics")
        self._latest_relationship_metrics = (
            dict(relationship_metrics) if relationship_metrics else None
        )

        self._latest_job_snapshot = dict(payload.get("job_snapshot", {}))
        self._latest_economy_snapshot = dict(payload.get("economy_snapshot", {}))
        self._latest_employment_metrics = dict(payload.get("employment_metrics", {}))
        self._latest_events = list(payload.get("events", []))
        snapshot_payload = payload.get("relationship_snapshot") or {}
        if isinstance(snapshot_payload, dict):
            self._latest_relationship_snapshot = self._copy_relationship_snapshot(snapshot_payload)
            self._previous_relationship_snapshot = self._copy_relationship_snapshot(snapshot_payload)
        updates_payload = payload.get("relationship_updates", [])
        if isinstance(updates_payload, list):
            self._latest_relationship_updates = [dict(update) for update in updates_payload]

    def export_console_buffer(self) -> List[object]:
        return list(self._console_buffer)

    def import_console_buffer(self, buffer: Iterable[object]) -> None:
        self._console_buffer = list(buffer)

    def publish_tick(
        self,
        *,
        tick: int,
        world: "WorldState",
        observations: Dict[str, object],
        rewards: Dict[str, float],
        events: Iterable[Dict[str, object]] | None = None,
    ) -> None:
        # TODO(@townlet): Stream to pub/sub, write KPIs, emit narration.
        _ = tick, world, observations, rewards
        queue_metrics = world.queue_manager.metrics()
        self._latest_queue_metrics = queue_metrics
        rivalry_snapshot: Dict[str, object] = {}
        rivalry_getter = getattr(world, "rivalry_snapshot", None)
        if callable(rivalry_getter):
            rivalry_snapshot = dict(rivalry_getter())
        self._latest_conflict_snapshot = {
            "queues": dict(queue_metrics),
            "rivalry": rivalry_snapshot,
        }
        relationship_metrics_getter = getattr(
            world, "relationship_metrics_snapshot", None
        )
        if callable(relationship_metrics_getter):
            metrics_snapshot = relationship_metrics_getter()
            if metrics_snapshot is not None:
                self._latest_relationship_metrics = dict(metrics_snapshot)
        relationship_snapshot = self._capture_relationship_snapshot(world)
        self._latest_relationship_updates = self._compute_relationship_updates(
            self._previous_relationship_snapshot,
            relationship_snapshot,
        )
        self._latest_relationship_snapshot = relationship_snapshot
        self._previous_relationship_snapshot = self._copy_relationship_snapshot(
            relationship_snapshot
        )
        self._latest_embedding_metrics = world.embedding_allocator.metrics()
        if events is not None:
            self._latest_events = list(events)
        else:
            self._latest_events = []
        for subscriber in self._event_subscribers:
            subscriber(list(self._latest_events))
        self._latest_job_snapshot = {
            agent_id: {
                "job_id": snapshot.job_id,
                "on_shift": snapshot.on_shift,
                "wallet": snapshot.wallet,
                "lateness_counter": snapshot.lateness_counter,
                "wages_earned": snapshot.inventory.get("wages_earned", 0),
                "meals_cooked": snapshot.inventory.get("meals_cooked", 0),
                "meals_consumed": snapshot.inventory.get("meals_consumed", 0),
                "basket_cost": snapshot.inventory.get("basket_cost", 0.0),
                "shift_state": snapshot.shift_state,
                "attendance_ratio": snapshot.attendance_ratio,
                "late_ticks_today": snapshot.late_ticks_today,
                "absent_shifts_7d": snapshot.absent_shifts_7d,
                "wages_withheld": snapshot.wages_withheld,
                "exit_pending": snapshot.exit_pending,
            }
            for agent_id, snapshot in world.agents.items()
        }
        self._latest_economy_snapshot = {
            object_id: {
                "type": obj.object_type,
                "stock": dict(obj.stock),
            }
            for object_id, obj in world.objects.items()
        }
        self._latest_employment_metrics = world.employment_queue_snapshot()

    def latest_queue_metrics(self) -> Dict[str, int] | None:
        """Expose the most recent queue-related telemetry counters."""
        if self._latest_queue_metrics is None:
            return None
        return dict(self._latest_queue_metrics)

    def latest_conflict_snapshot(self) -> Dict[str, object]:
        """Return the conflict-focused telemetry payload (queues + rivalry)."""
        snapshot = dict(self._latest_conflict_snapshot)
        queues = snapshot.get("queues")
        if isinstance(queues, dict):
            snapshot["queues"] = dict(queues)
        return snapshot

    def latest_relationship_metrics(self) -> Dict[str, object] | None:
        """Expose relationship churn payload captured during publish."""
        if self._latest_relationship_metrics is None:
            return None
        payload = dict(self._latest_relationship_metrics)
        history = payload.get("history")
        if isinstance(history, list):
            payload["history"] = [dict(entry) for entry in history]
        return payload

    def latest_relationship_snapshot(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        return self._copy_relationship_snapshot(self._latest_relationship_snapshot)

    def latest_relationship_updates(self) -> List[Dict[str, object]]:
        return [dict(update) for update in self._latest_relationship_updates]

    def update_relationship_metrics(self, payload: Dict[str, object]) -> None:
        """Allow external callers to seed the latest relationship metrics."""
        self._latest_relationship_metrics = dict(payload)

    def latest_embedding_metrics(self) -> Dict[str, float] | None:
        """Expose embedding allocator counters."""
        if self._latest_embedding_metrics is None:
            return None
        return dict(self._latest_embedding_metrics)

    def latest_events(self) -> Iterable[Dict[str, object]]:
        """Return the most recent event batch."""
        return getattr(self, "_latest_events", [])

    def register_event_subscriber(
        self, subscriber: Callable[[List[Dict[str, object]]], None]
    ) -> None:
        """Register a callback to receive each tick's event batch."""
        self._event_subscribers.append(subscriber)

    def latest_job_snapshot(self) -> Dict[str, Dict[str, object]]:
        return getattr(self, "_latest_job_snapshot", {})

    def latest_economy_snapshot(self) -> Dict[str, Dict[str, object]]:
        return getattr(self, "_latest_economy_snapshot", {})

    def latest_employment_metrics(self) -> Dict[str, object]:
        return dict(getattr(self, "_latest_employment_metrics", {}))

    def schema(self) -> str:
        return self.schema_version

    def _capture_relationship_snapshot(
        self,
        world: "WorldState",
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        snapshot_getter = getattr(world, "relationships_snapshot", None)
        if not callable(snapshot_getter):
            return {}
        raw = snapshot_getter() or {}
        if not isinstance(raw, dict):
            return {}
        normalised: Dict[str, Dict[str, Dict[str, float]]] = {}
        for owner, ties in raw.items():
            if not isinstance(ties, dict):
                continue
            normalised[owner] = {
                other: {
                    "trust": float(values.get("trust", 0.0)),
                    "familiarity": float(values.get("familiarity", 0.0)),
                    "rivalry": float(values.get("rivalry", 0.0)),
                }
                for other, values in ties.items()
                if isinstance(values, dict)
            }
        return normalised

    def _compute_relationship_updates(
        self,
        previous: Dict[str, Dict[str, Dict[str, float]]],
        current: Dict[str, Dict[str, Dict[str, float]]],
    ) -> List[Dict[str, object]]:
        updates: List[Dict[str, object]] = []
        for owner, ties in current.items():
            prev_ties = previous.get(owner, {})
            for other, metrics in ties.items():
                prev_metrics = prev_ties.get(other)
                if prev_metrics is None:
                    updates.append(
                        {
                            "owner": owner,
                            "other": other,
                            "trust": metrics["trust"],
                            "familiarity": metrics["familiarity"],
                            "rivalry": metrics["rivalry"],
                            "status": "added",
                            "delta": dict(metrics),
                        }
                    )
                else:
                    delta_trust = metrics["trust"] - prev_metrics.get("trust", 0.0)
                    delta_fam = metrics["familiarity"] - prev_metrics.get("familiarity", 0.0)
                    delta_riv = metrics["rivalry"] - prev_metrics.get("rivalry", 0.0)
                    if any(abs(delta) > 1e-6 for delta in (delta_trust, delta_fam, delta_riv)):
                        updates.append(
                            {
                                "owner": owner,
                                "other": other,
                                "trust": metrics["trust"],
                                "familiarity": metrics["familiarity"],
                                "rivalry": metrics["rivalry"],
                                "status": "updated",
                                "delta": {
                                    "trust": delta_trust,
                                    "familiarity": delta_fam,
                                    "rivalry": delta_riv,
                                },
                            }
                        )
            for other, prev_metrics in prev_ties.items():
                if other not in ties:
                    updates.append(
                        {
                            "owner": owner,
                            "other": other,
                            "trust": 0.0,
                            "familiarity": 0.0,
                            "rivalry": 0.0,
                            "status": "removed",
                            "delta": {
                                "trust": -prev_metrics.get("trust", 0.0),
                                "familiarity": -prev_metrics.get("familiarity", 0.0),
                                "rivalry": -prev_metrics.get("rivalry", 0.0),
                            },
                        }
                    )
        for owner, ties in previous.items():
            if owner not in current:
                for other, prev_metrics in ties.items():
                    updates.append(
                        {
                            "owner": owner,
                            "other": other,
                            "trust": 0.0,
                            "familiarity": 0.0,
                            "rivalry": 0.0,
                            "status": "removed",
                            "delta": {
                                "trust": -prev_metrics.get("trust", 0.0),
                                "familiarity": -prev_metrics.get("familiarity", 0.0),
                                "rivalry": -prev_metrics.get("rivalry", 0.0),
                            },
                        }
                    )
        return updates

    @staticmethod
    def _copy_relationship_snapshot(
        snapshot: Dict[str, Dict[str, Dict[str, float]]],
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        return {
            owner: {
                other: {
                    "trust": float(values.get("trust", 0.0)),
                    "familiarity": float(values.get("familiarity", 0.0)),
                    "rivalry": float(values.get("rivalry", 0.0)),
                }
                for other, values in ties.items()
            }
            for owner, ties in snapshot.items()
        }

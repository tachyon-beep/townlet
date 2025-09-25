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
        self.schema_version = "0.3.0"
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

    def queue_console_command(self, command: object) -> None:
        self._console_buffer.append(command)

    def drain_console_buffer(self) -> Iterable[object]:
        drained = list(self._console_buffer)
        self._console_buffer.clear()
        return drained

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

"""Context façade exposing shared world services."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, MutableMapping

from townlet.console.service import ConsoleService
from townlet.telemetry.relationship_metrics import RelationshipChurnAccumulator
from townlet.world.affordance_runtime_service import AffordanceRuntimeService
from townlet.world.employment_runtime import EmploymentRuntime
from townlet.world.employment_service import EmploymentCoordinator
from townlet.world.queue_conflict import QueueConflictTracker
from townlet.world.queue_manager import QueueManager


@dataclass(slots=True)
class WorldContext:
    """Lightweight view over world state shared across subsystems.

    This façade allows consumers to traverse core services without depending on
    the full ``WorldState`` implementation. It deliberately exposes read-only
    views for structures that should not be mutated directly.
    """

    agents: MutableMapping[str, object]
    objects: MutableMapping[str, object]
    affordances: MutableMapping[str, object]
    running_affordances: MutableMapping[str, object]
    queue_manager: QueueManager
    queue_conflicts: QueueConflictTracker
    affordance_service: AffordanceRuntimeService
    console: ConsoleService
    employment: EmploymentCoordinator
    employment_runtime: EmploymentRuntime
    relationship_ledgers: Mapping[str, object]
    rivalry_ledgers: Mapping[str, object]
    relationship_churn: RelationshipChurnAccumulator
    config: object
    emit_event_callback: Callable[[str, dict[str, Any]], None]
    sync_reservation_callback: Callable[[str], None]

    def agents_view(self) -> Mapping[str, object]:
        return self.agents

    def objects_view(self) -> Mapping[str, object]:
        return self.objects

    def affordances_view(self) -> Mapping[str, object]:
        return self.affordances

    def running_affordances_view(self) -> Mapping[str, object]:
        return self.running_affordances

    def emit_event(self, event: str, payload: dict[str, Any]) -> None:
        self.emit_event_callback(event, payload)

    def sync_reservation(self, object_id: str) -> None:
        self.sync_reservation_callback(object_id)

    @property
    def console_bridge(self):  # pragma: no cover - thin proxy
        return self.console.bridge

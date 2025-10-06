"""Context façade exposing shared world services."""

from __future__ import annotations

from collections.abc import Callable, Mapping, MutableMapping
from dataclasses import dataclass
from typing import Any

from townlet.console.service import ConsoleService
from townlet.world.affordance_runtime_service import AffordanceRuntimeService
from townlet.world.agents.employment import EmploymentService
from townlet.world.agents.nightly_reset import NightlyResetService
from townlet.world.agents.relationships_service import RelationshipService
from townlet.world.employment_runtime import EmploymentRuntime
from townlet.world.employment_service import EmploymentCoordinator
from townlet.world.queue import QueueConflictTracker, QueueManager


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
    employment_service: EmploymentService
    nightly_reset_service: NightlyResetService
    relationships: RelationshipService
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

    def apply_nightly_reset(self, tick: int) -> list[str]:
        """Delegate nightly reset to the configured service."""

        return self.nightly_reset_service.apply(tick)

    @property
    def console_bridge(self):  # pragma: no cover - thin proxy
        return self.console.bridge

    @property
    def relationship_ledgers(self) -> Mapping[str, object]:
        return self.relationships.relationships_snapshot()

    @property
    def rivalry_ledgers(self) -> Mapping[str, object]:
        return self.relationships.rivalry_snapshot()

    @property
    def relationship_churn(self) -> dict[str, object]:
        return self.relationships.relationship_metrics_snapshot()

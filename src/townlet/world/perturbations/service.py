"""Perturbation helpers for price spikes, outages, and arranged meets."""

from __future__ import annotations

from collections.abc import Callable, Iterable, MutableMapping
from dataclasses import dataclass
from typing import Any

from townlet.world.agents.registry import AgentRegistry


@dataclass(slots=True)
class PerturbationService:
    """Coordinate price spikes, utility outages, and arranged meets."""

    economy_service: Any
    agents: AgentRegistry
    objects: MutableMapping[str, Any]
    emit_event: Callable[[str, dict[str, object]], None]
    request_ctx_reset: Callable[[str], None]
    tick_supplier: Callable[[], int]

    def apply_price_spike(
        self,
        event_id: str,
        *,
        magnitude: float,
        targets: Iterable[str] | None = None,
    ) -> None:
        self.economy_service.apply_price_spike(
            event_id,
            magnitude=magnitude,
            targets=targets,
        )

    def clear_price_spike(self, event_id: str) -> None:
        self.economy_service.clear_price_spike(event_id)

    def apply_utility_outage(self, event_id: str, utility: str) -> None:
        self.economy_service.apply_utility_outage(event_id, utility)

    def clear_utility_outage(self, event_id: str, utility: str) -> None:
        self.economy_service.clear_utility_outage(event_id, utility)

    def apply_arranged_meet(
        self,
        *,
        location: str | None,
        targets: Iterable[str] | None = None,
    ) -> None:
        if not targets:
            return
        obj = None
        if location:
            obj = self.objects.get(location)
            if obj is None:
                for candidate in self.objects.values():
                    if getattr(candidate, "object_type", None) == location:
                        obj = candidate
                        break
        position = None
        if obj is not None and obj.position is not None:
            position = (int(obj.position[0]), int(obj.position[1]))
        if position is None:
            return
        for agent_id in targets:
            snapshot = self.agents.get(str(agent_id))
            if snapshot is None:
                continue
            snapshot.position = position
            self.request_ctx_reset(snapshot.agent_id)
            self.emit_event(
                "arranged_meet_relocated",
                {
                    "agent_id": snapshot.agent_id,
                    "location": obj.object_id if obj is not None else location,
                    "tick": self.tick_supplier(),
                },
            )

    def active_price_spikes(self) -> dict[str, dict[str, object]]:
        spikes = self.economy_service.active_price_spikes()
        if not isinstance(spikes, MutableMapping):
            return {}
        snapshot: dict[str, dict[str, object]] = {}
        for key, value in spikes.items():
            if isinstance(value, MutableMapping):
                snapshot[str(key)] = dict(value)
        return snapshot

    def utility_snapshot(self) -> dict[str, bool]:
        utilities = self.economy_service.utility_snapshot()
        if not isinstance(utilities, MutableMapping):
            return {}
        return {str(name): bool(state) for name, state in utilities.items()}

    def utility_online(self, utility: str) -> bool:
        return bool(self.economy_service.utility_online(utility))


__all__ = ["PerturbationService"]

"""Economy and utility helpers extracted from the world grid module."""

from __future__ import annotations

from collections.abc import Callable, Iterable, MutableMapping
from dataclasses import dataclass, field
from typing import Any

from townlet.config import SimulationConfig
from townlet.world.agents.registry import AgentRegistry
from townlet.world.queue import QueueManager


@dataclass(frozen=True, slots=True)
class PriceSpikeEvent:
    magnitude: float
    targets: tuple[str, ...]


@dataclass(slots=True)
class EconomyService:
    """Manage economy values, price spikes, and utility outages."""

    config: SimulationConfig
    agents: AgentRegistry
    objects: MutableMapping[str, Any]
    queue_manager: QueueManager
    sync_reservation: Callable[[str], None]
    emit_event: Callable[[str, dict[str, object]], None]
    tick_supplier: Callable[[], int]

    _economy_baseline: dict[str, float] = field(init=False)
    _price_spike_events: dict[str, PriceSpikeEvent] = field(init=False, default_factory=dict)
    _utility_status: dict[str, bool] = field(init=False)
    _utility_events: dict[str, set[str]] = field(init=False)
    _object_utility_baselines: dict[str, dict[str, float]] = field(init=False, default_factory=dict)
    _agent_basket_costs: dict[str, float] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        self._economy_baseline = {
            key: float(value) for key, value in self.config.economy.items()
        }
        self._price_spike_events = {}
        self._utility_status = {"power": True, "water": True}
        self._utility_events = {"power": set(), "water": set()}
        self._object_utility_baselines = {}

    # ------------------------------------------------------------------
    # Economy helpers
    # ------------------------------------------------------------------
    def update_basket_metrics(self) -> None:
        basket_cost = (
            self.config.economy.get("meal_cost", 0.0)
            + self.config.economy.get("cook_energy_cost", 0.0)
            + self.config.economy.get("cook_hygiene_cost", 0.0)
            + self.config.economy.get("ingredients_cost", 0.0)
        )
        basket_costs: dict[str, float] = {}
        for snapshot in self.agents.values():
            basket_costs[str(snapshot.agent_id)] = float(basket_cost)
        self.restock_economy()
        self._agent_basket_costs = basket_costs

    def restock_economy(self) -> None:
        restock_amount = int(self.config.economy.get("stove_stock_replenish", 0))
        if restock_amount <= 0:
            return
        if self.tick_supplier() % 200 != 0:
            return
        for obj in self.objects.values():
            if getattr(obj, "object_type", None) == "stove":
                before = obj.stock.get("raw_ingredients", 0)
                obj.stock["raw_ingredients"] = before + restock_amount
                self.emit_event(
                    "stock_replenish",
                    {
                        "object_id": obj.object_id,
                        "type": "stove",
                        "amount": restock_amount,
                    },
                )

    def set_price_target(self, key: str, value: float) -> float:
        normalised = str(key)
        if normalised not in self.config.economy:
            raise KeyError(normalised)
        numeric = float(value)
        self.config.economy[normalised] = numeric
        self._economy_baseline[normalised] = numeric
        self.update_basket_metrics()
        self.emit_event(
            "economy_price_update",
            {
                "key": normalised,
                "value": numeric,
            },
        )
        return numeric

    # ------------------------------------------------------------------
    # Price spike helpers
    # ------------------------------------------------------------------
    def apply_price_spike(
        self,
        event_id: str,
        *,
        magnitude: float,
        targets: Iterable[str] | None = None,
    ) -> None:
        resolved = self._resolve_price_targets(targets)
        if not resolved:
            return
        self._price_spike_events[event_id] = PriceSpikeEvent(
            magnitude=max(float(magnitude), 0.0),
            targets=resolved,
        )
        self._recompute_price_spikes()

    def clear_price_spike(self, event_id: str) -> None:
        if event_id not in self._price_spike_events:
            return
        self._price_spike_events.pop(event_id, None)
        self._recompute_price_spikes()

    def _resolve_price_targets(self, targets: Iterable[str] | None) -> tuple[str, ...]:
        resolved: list[str] = []
        if not targets:
            return tuple(self._economy_baseline.keys())
        groups = {
            "global": list(self.config.economy.keys()),
            "market": [
                "meal_cost",
                "cook_energy_cost",
                "cook_hygiene_cost",
                "ingredients_cost",
            ],
        }
        for target in targets:
            key = str(target).lower()
            if key in groups:
                for entry in groups[key]:
                    if entry in self.config.economy and entry not in resolved:
                        resolved.append(entry)
                continue
            if key in self.config.economy and key not in resolved:
                resolved.append(key)
        return tuple(resolved)

    def _recompute_price_spikes(self) -> None:
        for key, value in self._economy_baseline.items():
            self.config.economy[key] = value
        for event in self._price_spike_events.values():
            magnitude = max(event.magnitude, 0.0)
            for key in event.targets:
                if key in self.config.economy:
                    self.config.economy[key] = self.config.economy[key] * magnitude
        self.update_basket_metrics()

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def apply_utility_outage(self, event_id: str, utility: str) -> None:
        util = utility.lower()
        events = self._utility_events.setdefault(util, set())
        if event_id in events:
            return
        events.add(event_id)
        if len(events) == 1:
            self._set_utility_state(util, online=False)

    def clear_utility_outage(self, event_id: str, utility: str) -> None:
        util = utility.lower()
        events = self._utility_events.setdefault(util, set())
        if event_id not in events:
            return
        events.discard(event_id)
        if not events:
            self._set_utility_state(util, online=True)

    def _set_utility_state(self, utility: str, *, online: bool) -> None:
        utility_key = utility.lower()
        self._utility_status[utility_key] = online
        affected_types = {
            "power": {"stove"},
            "water": {"shower", "sink"},
        }.get(utility_key, set())
        flag = f"{utility_key}_on"
        for obj in self.objects.values():
            if affected_types and getattr(obj, "object_type", None) not in affected_types:
                continue
            baseline_flags = self._object_utility_baselines.setdefault(obj.object_id, {})
            if not online:
                baseline_flags.setdefault(flag, float(obj.stock.get(flag, 1.0)))
                obj.stock[flag] = 0.0
                active_agent = self.queue_manager.active_agent(obj.object_id)
                if active_agent is not None:
                    self.queue_manager.release(
                        obj.object_id, active_agent, self.tick_supplier(), success=False
                    )
                    self.sync_reservation(obj.object_id)
            else:
                baseline = baseline_flags.get(flag, 1.0)
                obj.stock[flag] = baseline

    # ------------------------------------------------------------------
    # Snapshots & inspectors
    # ------------------------------------------------------------------
    def economy_settings(self) -> dict[str, float]:
        return {str(key): float(value) for key, value in self.config.economy.items()}

    def active_price_spikes(self) -> dict[str, dict[str, object]]:
        return {
            event_id: {
                "magnitude": float(event.magnitude),
                "targets": [str(target) for target in event.targets],
            }
            for event_id, event in self._price_spike_events.items()
        }

    def utility_snapshot(self) -> dict[str, bool]:
        return {str(key): bool(value) for key, value in self._utility_status.items()}

    def utility_online(self, utility: str) -> bool:
        return self._utility_status.get(utility.lower(), True)

    def basket_cost_for_agent(self, agent_id: str) -> float:
        return float(self._agent_basket_costs.get(str(agent_id), 0.0))

    def basket_cost_snapshot(self) -> dict[str, float]:
        return {str(agent_id): float(cost) for agent_id, cost in self._agent_basket_costs.items()}


__all__ = ["EconomyService"]

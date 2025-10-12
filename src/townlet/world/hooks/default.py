"""Built-in affordance hook handlers routed through modular services."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Mapping

from townlet.world.affordances.core import AffordanceEnvironment, HookPayload
from townlet.world.agents.snapshot import AgentSnapshot

if TYPE_CHECKING:  # pragma: no cover - type hint guard
    from townlet.world.grid import WorldState

_AFFORDANCE_FAIL_EVENT = "affordance_fail"
_SHOWER_COMPLETE_EVENT = "shower_complete"
_SHOWER_POWER_EVENT = "shower_power_outage"
_SHOWER_SESSION_KEY = "shower_sessions"
_SLEEP_COMPLETE_EVENT = "sleep_complete"


def register_hooks(world: WorldState) -> None:
    """Register built-in affordance hooks with the provided world."""

    world.register_affordance_hook("on_attempt_shower", _on_attempt_shower)
    world.register_affordance_hook("on_finish_shower", _on_finish_shower)
    world.register_affordance_hook("on_no_power", _on_no_power)
    world.register_affordance_hook("on_attempt_eat", _on_attempt_eat)
    world.register_affordance_hook("on_finish_eat", _on_finish_eat)
    world.register_affordance_hook("on_attempt_cook", _on_attempt_cook)
    world.register_affordance_hook("on_finish_cook", _on_finish_cook)
    world.register_affordance_hook("on_cook_fail", _on_cook_fail)
    world.register_affordance_hook("on_attempt_sleep", _on_attempt_sleep)
    world.register_affordance_hook("on_finish_sleep", _on_finish_sleep)


# ---------------------------------------------------------------------------
# Hook helpers
# ---------------------------------------------------------------------------

def _env(payload: HookPayload) -> AffordanceEnvironment:
    return payload["environment"]


def _lookup_agent(environment: AffordanceEnvironment, agent_id: str) -> AgentSnapshot | None:
    values = environment.agents.values_map()
    return values.get(agent_id)


def _lookup_object(environment: AffordanceEnvironment, object_id: str) -> Any | None:
    return environment.objects.get(object_id)


def _store_stock(environment: AffordanceEnvironment, object_id: str, stock: Mapping[str, Any]) -> None:
    environment.store_stock[object_id] = stock if isinstance(stock, dict) else dict(stock)


def _tick(environment: AffordanceEnvironment) -> int:
    return int(environment.tick_supplier())


def _set_cancel(payload: HookPayload) -> None:
    payload["cancel"] = True


def _abort_affordance(payload: HookPayload, *, reason: str) -> None:
    environment = _env(payload)
    spec = payload.get("spec")
    agent_id = payload.get("agent_id")
    object_id = payload.get("object_id")
    if agent_id is None or object_id is None:
        return

    environment.running_affordances.pop(object_id, None)
    obj = _lookup_object(environment, object_id)
    if obj is not None and getattr(obj, "occupied_by", None) == agent_id:
        obj.occupied_by = None

    environment.queue_manager.release(object_id, agent_id, _tick(environment), success=False)
    environment.sync_reservation(object_id)

    payload_event: dict[str, Any] = {
        "agent_id": agent_id,
        "object_id": object_id,
        "reason": reason,
    }
    hook_names: Iterable[str] = ()
    if spec is not None:
        payload_event["affordance_id"] = getattr(spec, "affordance_id", None)
        hook_names = getattr(spec, "hooks", {}).get("fail", ())
        if getattr(spec, "affordance_id", None) == "rest_sleep" and obj is not None:
            capacity = obj.stock.get("sleep_capacity", obj.stock.get("sleep_slots", 0))
            obj.stock["sleep_slots"] = min(capacity, obj.stock.get("sleep_slots", 0) + 1)
            _store_stock(environment, object_id, obj.stock)

    environment.emit_event(_AFFORDANCE_FAIL_EVENT, payload_event)
    if hook_names:
        environment.dispatch_hooks(
            "fail",
            hook_names,
            agent_id=agent_id,
            object_id=object_id,
            spec=spec,
            extra={"reason": reason},
        )


# ---------------------------------------------------------------------------
# Hook implementations
# ---------------------------------------------------------------------------

def _on_attempt_shower(payload: HookPayload) -> None:
    environment = _env(payload)
    object_id = payload["object_id"]
    agent_id = payload["agent_id"]

    obj = _lookup_object(environment, object_id)
    if obj is None:
        _set_cancel(payload)
        return

    power_on = bool(obj.stock.get("power_on", 1))
    if not power_on:
        _abort_affordance(payload, reason="power_off")
        obj.stock["power_on"] = 0
        _store_stock(environment, object_id, obj.stock)
        _set_cancel(payload)
        return

    obj.stock[_SHOWER_SESSION_KEY] = obj.stock.get(_SHOWER_SESSION_KEY, 0) + 1
    _store_stock(environment, object_id, obj.stock)

    snapshot = _lookup_agent(environment, agent_id)
    if snapshot is not None:
        snapshot.inventory["showers_started"] = snapshot.inventory.get("showers_started", 0) + 1


def _on_finish_shower(payload: HookPayload) -> None:
    environment = _env(payload)
    agent_id = payload["agent_id"]
    object_id = payload["object_id"]

    snapshot = _lookup_agent(environment, agent_id)
    if snapshot is not None:
        snapshot.inventory["showers_taken"] = snapshot.inventory.get("showers_taken", 0) + 1

    environment.emit_event(
        _SHOWER_COMPLETE_EVENT,
        {
            "agent_id": agent_id,
            "object_id": object_id,
        },
    )


def _on_no_power(payload: HookPayload) -> None:
    environment = _env(payload)
    object_id = payload["object_id"]

    obj = _lookup_object(environment, object_id)
    if obj is None:
        return

    obj.stock["power_on"] = 0
    _store_stock(environment, object_id, obj.stock)
    environment.emit_event(
        _SHOWER_POWER_EVENT,
        {
            "object_id": object_id,
        },
    )


def _on_attempt_eat(payload: HookPayload) -> None:
    environment = _env(payload)
    agent_id = payload["agent_id"]
    object_id = payload["object_id"]

    snapshot = _lookup_agent(environment, agent_id)
    obj = _lookup_object(environment, object_id)
    if snapshot is None or obj is None:
        _set_cancel(payload)
        return

    meal_cost = float(environment.config.economy.get("meal_cost", 0.4))
    stock = obj.stock.get("meals", 0)
    if stock <= 0:
        _abort_affordance(payload, reason="insufficient_stock")
        _set_cancel(payload)
        return
    if snapshot.wallet < meal_cost:
        _abort_affordance(payload, reason="insufficient_funds")
        _set_cancel(payload)
        return

    obj.stock["meals"] = stock - 1
    _store_stock(environment, object_id, obj.stock)
    snapshot.wallet -= meal_cost
    snapshot.inventory["meals_consumed"] = snapshot.inventory.get("meals_consumed", 0) + 1

    participants_record = environment.recent_meal_participants.get(object_id)
    current_tick = _tick(environment)
    if participants_record and participants_record.get("tick") == current_tick:
        participants: set[str] = participants_record["agents"]
    else:
        participants = set()
        environment.recent_meal_participants[object_id] = {
            "tick": current_tick,
            "agents": participants,
        }
    participants.add(agent_id)


def _on_finish_eat(payload: HookPayload) -> None:
    environment = _env(payload)
    agent_id = payload["agent_id"]
    object_id = payload["object_id"]

    record = environment.recent_meal_participants.get(object_id)
    if not record:
        return

    participants: set[str] = record.get("agents", set())
    participants.add(agent_id)
    for other_id in participants:
        if other_id == agent_id:
            continue
        environment.relationships.update_relationship(
            agent_id,
            other_id,
            trust=0.1,
            familiarity=0.25,
            event="shared_meal",
        )

    environment.emit_event(
        "shared_meal",
        {
            "agents": sorted(participants),
            "object_id": object_id,
        },
    )


def _on_attempt_cook(payload: HookPayload) -> None:
    environment = _env(payload)
    agent_id = payload["agent_id"]
    object_id = payload["object_id"]

    snapshot = _lookup_agent(environment, agent_id)
    obj = _lookup_object(environment, object_id)
    if snapshot is None or obj is None:
        _set_cancel(payload)
        return

    cost = float(environment.config.economy.get("ingredients_cost", 0.15))
    if snapshot.wallet < cost:
        _abort_affordance(payload, reason="insufficient_funds")
        _set_cancel(payload)
        return

    snapshot.wallet -= cost
    obj.stock["raw_ingredients"] = obj.stock.get("raw_ingredients", 0) - 1
    if obj.stock["raw_ingredients"] < 0:
        obj.stock["raw_ingredients"] = 0
        _abort_affordance(payload, reason="no_ingredients")
        _set_cancel(payload)
        return

    _store_stock(environment, object_id, obj.stock)


def _on_finish_cook(payload: HookPayload) -> None:
    environment = _env(payload)
    agent_id = payload["agent_id"]
    object_id = payload["object_id"]

    snapshot = _lookup_agent(environment, agent_id)
    obj = _lookup_object(environment, object_id)
    if snapshot is None or obj is None:
        return

    obj.stock["meals"] = obj.stock.get("meals", 0) + 1
    _store_stock(environment, object_id, obj.stock)
    snapshot.inventory["meals_cooked"] = snapshot.inventory.get("meals_cooked", 0) + 1


def _on_cook_fail(payload: HookPayload) -> None:
    environment = _env(payload)
    object_id = payload["object_id"]
    obj = _lookup_object(environment, object_id)
    if obj is None:
        return
    obj.stock.setdefault("raw_ingredients", 0)
    _store_stock(environment, object_id, obj.stock)


def _on_attempt_sleep(payload: HookPayload) -> None:
    environment = _env(payload)
    agent_id = payload["agent_id"]
    object_id = payload["object_id"]

    obj = _lookup_object(environment, object_id)
    if obj is None:
        _set_cancel(payload)
        return

    capacity = obj.stock.get("sleep_capacity")
    if capacity is None:
        capacity = obj.stock.get("sleep_slots", 1)
        obj.stock["sleep_capacity"] = capacity

    available = obj.stock.get("sleep_slots", capacity)
    if available <= 0:
        _abort_affordance(payload, reason="bed_unavailable")
        _set_cancel(payload)
        return

    obj.stock["sleep_slots"] = available - 1
    _store_stock(environment, object_id, obj.stock)

    snapshot = _lookup_agent(environment, agent_id)
    if snapshot is not None:
        snapshot.inventory["sleep_attempts"] = snapshot.inventory.get("sleep_attempts", 0) + 1


def _on_finish_sleep(payload: HookPayload) -> None:
    environment = _env(payload)
    agent_id = payload["agent_id"]
    object_id = payload["object_id"]

    obj = _lookup_object(environment, object_id)
    if obj is not None:
        capacity = obj.stock.get("sleep_capacity", obj.stock.get("sleep_slots", 0) + 1)
        obj.stock["sleep_slots"] = min(capacity, obj.stock.get("sleep_slots", 0) + 1)
        _store_stock(environment, object_id, obj.stock)

    snapshot = _lookup_agent(environment, agent_id)
    if snapshot is not None:
        snapshot.inventory["sleep_sessions"] = snapshot.inventory.get("sleep_sessions", 0) + 1

    environment.emit_event(
        _SLEEP_COMPLETE_EVENT,
        {
            "agent_id": agent_id,
            "object_id": object_id,
        },
    )

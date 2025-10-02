"""Built-in affordance hook handlers."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - type hint guard
    from townlet.world.grid import WorldState

_AFFORDANCE_FAIL_EVENT = "affordance_fail"
_SHOWER_COMPLETE_EVENT = "shower_complete"
_SHOWER_POWER_EVENT = "shower_power_outage"
_SLEEP_COMPLETE_EVENT = "sleep_complete"


def register_hooks(world: "WorldState") -> None:
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


def _on_attempt_shower(context: dict[str, Any]) -> None:
    world = context["world"]
    object_id = context["object_id"]
    agent_id = context["agent_id"]
    spec = context["spec"]

    obj = world.objects.get(object_id)
    if obj is None:
        context["cancel"] = True
        return

    power_on = bool(obj.stock.get("power_on", 1))
    if not power_on:
        _abort_affordance(world, spec, agent_id, object_id, "power_off")
        obj.stock["power_on"] = 0
        world.store_stock[object_id] = obj.stock
        context["cancel"] = True
        return

    obj.stock.setdefault("shower_sessions", 0)
    obj.stock["shower_sessions"] += 1
    world.store_stock[object_id] = obj.stock

    snapshot = world.agents.get(agent_id)
    if snapshot is not None:
        snapshot.inventory["showers_started"] = (
            snapshot.inventory.get("showers_started", 0) + 1
        )


def _on_finish_shower(context: dict[str, Any]) -> None:
    world = context["world"]
    agent_id = context["agent_id"]
    object_id = context["object_id"]

    snapshot = world.agents.get(agent_id)
    if snapshot is not None:
        snapshot.inventory["showers_taken"] = (
            snapshot.inventory.get("showers_taken", 0) + 1
        )
    world._emit_event(  # pylint: disable=protected-access
        _SHOWER_COMPLETE_EVENT,
        {
            "agent_id": agent_id,
            "object_id": object_id,
        },
    )


def _on_no_power(context: dict[str, Any]) -> None:
    world = context["world"]
    object_id = context["object_id"]
    obj = world.objects.get(object_id)
    if obj is None:
        return
    obj.stock["power_on"] = 0
    world.store_stock[object_id] = obj.stock
    world._emit_event(  # pylint: disable=protected-access
        _SHOWER_POWER_EVENT,
        {
            "object_id": object_id,
        },
    )


def _on_attempt_eat(context: dict[str, Any]) -> None:
    world = context["world"]
    agent_id = context["agent_id"]
    object_id = context["object_id"]
    spec = context["spec"]

    snapshot = world.agents.get(agent_id)
    obj = world.objects.get(object_id)
    if snapshot is None or obj is None:
        context["cancel"] = True
        return

    meal_cost = world.config.economy.get("meal_cost", 0.4)
    stock = obj.stock.get("meals", 0)
    if stock <= 0:
        _abort_affordance(world, spec, agent_id, object_id, "insufficient_stock")
        context["cancel"] = True
        return
    if snapshot.wallet < meal_cost:
        _abort_affordance(world, spec, agent_id, object_id, "insufficient_funds")
        context["cancel"] = True
        return

    obj.stock["meals"] = stock - 1
    world.store_stock[object_id] = obj.stock
    snapshot.wallet -= meal_cost
    snapshot.inventory["meals_consumed"] = snapshot.inventory.get("meals_consumed", 0) + 1

    record = world._recent_meal_participants.get(object_id)  # pylint: disable=protected-access
    if record and record.get("tick") == world.tick:
        participants = record["agents"]
    else:
        participants = set()
        world._recent_meal_participants[object_id] = {  # pylint: disable=protected-access
            "tick": world.tick,
            "agents": participants,
        }
    participants.add(agent_id)


def _on_finish_eat(context: dict[str, Any]) -> None:
    world = context["world"]
    agent_id = context["agent_id"]
    object_id = context["object_id"]

    record = world._recent_meal_participants.get(object_id)  # pylint: disable=protected-access
    if not record:
        return
    participants: set[str] = record.get("agents", set())
    participants.add(agent_id)
    for other_id in participants:
        if other_id == agent_id:
            continue
        world.update_relationship(
            agent_id,
            other_id,
            trust=0.1,
            familiarity=0.25,
            event="shared_meal",
        )
    world._emit_event(  # pylint: disable=protected-access
        "shared_meal",
        {
            "agents": sorted(participants),
            "object_id": object_id,
        },
    )


def _on_attempt_cook(context: dict[str, Any]) -> None:
    world = context["world"]
    agent_id = context["agent_id"]
    object_id = context["object_id"]
    spec = context["spec"]

    snapshot = world.agents.get(agent_id)
    obj = world.objects.get(object_id)
    if snapshot is None or obj is None:
        context["cancel"] = True
        return

    cost = world.config.economy.get("ingredients_cost", 0.15)
    if snapshot.wallet < cost:
        _abort_affordance(world, spec, agent_id, object_id, "insufficient_funds")
        context["cancel"] = True
        return

    snapshot.wallet -= cost
    obj.stock["raw_ingredients"] = obj.stock.get("raw_ingredients", 0) - 1
    if obj.stock["raw_ingredients"] < 0:
        obj.stock["raw_ingredients"] = 0
        _abort_affordance(world, spec, agent_id, object_id, "no_ingredients")
        context["cancel"] = True
        return
    world.store_stock[object_id] = obj.stock


def _on_finish_cook(context: dict[str, Any]) -> None:
    world = context["world"]
    agent_id = context["agent_id"]
    object_id = context["object_id"]

    snapshot = world.agents.get(agent_id)
    obj = world.objects.get(object_id)
    if snapshot is None or obj is None:
        return
    obj.stock["meals"] = obj.stock.get("meals", 0) + 1
    world.store_stock[object_id] = obj.stock
    snapshot.inventory["meals_cooked"] = snapshot.inventory.get("meals_cooked", 0) + 1


def _on_cook_fail(context: dict[str, Any]) -> None:
    world = context["world"]
    object_id = context["object_id"]
    obj = world.objects.get(object_id)
    if obj is None:
        return
    obj.stock.setdefault("raw_ingredients", 0)
    world.store_stock[object_id] = obj.stock


def _on_attempt_sleep(context: dict[str, Any]) -> None:
    world = context["world"]
    agent_id = context["agent_id"]
    object_id = context["object_id"]
    spec = context["spec"]

    obj = world.objects.get(object_id)
    if obj is None:
        context["cancel"] = True
        return

    capacity = obj.stock.get("sleep_capacity")
    if capacity is None:
        capacity = obj.stock.get("sleep_slots", 1)
        obj.stock["sleep_capacity"] = capacity

    available = obj.stock.get("sleep_slots", capacity)
    if available <= 0:
        _abort_affordance(world, spec, agent_id, object_id, "bed_unavailable")
        context["cancel"] = True
        return

    obj.stock["sleep_slots"] = available - 1
    world.store_stock[object_id] = obj.stock

    snapshot = world.agents.get(agent_id)
    if snapshot is not None:
        snapshot.inventory["sleep_attempts"] = (
            snapshot.inventory.get("sleep_attempts", 0) + 1
        )


def _on_finish_sleep(context: dict[str, Any]) -> None:
    world = context["world"]
    agent_id = context["agent_id"]
    object_id = context["object_id"]

    obj = world.objects.get(object_id)
    if obj is not None:
        capacity = obj.stock.get("sleep_capacity", obj.stock.get("sleep_slots", 0) + 1)
        obj.stock["sleep_slots"] = min(
            capacity,
            obj.stock.get("sleep_slots", 0) + 1,
        )
        world.store_stock[object_id] = obj.stock

    snapshot = world.agents.get(agent_id)
    if snapshot is not None:
        snapshot.inventory["sleep_sessions"] = (
            snapshot.inventory.get("sleep_sessions", 0) + 1
        )
    world._emit_event(  # pylint: disable=protected-access
        _SLEEP_COMPLETE_EVENT,
        {
            "agent_id": agent_id,
            "object_id": object_id,
        },
    )


def _abort_affordance(
    world: "WorldState",
    spec: Any,
    agent_id: str,
    object_id: str,
    reason: str,
) -> None:
    world.affordance_runtime.running_affordances.pop(object_id, None)
    obj = world.objects.get(object_id)
    if obj is not None and obj.occupied_by == agent_id:
        obj.occupied_by = None
    world.queue_manager.release(object_id, agent_id, world.tick, success=False)
    world._sync_reservation(object_id)  # pylint: disable=protected-access
    payload = {
        "agent_id": agent_id,
        "object_id": object_id,
        "affordance_id": spec.affordance_id,
        "reason": reason,
    }
    if spec.affordance_id == "rest_sleep":
        obj = world.objects.get(object_id)
        if obj is not None:
            capacity = obj.stock.get("sleep_capacity", obj.stock.get("sleep_slots", 0))
            obj.stock["sleep_slots"] = min(
                capacity,
                obj.stock.get("sleep_slots", 0) + 1,
            )
            world.store_stock[object_id] = obj.stock
    world._emit_event(_AFFORDANCE_FAIL_EVENT, payload)  # pylint: disable=protected-access
    world._dispatch_affordance_hooks(  # pylint: disable=protected-access
        "fail",
        spec.hooks.get("fail", ()),
        agent_id=agent_id,
        object_id=object_id,
        spec=spec,
        extra={"reason": reason},
    )

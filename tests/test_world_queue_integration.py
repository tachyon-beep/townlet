from pathlib import Path

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world.grid import AgentSnapshot, WorldState


def _make_world() -> WorldState:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.register_object("shower", "shower")
    world.register_object("fridge_1", "fridge")
    world.register_object("stove_1", "stove")
    world.register_object("bed_1", "bed")
    # Update the loaded affordance to known duration/effects for deterministic tests
    world.register_affordance(
        affordance_id="use_shower",
        object_type="shower",
        duration=2,
        effects={"hygiene": 0.2, "money": -0.1},
    )
    world.agents["alice"] = AgentSnapshot(
        "alice", (0, 0), {"hunger": 0.5, "hygiene": 0.3}, wallet=1.0
    )
    world.agents["bob"] = AgentSnapshot(
        "bob", (1, 0), {"hunger": 0.6, "hygiene": 0.4}, wallet=1.0
    )
    return world


def test_queue_assignment_flow() -> None:
    world = _make_world()
    world.tick = 0
    world.apply_actions(
        {
            "alice": {"kind": "request", "object": "shower"},
            "bob": {"kind": "request", "object": "shower"},
        }
    )
    world.resolve_affordances(current_tick=world.tick)

    assert world.queue_manager.active_agent("shower") == "alice"
    assert world.active_reservations.get("shower") == "alice"

    world.tick = 1
    world.apply_actions({"alice": {"kind": "release", "object": "shower"}})
    assert world.queue_manager.active_agent("shower") == "bob"
    assert world.active_reservations.get("shower") == "bob"


def test_queue_ghost_step_promotes_waiter() -> None:
    world = _make_world()
    world.queue_manager._settings.ghost_step_after = 1  # expedite test
    world.tick = 0
    world.apply_actions(
        {
            "alice": {"kind": "request", "object": "shower"},
            "bob": {"kind": "request", "object": "shower"},
        }
    )
    world.resolve_affordances(current_tick=world.tick)

    for tick in range(1, 3):
        world.tick = tick
        world.resolve_affordances(current_tick=world.tick)

    assert world.queue_manager.active_agent("shower") == "bob"
    assert world.active_reservations.get("shower") == "bob"
    assert world.queue_manager.metrics()["ghost_step_events"] >= 1


def test_affordance_completion_applies_effects() -> None:
    world = _make_world()
    world.tick = 0
    world.apply_actions({"alice": {"kind": "request", "object": "shower"}})
    world.resolve_affordances(current_tick=world.tick)

    world.apply_actions(
        {
            "alice": {
                "kind": "start",
                "object": "shower",
                "affordance": "use_shower",
            }
        }
    )

    for t in range(1, 3):
        world.tick = t
        world.resolve_affordances(current_tick=world.tick)

    alice = world.agents["alice"]
    assert alice.needs["hygiene"] > 0.3
    assert alice.wallet < 1.0
    assert world.queue_manager.active_agent("shower") is None


def test_affordances_loaded_from_yaml() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    assert "use_shower" in world.affordances
    spec = world.affordances["use_shower"]
    assert spec.object_type == "shower"


def test_affordance_events_emitted() -> None:
    world = _make_world()
    world.tick = 0
    world.apply_actions({"alice": {"kind": "request", "object": "shower"}})
    world.resolve_affordances(current_tick=world.tick)

    world.apply_actions(
        {
            "alice": {
                "kind": "start",
                "object": "shower",
                "affordance": "use_shower",
            }
        }
    )

    events = world.drain_events()
    assert any(e["event"] == "affordance_start" for e in events)

    for t in range(1, 3):
        world.tick = t
        world.resolve_affordances(current_tick=world.tick)

    events = world.drain_events()
    assert any(e["event"] == "affordance_finish" for e in events)


def test_need_decay_applied_each_tick() -> None:
    world = _make_world()
    world.agents["alice"].needs["hunger"] = 1.0
    initial = world.agents["alice"].needs["hunger"]
    world.tick = 0
    world.resolve_affordances(current_tick=world.tick)
    world.tick = 1
    world.resolve_affordances(current_tick=world.tick)
    assert world.agents["alice"].needs["hunger"] < initial


def test_eat_meal_deducts_wallet_and_stock() -> None:
    world = _make_world()
    world.tick = 0
    world.apply_actions({"alice": {"kind": "request", "object": "fridge_1"}})
    world.resolve_affordances(current_tick=world.tick)
    initial_wallet = world.agents["alice"].wallet
    initial_stock = world.store_stock.get("fridge_1", {}).get("meals", 0)

    world.apply_actions(
        {
            "alice": {
                "kind": "start",
                "object": "fridge_1",
                "affordance": "eat_meal",
            }
        }
    )

    world.tick = 1
    world.resolve_affordances(current_tick=world.tick)
    world.tick = 2
    world.resolve_affordances(current_tick=world.tick)

    assert world.agents["alice"].wallet < initial_wallet
    assert world.store_stock["fridge_1"]["meals"] == initial_stock - 1


def test_wage_income_applied_on_shift() -> None:
    world = _make_world()
    alice = world.agents["alice"]
    alice.position = (0, 0)
    initial_wallet = alice.wallet
    world.tick = 200
    world.resolve_affordances(current_tick=world.tick)
    assert alice.on_shift is True
    assert alice.wallet > initial_wallet

    # Advance beyond shift end
    world.tick = 401
    world.resolve_affordances(current_tick=world.tick)
    assert alice.on_shift is False


def test_stove_restock_event_emitted() -> None:
    world = _make_world()
    world.tick = 199
    world.resolve_affordances(current_tick=world.tick)
    world.tick = 200
    world.resolve_affordances(current_tick=world.tick)
    events = world.drain_events()
    assert any(event.get("event") == "stock_replenish" for event in events)
def test_scripted_behavior_handles_sleep() -> None:
    world = _make_world()
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.world = world
    world.agents["alice"].needs["energy"] = 0.1

    for _ in range(120):
        loop.step()

    assert world.agents["alice"].needs["energy"] > 0.1

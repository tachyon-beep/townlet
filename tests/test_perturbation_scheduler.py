from pathlib import Path

import pytest

from townlet.config import (
    ArrangedMeetEventConfig,
    BlackoutEventConfig,
    FloatRange,
    IntRange,
    PerturbationSchedulerConfig,
    PriceSpikeEventConfig,
    SimulationConfig,
    load_config,
)
from townlet.scheduler.perturbations import PerturbationScheduler
from townlet.world.grid import WorldState


def _base_config() -> SimulationConfig:
    config_path = Path("configs/examples/poc_hybrid.yaml")
    if not config_path.exists():
        raise RuntimeError("example config not found")
    config = load_config(config_path)
    config.perturbations = PerturbationSchedulerConfig(
        max_concurrent_events=2,
        global_cooldown_ticks=0,
        per_agent_cooldown_ticks=0,
        grace_window_ticks=0,
        window_ticks=10,
        max_events_per_window=10,
        events={
            "price_spike": PriceSpikeEventConfig(
                probability_per_day=1.0,
                cooldown_ticks=0,
                duration=IntRange(min=1, max=1),
                magnitude=FloatRange(min=1.5, max=1.5),
                targets=["market"],
            ),
            "arranged_meet": ArrangedMeetEventConfig(
                probability_per_day=0.0,
                cooldown_ticks=0,
                duration=IntRange(min=1, max=1),
                max_participants=2,
            ),
            "blackout": BlackoutEventConfig(
                probability_per_day=0.0,
                cooldown_ticks=0,
                duration=IntRange(min=2, max=2),
            ),
        },
    )
    config.observations_config.hybrid.time_ticks_per_day = 1
    return config


def test_manual_event_activation_and_expiry() -> None:
    config = _base_config()
    config.perturbations.events["price_spike"].probability_per_day = 0.0
    scheduler = PerturbationScheduler(config)
    world = WorldState.from_config(config)
    base_meal_cost = world.config.economy.get("meal_cost", 0.0)
    event = scheduler.schedule_manual(
        world,
        spec_name="price_spike",
        current_tick=0,
        payload_overrides={"magnitude": 1.2},
    )

    scheduler.tick(world, 0)
    tick_events = world.drain_events()
    assert world.config.economy.get("meal_cost") == pytest.approx(base_meal_cost * 1.2)
    assert any(e.get("event") == "perturbation_price_spike" for e in tick_events)
    assert event.event_id in scheduler.active

    scheduler.tick(world, event.ends_at)
    end_events = world.drain_events()
    assert any(e.get("event") == "perturbation_ended" for e in end_events)
    assert event.event_id not in scheduler.active
    scheduler.tick(world, event.ends_at + 1)
    world.drain_events()
    assert world.config.economy.get("meal_cost") == pytest.approx(base_meal_cost)

    exported = scheduler.export_state()
    restored = PerturbationScheduler(config)
    restored.import_state(exported)
    assert restored.active == scheduler.active


def test_auto_scheduling_respects_cooldowns() -> None:
    config = _base_config()
    config.perturbations.events["price_spike"].cooldown_ticks = 2
    scheduler = PerturbationScheduler(config)
    scheduler.seed(123)
    world = WorldState.from_config(config)

    scheduler.tick(world, 0)
    first_events = world.drain_events()
    assert any(e.get("event") == "perturbation_price_spike" for e in first_events)

    scheduler.tick(world, 1)
    assert not any(
        e.get("event") == "perturbation_price_spike" for e in world.drain_events()
    )

    scheduler.tick(world, 4)
    later_events = world.drain_events()
    assert any(e.get("event") == "perturbation_price_spike" for e in later_events)


def test_cancel_event_removes_from_active() -> None:
    config = _base_config()
    scheduler = PerturbationScheduler(config)
    world = WorldState.from_config(config)
    event = scheduler.schedule_manual(world, "price_spike", 0)
    scheduler.tick(world, 0)
    world.drain_events()
    assert event.event_id in scheduler.active
    cancelled = scheduler.cancel_event(world, event.event_id)
    assert cancelled is True
    assert event.event_id not in scheduler.active


def test_blackout_toggles_power_status() -> None:
    config = _base_config()
    scheduler = PerturbationScheduler(config)
    world = WorldState.from_config(config)
    world.register_object(object_id="stove#1", object_type="stove", position=(0, 0))
    stoves = [obj for obj in world.objects.values() if obj.object_type == "stove"]
    assert stoves, "expected stove objects for blackout test"

    event = scheduler.schedule_manual(
        world,
        spec_name="blackout",
        current_tick=0,
        duration=2,
        payload_overrides={"utility": "power"},
    )

    scheduler.tick(world, 0)
    world.drain_events()
    assert world.utility_online("power") is False
    assert all(obj.stock.get("power_on", 1.0) == 0.0 for obj in stoves)

    scheduler.tick(world, event.ends_at)
    world.drain_events()
    scheduler.tick(world, event.ends_at + 1)
    world.drain_events()
    assert world.utility_online("power") is True
    assert all(obj.stock.get("power_on", 0.0) == 1.0 for obj in stoves)


def test_arranged_meet_relocates_agents() -> None:
    config = _base_config()
    scheduler = PerturbationScheduler(config)
    world = WorldState.from_config(config)

    world.respawn_agent({"agent_id": "alice", "position": [0, 0]})
    world.respawn_agent({"agent_id": "bob", "position": [1, 0]})
    world.register_object(object_id="meet_square", object_type="plaza", position=(5, 5))
    meet_location = None
    for candidate in world.objects.values():
        if candidate.position is not None:
            meet_location = candidate
            break
    assert meet_location is not None, "expected object with position for arranged meet"

    scheduler.schedule_manual(
        world,
        spec_name="arranged_meet",
        current_tick=0,
        targets=["alice", "bob"],
        payload_overrides={"location": meet_location.object_id},
    )

    scheduler.tick(world, 0)
    world.drain_events()
    pos = (int(meet_location.position[0]), int(meet_location.position[1]))  # type: ignore[index]
    assert world.agents["alice"].position == pos
    assert world.agents["bob"].position == pos

from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config.loader import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world.grid import AgentSnapshot


@pytest.fixture()
def loop_with_world() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    try:
        yield loop
    finally:
        loop.close()


def _register_agent(world, agent_id: str, position: tuple[int, int]) -> None:
    world.agents[agent_id] = AgentSnapshot(
        agent_id=agent_id,
        position=position,
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )


def test_world_context_queue_and_relationship_exports(loop_with_world: SimulationLoop) -> None:
    loop = loop_with_world
    world = loop.world
    context = loop.world_context

    world.register_object(object_id="stove_1", object_type="stove")
    _register_agent(world, "alice", (0, 0))
    _register_agent(world, "bob", (1, 0))

    # Configure ghost-step to trigger quickly and simulate queue pressure.
    world.queue_manager._settings.ghost_step_after = 1
    world.queue_manager.request_access("stove_1", "alice", tick=0)
    world.queue_manager.request_access("stove_1", "bob", tick=1)
    world.queue_manager.record_blocked_attempt("stove_1")
    world.queue_manager.record_blocked_attempt("stove_1")
    world.queue_manager.requeue_to_tail("stove_1", "bob", tick=2)
    world.queue_manager.promote_agent("stove_1", "bob")

    assert context.export_queue_metrics() == world.queue_manager.metrics()
    assert context.export_queue_affinity_metrics() == world.queue_manager.performance_metrics()
    assert context.export_queue_state() == world.queue_manager.export_state()

    # Apply rivalry/conflict updates and compare relationship snapshots.
    relationships = context.relationships
    relationships.set_relationship("alice", "bob", trust=0.2, familiarity=0.1, rivalry=0.0)
    relationships.apply_rivalry_conflict("alice", "bob", intensity=0.6)

    assert context.export_relationship_snapshot() == world.relationships_snapshot()
    assert context.export_relationship_metrics() == world.relationship_metrics_snapshot()


def test_world_context_economy_exports(loop_with_world: SimulationLoop) -> None:
    loop = loop_with_world
    world = loop.world
    context = loop.world_context

    # Apply a price spike and utility outage via the economy/perturbation services.
    context.economy_service.apply_price_spike("spike-1", magnitude=1.25, targets=["stove_1"])
    context.economy_service.apply_utility_outage("outage-1", utility="power")

    economy_snapshot = context.export_economy_snapshot()
    assert economy_snapshot["active_price_spikes"] == world.active_price_spikes()
    assert economy_snapshot["utility_snapshot"] == world.utility_snapshot()

    # Clear and ensure export reflects update.
    context.economy_service.clear_price_spike("spike-1")
    context.economy_service.clear_utility_outage("outage-1", utility="power")

    cleared_snapshot = context.export_economy_snapshot()
    assert cleared_snapshot["active_price_spikes"] == world.active_price_spikes()
    assert cleared_snapshot["utility_snapshot"] == world.utility_snapshot()

from __future__ import annotations

from pathlib import Path

from townlet.agents.models import PersonalityProfiles
from townlet.config import load_config
from townlet.world.affordances.core import AffordanceEnvironment, AffordanceRuntimeContext
from townlet.world.agents.registry import AgentRegistry
from townlet.world.agents.relationships_service import RelationshipService
from townlet.world.agents.snapshot import AgentSnapshot
from townlet.world.queue import QueueManager


def test_agent_registry_invokes_callbacks() -> None:
    added: list[str] = []
    removed: list[str] = []

    registry = AgentRegistry()
    registry.configure_callbacks(
        on_add=lambda snapshot: added.append(snapshot.agent_id),
        on_remove=lambda snapshot: removed.append(snapshot.agent_id),
    )

    alice = AgentSnapshot(agent_id="alice", position=(0, 0), needs={"hunger": 0.5})
    registry.add(alice)
    assert "alice" in added

    registry.discard("alice")
    assert "alice" in removed


def test_relationship_service_set_relationship_pins_values(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    current_tick = {"value": 0}

    def tick_supplier() -> int:
        return current_tick["value"]

    service = RelationshipService(
        config,
        tick_supplier=tick_supplier,
        personality_resolver=lambda _: PersonalityProfiles.get("balanced"),
    )

    service.set_relationship("alice", "bob", trust=0.4, familiarity=0.2, rivalry=0.1)
    tie = service.relationship_tie("alice", "bob")
    assert tie is not None and tie.trust == 0.4

    service.decay()
    tie_after_decay = service.relationship_tie("alice", "bob")
    assert tie_after_decay is not None and tie_after_decay.trust == tie.trust

    current_tick["value"] = 1
    service.decay()
    tie_future = service.relationship_tie("alice", "bob")
    assert tie_future is not None
    assert tie_future.trust <= tie.trust


def test_affordance_runtime_context_delegates_environment() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    queue_manager = QueueManager(config=config)
    environment = AffordanceEnvironment(
        queue_manager=queue_manager,
        agents=AgentRegistry(),
        relationships=RelationshipService(
            config,
            tick_supplier=lambda: 0,
            personality_resolver=lambda _: PersonalityProfiles.get("balanced"),
        ),
        objects={},
        affordances={},
        running_affordances={},
        active_reservations={},
        emit_event=lambda *_, **__: None,
        sync_reservation=lambda *_: None,
        apply_affordance_effects=lambda *_: None,
        dispatch_hooks=lambda *_, **__: True,
        record_queue_conflict=lambda *_, **__: None,
        apply_need_decay=lambda: None,
        build_precondition_context=lambda **_: {},
        snapshot_precondition_context=lambda _: {},
        tick_supplier=lambda: 42,
        store_stock={},
        recent_meal_participants={},
        config=config,
        world_ref="sentinel",
    )
    context = AffordanceRuntimeContext(environment=environment)

    assert context.queue_manager is queue_manager
    assert context.world == "sentinel"
    assert context.dispatch_hooks("before", ()) is True

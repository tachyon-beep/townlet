from __future__ import annotations

from townlet.world.agents.snapshot import AgentSnapshot
from townlet.world.grid import InteractiveObject
from townlet.world.spatial import WorldSpatialIndex


def make_agent(agent_id: str, x: int, y: int) -> tuple[str, AgentSnapshot]:
    snapshot = AgentSnapshot(
        agent_id=agent_id,
        position=(x, y),
        needs={},
    )
    return agent_id, snapshot


def test_rebuild_and_query() -> None:
    index = WorldSpatialIndex()
    agents = dict(
        [
            make_agent("alice", 0, 0),
            make_agent("bob", 1, 0),
        ]
    )
    objects = {
        "kiosk": InteractiveObject(object_id="kiosk", object_type="stall", position=(1, 0)),
    }
    reservations = {"kiosk": "alice"}

    index.rebuild(agents, objects, reservations)

    assert set(index.agents_at((0, 0))) == {"alice"}
    assert set(index.agents_at((1, 0))) == {"bob"}
    assert index.position_of("alice") == (0, 0)
    assert (1, 0) in index.reservation_tiles()


def test_move_and_remove_agent() -> None:
    index = WorldSpatialIndex()
    agents = dict([make_agent("charlie", 0, 0)])
    index.rebuild(agents, {}, {})

    index.move_agent("charlie", (2, 2))
    assert index.position_of("charlie") == (2, 2)
    assert index.agents_at((0, 0)) == ()
    assert index.agents_at((2, 2)) == ("charlie",)

    index.remove_agent("charlie")
    assert index.position_of("charlie") is None
    assert index.agents_at((2, 2)) == ()

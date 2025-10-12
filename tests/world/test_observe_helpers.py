from __future__ import annotations

from collections.abc import Iterable, Mapping

from townlet.world.observations.interfaces import WorldRuntimeAdapterProtocol
from townlet.world.observe import find_nearest_object_of_type, local_view


class FakeWorldAdapter(WorldRuntimeAdapterProtocol):
    def __init__(self) -> None:
        self._snapshots = {
            "alice": type("Snap", (), {"position": (0, 0), "on_shift": False})(),
            "bob": type("Snap", (), {"position": (1, 0), "on_shift": True})(),
        }
        self._objects = {
            "stall": type("Obj", (), {"object_type": "stall", "position": (2, 0), "occupied_by": None})(),
        }

    def agent_snapshots_view(self) -> Mapping[str, object]:
        return self._snapshots

    def agents_at_tile(self, position: tuple[int, int]) -> tuple[str, ...]:
        return tuple(agent for agent, snap in self._snapshots.items() if snap.position == position)

    @property
    def objects(self) -> Mapping[str, object]:
        return self._objects

    def objects_by_position_view(self) -> Mapping[tuple[int, int], tuple[str, ...]]:
        return {(2, 0): ("stall",)}

    def reservation_tiles(self) -> Iterable[tuple[int, int]]:
        return [(2, 0)]

def test_local_view_returns_expected_structure() -> None:
    adapter = FakeWorldAdapter()
    view = local_view(adapter, "alice", radius=1)

    assert view["center"] == (0, 0)
    assert view["radius"] == 1
    # Ensure bob appears in neighbouring tiles
    agent_ids = {agent["agent_id"] for agent in view["agents"]}
    assert "bob" in agent_ids


def test_find_nearest_object_of_type() -> None:
    adapter = FakeWorldAdapter()
    coords = find_nearest_object_of_type(adapter, "stall", origin=(0, 0))
    assert coords == (2, 0)

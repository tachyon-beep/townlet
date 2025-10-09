from __future__ import annotations

from typing import Any

from townlet.world.systems import relationships


class FakeRelationshipService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []

    def relationships_snapshot(self) -> dict[str, dict[str, dict[str, float]]]:
        self.calls.append(("relationships_snapshot", (), {}))
        return {"alice": {"bob": {"trust": 1.0}}}

    def relationship_metrics_snapshot(self) -> dict[str, object]:
        self.calls.append(("relationship_metrics_snapshot", (), {}))
        return {"metrics": 1}

    def load_relationship_metrics(self, payload: dict[str, object] | None) -> None:
        self.calls.append(("load_relationship_metrics", (payload,), {}))

    def load_relationship_snapshot(self, snapshot: dict[str, dict[str, dict[str, float]]]) -> None:
        self.calls.append(("load_relationship_snapshot", (snapshot,), {}))

    def update_relationship(self, *args, **kwargs) -> None:
        self.calls.append(("update_relationship", args, kwargs))

    def set_relationship(self, *args, **kwargs) -> None:
        self.calls.append(("set_relationship", args, kwargs))

    def relationship_tie(self, agent_id: str, other_id: str) -> dict[str, float]:
        self.calls.append(("relationship_tie", (agent_id, other_id), {}))
        return {"trust": 0.5}

    def get_relationship_ledger(self, agent_id: str):
        self.calls.append(("get_relationship_ledger", (agent_id,), {}))
        return "ledger"

    def rivalry_snapshot(self) -> dict[str, dict[str, float]]:
        self.calls.append(("rivalry_snapshot", (), {}))
        return {"alice": {"bob": 0.3}}

    def rivalry_value(self, agent_id: str, other_id: str) -> float:
        self.calls.append(("rivalry_value", (agent_id, other_id), {}))
        return 0.7

    def rivalry_should_avoid(self, agent_id: str, other_id: str) -> bool:
        self.calls.append(("rivalry_should_avoid", (agent_id, other_id), {}))
        return True

    def rivalry_top(self, agent_id: str, limit: int) -> list[tuple[str, float]]:
        self.calls.append(("rivalry_top", (agent_id, limit), {}))
        return [("bob", 0.9)]

    def apply_rivalry_conflict(self, agent_a: str, agent_b: str, *, intensity: float) -> None:
        self.calls.append(("apply_rivalry_conflict", (agent_a, agent_b, intensity), {}))

    def decay(self) -> None:
        self.calls.append(("decay", (), {}))

    def remove_agent(self, agent_id: str) -> None:
        self.calls.append(("remove_agent", (agent_id,), {}))


def test_relationship_snapshots_delegate() -> None:
    service = FakeRelationshipService()
    assert relationships.relationships_snapshot(service)["alice"]["bob"]["trust"] == 1.0
    assert relationships.relationship_metrics_snapshot(service) == {"metrics": 1}


def test_loaders_delegate() -> None:
    service = FakeRelationshipService()
    relationships.load_relationship_metrics(service, {"metrics": 1})
    relationships.load_relationship_snapshot(service, {"alice": {}})

    calls = [name for name, _, _ in service.calls[:2]]
    assert calls == ["load_relationship_metrics", "load_relationship_snapshot"]


def test_update_and_set_relationship_delegate() -> None:
    service = FakeRelationshipService()
    relationships.update_relationship(service, "alice", "bob", trust=0.1, event="chat")
    relationships.set_relationship(service, "alice", "bob", trust=0.2, familiarity=0.3, rivalry=0.1)

    names = [name for name, _, _ in service.calls[-2:]]
    assert names == ["update_relationship", "set_relationship"]


def test_rivalry_helpers_delegate() -> None:
    service = FakeRelationshipService()
    relationships.apply_rivalry_conflict(service, "alice", "bob", intensity=0.5)
    assert relationships.rivalry_snapshot(service)["alice"]["bob"] == 0.3
    assert relationships.rivalry_value(service, "alice", "bob") == 0.7
    assert relationships.rivalry_should_avoid(service, "alice", "bob") is True
    assert relationships.rivalry_top(service, "alice", 1) == [("bob", 0.9)]


def test_decay_and_remove_agent_delegate() -> None:
    service = FakeRelationshipService()
    relationships.decay(service)
    relationships.remove_agent(service, "alice")

    assert [name for name, _, _ in service.calls[-2:]] == ["decay", "remove_agent"]


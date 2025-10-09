from __future__ import annotations

from types import SimpleNamespace

from townlet.world.agents.snapshot import AgentSnapshot
from townlet.world.systems import affordances


class FakeRuntime:
    def __init__(self) -> None:
        self.started: list[tuple[str, str, str, int]] = []
        self.released: list[tuple[str, str, bool, str | None, str | None, int]] = []
        self.blocked: list[tuple[str, int]] = []
        self.resolved: list[int] = []

    def start(self, agent_id: str, object_id: str, affordance_id: str, *, tick: int):
        self.started.append((agent_id, object_id, affordance_id, tick))
        return True, {"meta": "value"}

    def release(
        self,
        agent_id: str,
        object_id: str,
        *,
        success: bool,
        reason: str | None,
        requested_affordance_id: str | None,
        tick: int,
    ):
        self.released.append((agent_id, object_id, success, reason, requested_affordance_id, tick))
        return requested_affordance_id, {"meta": "released"}

    def handle_blocked(self, object_id: str, tick: int) -> None:
        self.blocked.append((object_id, tick))

    def resolve(self, *, tick: int) -> None:
        self.resolved.append(tick)


def make_snapshot(agent_id: str) -> AgentSnapshot:
    return AgentSnapshot(
        agent_id=agent_id,
        position=(0, 0),
        needs={"hunger": 0.5, "energy": 0.5, "hygiene": 0.5},
        wallet=0.0,
    )


def test_start_and_release_delegate_to_runtime() -> None:
    runtime = FakeRuntime()

    success, metadata = affordances.start(
        runtime,
        agent_id="alice",
        object_id="stall",
        affordance_id="serve",
        tick=10,
    )
    assert success is True
    assert metadata == {"meta": "value"}

    affordance_id, release_metadata = affordances.release(
        runtime,
        agent_id="alice",
        object_id="stall",
        success=True,
        reason=None,
        requested_affordance_id="serve",
        tick=12,
    )
    assert affordance_id == "serve"
    assert release_metadata == {"meta": "released"}

    assert runtime.started == [("alice", "stall", "serve", 10)]
    assert runtime.released == [("alice", "stall", True, None, "serve", 12)]


def test_handle_blocked_and_resolve_delegate_to_runtime() -> None:
    runtime = FakeRuntime()

    affordances.handle_blocked(runtime, "stall", 15)
    affordances.resolve(runtime, 20)

    assert runtime.blocked == [("stall", 15)]
    assert runtime.resolved == [20]


def test_apply_outcome_updates_snapshot() -> None:
    snapshot = make_snapshot("alice")
    affordances.apply_outcome(
        snapshot,
        kind="start",
        success=True,
        duration=3,
        object_id="stall",
        affordance_id="serve",
        tick=30,
        metadata={"foo": "bar"},
    )

    assert snapshot.last_action_id == "start"
    assert snapshot.last_action_success is True
    assert snapshot.last_action_duration == 3

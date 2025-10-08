from __future__ import annotations

from townlet.core.sim_loop import SimulationLoop


class _Provider:
    def __init__(self, provider: str) -> None:
        self.provider = provider
        self.options: dict[str, object] = {}


class _Runtime:
    def __init__(self, world: str, policy: str, telemetry: str) -> None:
        self.world = _Provider(world)
        self.policy = _Provider(policy)
        self.telemetry = _Provider(telemetry)


class _Config:
    def __init__(self) -> None:
        self.runtime = _Runtime("dummy", "dummy", "dummy")
        self.seed = 0


def test_loop_runs_with_dummies() -> None:
    loop = SimulationLoop(_Config())
    loop.run_for(3)
    assert loop.tick == 3
    snapshot = loop.world.snapshot()
    assert snapshot["tick"] == 3
    assert len(loop.telemetry.events) == 3

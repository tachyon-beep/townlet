from __future__ import annotations

import types
from pathlib import Path

from townlet.config import load_config
from townlet.policy.training_orchestrator import PolicyTrainingOrchestrator

class _StubPolicy:
    def __init__(self) -> None:
        self._frames = [
            {
                "agent_id": "agent_1",
                "tick": 1,
                "map": [[[0.0]]],
                "features": [0.1, 0.2],
                "metadata": {},
                "anneal_context": {"ratio": 0.0},
            }
        ]

    def collect_trajectory(self, clear: bool = True) -> list[dict[str, object]]:
        frames = list(self._frames)
        if clear:
            self._frames.clear()
        return frames


class _StubTelemetry:
    @staticmethod
    def latest_events() -> list[dict[str, object]]:
        return []


class _StubLoop:
    def __init__(self, config: object) -> None:
        self.config = config
        self.world = types.SimpleNamespace(agents={"agent_1": object()})
        self.policy = _StubPolicy()
        self.telemetry = _StubTelemetry()

    def step(self) -> None:  # pragma: no cover - no-op
        return None


def test_capture_rollout_produces_dto_frames(monkeypatch) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    orchestrator = PolicyTrainingOrchestrator(config)
    monkeypatch.setattr(
        "townlet.core.sim_loop.SimulationLoop",
        _StubLoop,
    )
    monkeypatch.setattr(
        "townlet.policy.scenario_utils.apply_scenario",
        lambda loop, scenario: None,
    )
    monkeypatch.setattr(
        "townlet.policy.scenario_utils.seed_default_agents",
        lambda loop: None,
    )
    monkeypatch.setattr(
        "townlet.policy.scenario_utils.has_agents",
        lambda loop: True,
    )
    buffer = orchestrator.capture_rollout(ticks=1, auto_seed_agents=True)
    assert len(buffer) > 0
    agent_rollouts = buffer.by_agent()
    assert agent_rollouts
    first_rollout = next(iter(agent_rollouts.values()))
    assert first_rollout.frames
    frame = first_rollout.frames[0]
    assert "map" in frame and frame["map"] is not None
    assert "features" in frame and frame["features"] is not None
    # DTO plumbing should populate anneal_context even if empty
    assert "anneal_context" in frame

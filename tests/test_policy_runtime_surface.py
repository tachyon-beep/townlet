from __future__ import annotations

from pathlib import Path

from townlet.config import load_config
from townlet.policy.runner import PolicyRuntime
from townlet.policy.training_orchestrator import PolicyTrainingOrchestrator


def test_policy_runtime_exposes_transitions_and_trajectory() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    policy = PolicyRuntime(config)
    assert isinstance(policy.transitions, dict)
    assert isinstance(policy.trajectory, list)


def test_training_orchestrator_shares_transition_service() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    orchestrator = PolicyTrainingOrchestrator(config)
    assert isinstance(orchestrator.transitions, dict)
    assert isinstance(orchestrator.trajectory, list)

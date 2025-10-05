from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.policy.training_orchestrator import PolicyTrainingOrchestrator


def test_training_orchestrator_run_replay(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    orchestrator = PolicyTrainingOrchestrator(config)
    dataset = orchestrator.build_replay_dataset(
        orchestrator.config.training.replay_manifest  # type: ignore[arg-type]
    )
    summary = orchestrator.run_replay_dataset(dataset)
    assert summary and summary.get("batch") == pytest.approx(len(dataset))


def test_training_orchestrator_anneal_guardrails(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    orchestrator = PolicyTrainingOrchestrator(config)
    with pytest.raises(ValueError):
        orchestrator.run_anneal(dataset_config=None, in_memory_dataset=None)

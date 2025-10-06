from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import RuntimeProviderConfig, load_config
from townlet.core import policy_registry, telemetry_registry
from townlet.policy.fallback import StubPolicyBackend
from townlet.policy.training_orchestrator import PolicyTrainingOrchestrator
from townlet.telemetry.fallback import StubTelemetrySink


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


def test_capture_rollout_warns_on_stub_policy(caplog: pytest.LogCaptureFixture) -> None:
    project_root = Path(__file__).resolve().parents[1]
    base_config = load_config(project_root / "configs" / "examples" / "poc_hybrid.yaml")
    runtime_overrides = base_config.runtime.model_copy(
        update={
            "policy": RuntimeProviderConfig(provider="stub"),
            "telemetry": RuntimeProviderConfig(provider="stub"),
        }
    )
    stub_config = base_config.model_copy(update={"runtime": runtime_overrides})

    policy_reg = policy_registry()
    telemetry_reg = telemetry_registry()
    original_policy_stub = policy_reg._providers.get("stub")
    original_telemetry_stub = telemetry_reg._providers.get("stub")

    try:
        policy_reg.register("stub", lambda **kwargs: StubPolicyBackend(**kwargs))
        telemetry_reg.register("stub", lambda **kwargs: StubTelemetrySink(**kwargs))

        orchestrator = PolicyTrainingOrchestrator(stub_config)
        with caplog.at_level("WARNING", logger="townlet.policy.training_orchestrator"):
            buffer = orchestrator.capture_rollout(ticks=4, auto_seed_agents=True)

        assert len(buffer) == 0
        assert any("capture_rollout_stub_policy" in record.message for record in caplog.records)
    finally:
        if original_policy_stub is not None:
            policy_reg._providers["stub"] = original_policy_stub
        if original_telemetry_stub is not None:
            telemetry_reg._providers["stub"] = original_telemetry_stub

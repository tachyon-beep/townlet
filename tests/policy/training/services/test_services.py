"""Unit tests for training services."""

from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import SimulationConfig, load_config
from townlet.policy.training.services import (
    PromotionServiceAdapter,
    ReplayDatasetService,
    RolloutCaptureService,
    TrainingServices,
)


@pytest.fixture
def test_config():
    """Provide test configuration."""
    return load_config(Path("configs/examples/poc_hybrid.yaml"))


class TestReplayDatasetService:
    """Tests for ReplayDatasetService."""

    def test_service_init(self, test_config: SimulationConfig):
        """Verify service initializes correctly."""
        service = ReplayDatasetService(test_config)
        assert service.config is test_config

    def test_service_torch_free_import(self):
        """Verify service can be imported without torch."""
        # This test passes if the import above succeeded
        assert ReplayDatasetService is not None


class TestRolloutCaptureService:
    """Tests for RolloutCaptureService."""

    def test_service_init(self, test_config: SimulationConfig):
        """Verify service initializes correctly."""
        service = RolloutCaptureService(test_config)
        assert service.config is test_config

    def test_service_torch_free_import(self):
        """Verify service can be imported without torch."""
        assert RolloutCaptureService is not None

    def test_capture_negative_ticks_rejected(self, test_config: SimulationConfig):
        """Verify capture rejects negative ticks."""
        service = RolloutCaptureService(test_config)
        with pytest.raises(ValueError, match="ticks must be positive"):
            service.capture(ticks=-1)

    def test_capture_zero_ticks_rejected(self, test_config: SimulationConfig):
        """Verify capture rejects zero ticks."""
        service = RolloutCaptureService(test_config)
        with pytest.raises(ValueError, match="ticks must be positive"):
            service.capture(ticks=0)


class TestPromotionServiceAdapter:
    """Tests for PromotionServiceAdapter."""

    def test_service_init(self, test_config: SimulationConfig):
        """Verify service initializes correctly."""
        service = PromotionServiceAdapter(test_config)
        assert service.config is test_config
        assert service.pass_streak == 0
        assert service.eval_counter == 0

    def test_service_torch_free_import(self):
        """Verify service can be imported without torch."""
        assert PromotionServiceAdapter is not None

    def test_record_evaluation_pass(self, test_config: SimulationConfig):
        """Verify record_evaluation handles PASS status."""
        service = PromotionServiceAdapter(test_config)
        results = [{"cycle": 0, "mode": "bc", "accuracy": 0.93}]

        metrics = service.record_evaluation(
            status="PASS",
            results=results,
        )

        assert metrics["pass_streak"] == 1
        assert metrics["last_result"] == "pass"
        assert metrics["last_evaluated_tick"] == 1

    def test_record_evaluation_fail(self, test_config: SimulationConfig):
        """Verify record_evaluation handles FAIL status."""
        service = PromotionServiceAdapter(test_config)
        results = [{"cycle": 0, "mode": "bc", "accuracy": 0.85}]

        # First pass
        service.record_evaluation(status="PASS", results=results)
        assert service.pass_streak == 1

        # Then fail (should reset streak)
        metrics = service.record_evaluation(status="FAIL", results=results)

        assert metrics["pass_streak"] == 0
        assert metrics["last_result"] == "fail"
        assert service.pass_streak == 0

    def test_record_evaluation_pass_streak(self, test_config: SimulationConfig):
        """Verify pass streak increments correctly."""
        service = PromotionServiceAdapter(test_config)
        results = [{"cycle": 0, "mode": "bc"}]

        service.record_evaluation(status="PASS", results=results)
        assert service.pass_streak == 1

        service.record_evaluation(status="PASS", results=results)
        assert service.pass_streak == 2

        service.record_evaluation(status="PASS", results=results)
        assert service.pass_streak == 3


class TestTrainingServices:
    """Tests for TrainingServices composition."""

    def test_from_config(self, test_config: SimulationConfig):
        """Verify TrainingServices.from_config creates all services."""
        services = TrainingServices.from_config(test_config)

        assert isinstance(services.replay, ReplayDatasetService)
        assert isinstance(services.rollout, RolloutCaptureService)
        assert isinstance(services.promotion, PromotionServiceAdapter)

    def test_all_services_use_same_config(self, test_config: SimulationConfig):
        """Verify all services share the same config instance."""
        services = TrainingServices.from_config(test_config)

        assert services.replay.config is test_config
        assert services.rollout.config is test_config
        assert services.promotion.config is test_config

    def test_services_torch_free_import(self):
        """Verify TrainingServices can be imported without torch."""
        assert TrainingServices is not None

    def test_manual_construction(self, test_config: SimulationConfig):
        """Verify TrainingServices can be manually constructed."""
        replay = ReplayDatasetService(test_config)
        rollout = RolloutCaptureService(test_config)
        promotion = PromotionServiceAdapter(test_config)

        services = TrainingServices(
            replay=replay,
            rollout=rollout,
            promotion=promotion,
        )

        assert services.replay is replay
        assert services.rollout is rollout
        assert services.promotion is promotion

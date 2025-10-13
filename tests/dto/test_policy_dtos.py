"""Unit tests for policy training DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from townlet.dto.policy import (
    AnnealStageResultDTO,
    AnnealSummaryDTO,
    BCTrainingResultDTO,
    PPOTrainingResultDTO,
    TrainingResultBase,
)


class TestTrainingResultBase:
    """Tests for TrainingResultBase DTO."""

    def test_base_dto_defaults(self):
        """Verify base DTO has correct defaults."""
        base = TrainingResultBase()
        assert base.schema_version == "1.0.0"
        assert base.duration_sec is None

    def test_base_dto_with_duration(self):
        """Verify duration can be set."""
        base = TrainingResultBase(duration_sec=45.2)
        assert base.duration_sec == 45.2

    def test_base_dto_negative_duration_rejected(self):
        """Verify negative duration is rejected."""
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            TrainingResultBase(duration_sec=-1.0)

    def test_base_dto_frozen(self):
        """Verify DTO is immutable."""
        base = TrainingResultBase()
        with pytest.raises((ValidationError, AttributeError)):
            base.schema_version = "2.0.0"  # type: ignore

    def test_base_dto_extra_fields_rejected(self):
        """Verify unknown fields are rejected."""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            TrainingResultBase(unknown_field="value")  # type: ignore


class TestBCTrainingResultDTO:
    """Tests for BCTrainingResultDTO."""

    def test_bc_result_minimal(self):
        """Verify BC result with minimal required fields."""
        result = BCTrainingResultDTO(
            manifest="/path/to/manifest.json",
            accuracy=0.93,
            loss=0.15,
            learning_rate=1e-3,
            batch_size=32,
            epochs=10,
        )
        assert result.mode == "bc"
        assert result.manifest == "/path/to/manifest.json"
        assert result.accuracy == 0.93
        assert result.loss == 0.15
        assert result.learning_rate == 1e-3
        assert result.batch_size == 32
        assert result.epochs == 10
        assert result.schema_version == "1.0.0"

    def test_bc_result_with_optional_fields(self):
        """Verify BC result with optional fields."""
        result = BCTrainingResultDTO(
            manifest="/path/to/manifest.json",
            accuracy=0.93,
            loss=0.15,
            learning_rate=1e-3,
            batch_size=32,
            epochs=10,
            val_accuracy=0.91,
            val_loss=0.17,
            weight_decay=1e-4,
            device="cuda",
            duration_sec=45.2,
        )
        assert result.val_accuracy == 0.91
        assert result.val_loss == 0.17
        assert result.weight_decay == 1e-4
        assert result.device == "cuda"
        assert result.duration_sec == 45.2

    def test_bc_result_accuracy_out_of_range(self):
        """Verify accuracy must be in [0, 1]."""
        with pytest.raises(ValidationError, match="less than or equal to 1"):
            BCTrainingResultDTO(
                manifest="/path/to/manifest.json",
                accuracy=1.5,
                loss=0.15,
                learning_rate=1e-3,
                batch_size=32,
                epochs=10,
            )

    def test_bc_result_negative_loss(self):
        """Verify loss must be non-negative."""
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            BCTrainingResultDTO(
                manifest="/path/to/manifest.json",
                accuracy=0.93,
                loss=-0.15,
                learning_rate=1e-3,
                batch_size=32,
                epochs=10,
            )

    def test_bc_result_zero_learning_rate(self):
        """Verify learning rate must be positive."""
        with pytest.raises(ValidationError, match="greater than 0"):
            BCTrainingResultDTO(
                manifest="/path/to/manifest.json",
                accuracy=0.93,
                loss=0.15,
                learning_rate=0.0,
                batch_size=32,
                epochs=10,
            )

    def test_bc_result_serialization(self):
        """Verify BC result can be serialized to dict."""
        result = BCTrainingResultDTO(
            manifest="/path/to/manifest.json",
            accuracy=0.93,
            loss=0.15,
            learning_rate=1e-3,
            batch_size=32,
            epochs=10,
        )
        data = result.model_dump()
        assert isinstance(data, dict)
        assert data["mode"] == "bc"
        assert data["accuracy"] == 0.93


class TestPPOTrainingResultDTO:
    """Tests for PPOTrainingResultDTO."""

    def test_ppo_result_minimal_v1_0(self):
        """Verify PPO result with minimal v1.0 fields."""
        result = PPOTrainingResultDTO(
            epoch=1.0,
            updates=10.0,
            transitions=100.0,
            loss_policy=0.1,
            loss_value=0.2,
            loss_entropy=0.01,
            loss_total=0.29,
            clip_fraction=0.1,
            adv_mean=0.0,
            adv_std=1.0,
            grad_norm=1.0,
            kl_divergence=0.01,
            lr=1e-3,
            steps=100.0,
        )
        assert result.epoch == 1.0
        assert result.updates == 10.0
        assert result.telemetry_version == 1.2  # Default
        assert result.adv_zero_std_batches == 0.0  # Default health tracking
        assert result.epoch_duration_sec is None  # v1.1 optional

    def test_ppo_result_with_v1_1_fields(self):
        """Verify PPO result with v1.1 extended fields."""
        result = PPOTrainingResultDTO(
            epoch=5.0,
            updates=1000.0,
            transitions=10000.0,
            loss_policy=0.05,
            loss_value=0.10,
            loss_entropy=0.02,
            loss_total=0.13,
            clip_fraction=0.15,
            adv_mean=0.02,
            adv_std=0.8,
            grad_norm=1.2,
            kl_divergence=0.01,
            lr=1e-3,
            steps=10000.0,
            # v1.1 fields
            epoch_duration_sec=120.5,
            data_mode="rollout",
            cycle_id=1.0,
            batch_entropy_mean=0.5,
            batch_entropy_std=0.1,
            grad_norm_max=2.5,
            kl_divergence_max=0.02,
            reward_advantage_corr=0.7,
            rollout_ticks=100.0,
            log_stream_offset=5.0,
            queue_conflict_events=10.0,
            queue_conflict_intensity_sum=45.0,
        )
        assert result.epoch_duration_sec == 120.5
        assert result.data_mode == "rollout"
        assert result.cycle_id == 1.0
        assert result.queue_conflict_events == 10.0

    def test_ppo_result_with_v1_2_anneal_fields(self):
        """Verify PPO result with v1.2 anneal context fields."""
        result = PPOTrainingResultDTO(
            epoch=5.0,
            updates=1000.0,
            transitions=10000.0,
            loss_policy=0.05,
            loss_value=0.10,
            loss_entropy=0.02,
            loss_total=0.13,
            clip_fraction=0.15,
            adv_mean=0.02,
            adv_std=0.8,
            grad_norm=1.2,
            kl_divergence=0.01,
            lr=1e-3,
            steps=10000.0,
            # v1.2 anneal fields
            anneal_cycle=1.0,
            anneal_stage="ppo",
            anneal_dataset="rollout_001",
            anneal_bc_accuracy=0.93,
            anneal_bc_threshold=0.90,
            anneal_bc_passed=True,
            anneal_loss_baseline=0.15,
            anneal_queue_baseline=12.0,
            anneal_intensity_baseline=50.0,
            anneal_loss_flag=False,
            anneal_queue_flag=False,
            anneal_intensity_flag=False,
        )
        assert result.anneal_cycle == 1.0
        assert result.anneal_stage == "ppo"
        assert result.anneal_bc_accuracy == 0.93
        assert result.anneal_loss_flag is False

    def test_ppo_result_with_dynamic_conflict_fields(self):
        """Verify PPO result accepts dynamic conflict.* fields."""
        result = PPOTrainingResultDTO(
            epoch=1.0,
            updates=10.0,
            transitions=100.0,
            loss_policy=0.1,
            loss_value=0.2,
            loss_entropy=0.01,
            loss_total=0.29,
            clip_fraction=0.1,
            adv_mean=0.0,
            adv_std=1.0,
            grad_norm=1.0,
            kl_divergence=0.01,
            lr=1e-3,
            steps=100.0,
            **{
                "conflict.queue_conflict_events_avg": 5.0,
                "conflict.shared_meal_count_avg": 2.0,
            },
        )
        # Access via __pydantic_extra__
        assert result.__pydantic_extra__["conflict.queue_conflict_events_avg"] == 5.0
        assert result.__pydantic_extra__["conflict.shared_meal_count_avg"] == 2.0

    def test_ppo_result_rejects_invalid_dynamic_fields(self):
        """Verify PPO result rejects non-conflict dynamic fields."""
        with pytest.raises(ValidationError, match="Unknown field.*Only 'conflict.*' dynamic fields are allowed"):
            PPOTrainingResultDTO(
                epoch=1.0,
                updates=10.0,
                transitions=100.0,
                loss_policy=0.1,
                loss_value=0.2,
                loss_entropy=0.01,
                loss_total=0.29,
                clip_fraction=0.1,
                adv_mean=0.0,
                adv_std=1.0,
                grad_norm=1.0,
                kl_divergence=0.01,
                lr=1e-3,
                steps=100.0,
                **{"invalid_field": 123},
            )

    def test_ppo_result_clip_fraction_in_range(self):
        """Verify clip_fraction must be in [0, 1]."""
        with pytest.raises(ValidationError, match="less than or equal to 1"):
            PPOTrainingResultDTO(
                epoch=1.0,
                updates=10.0,
                transitions=100.0,
                loss_policy=0.1,
                loss_value=0.2,
                loss_entropy=0.01,
                loss_total=0.29,
                clip_fraction=1.5,  # Invalid
                adv_mean=0.0,
                adv_std=1.0,
                grad_norm=1.0,
                kl_divergence=0.01,
                lr=1e-3,
                steps=100.0,
            )

    def test_ppo_result_serialization_with_extras(self):
        """Verify PPO result serialization includes extra fields."""
        result = PPOTrainingResultDTO(
            epoch=1.0,
            updates=10.0,
            transitions=100.0,
            loss_policy=0.1,
            loss_value=0.2,
            loss_entropy=0.01,
            loss_total=0.29,
            clip_fraction=0.1,
            adv_mean=0.0,
            adv_std=1.0,
            grad_norm=1.0,
            kl_divergence=0.01,
            lr=1e-3,
            steps=100.0,
            **{"conflict.queue_events_avg": 5.0},
        )
        data = result.model_dump()
        assert data["epoch"] == 1.0
        assert data["conflict.queue_events_avg"] == 5.0


class TestAnnealStageResultDTO:
    """Tests for AnnealStageResultDTO."""

    def test_anneal_stage_bc(self):
        """Verify anneal BC stage result."""
        stage = AnnealStageResultDTO(
            cycle=1.0,
            mode="bc",
            accuracy=0.93,
            loss=0.15,
            threshold=0.90,
            passed=True,
            bc_weight=0.9,
        )
        assert stage.cycle == 1.0
        assert stage.mode == "bc"
        assert stage.accuracy == 0.93
        assert stage.passed is True
        assert stage.bc_weight == 0.9

    def test_anneal_stage_ppo(self):
        """Verify anneal PPO stage result."""
        stage = AnnealStageResultDTO(
            cycle=1.0,
            mode="ppo",
            loss_total=0.12,
            loss_policy=0.05,
            loss_value=0.07,
            queue_conflict_events=10.0,
            queue_conflict_intensity_sum=45.0,
            anneal_loss_flag=False,
            anneal_queue_flag=False,
            anneal_intensity_flag=False,
        )
        assert stage.cycle == 1.0
        assert stage.mode == "ppo"
        assert stage.loss_total == 0.12
        assert stage.anneal_loss_flag is False

    def test_anneal_stage_rolled_back(self):
        """Verify rolled_back flag works."""
        stage = AnnealStageResultDTO(
            cycle=1.0,
            mode="bc",
            accuracy=0.85,
            loss=0.20,
            threshold=0.90,
            passed=False,
            bc_weight=0.9,
            rolled_back=True,
        )
        assert stage.passed is False
        assert stage.rolled_back is True


class TestAnnealSummaryDTO:
    """Tests for AnnealSummaryDTO."""

    def test_anneal_summary_minimal(self):
        """Verify anneal summary with minimal fields."""
        stage1 = AnnealStageResultDTO(
            cycle=0.0, mode="bc", accuracy=0.93, passed=True
        )
        stage2 = AnnealStageResultDTO(
            cycle=0.0, mode="ppo", loss_total=0.12
        )
        summary = AnnealSummaryDTO(
            stages=[stage1, stage2],
            status="PASS",
            dataset_label="rollout_001",
        )
        assert len(summary.stages) == 2
        assert summary.status == "PASS"
        assert summary.dataset_label == "rollout_001"
        assert summary.baselines == {}

    def test_anneal_summary_with_baselines(self):
        """Verify anneal summary with baselines."""
        stage1 = AnnealStageResultDTO(
            cycle=0.0, mode="bc", accuracy=0.93, passed=True
        )
        summary = AnnealSummaryDTO(
            stages=[stage1],
            status="PASS",
            dataset_label="rollout_001",
            baselines={
                "rollout_001": {
                    "loss_total": 0.12,
                    "queue_conflict_events": 10.0,
                }
            },
        )
        assert "rollout_001" in summary.baselines
        assert summary.baselines["rollout_001"]["loss_total"] == 0.12

    def test_anneal_summary_with_promotion_metadata(self):
        """Verify anneal summary with promotion metadata."""
        stage1 = AnnealStageResultDTO(
            cycle=0.0, mode="bc", accuracy=0.93, passed=True
        )
        summary = AnnealSummaryDTO(
            stages=[stage1],
            status="PASS",
            dataset_label="rollout_001",
            promotion_pass_streak=2,
            promotion_candidate_ready=True,
        )
        assert summary.promotion_pass_streak == 2
        assert summary.promotion_candidate_ready is True

    def test_anneal_summary_serialization(self):
        """Verify anneal summary can be serialized."""
        stage1 = AnnealStageResultDTO(
            cycle=0.0, mode="bc", accuracy=0.93, passed=True
        )
        summary = AnnealSummaryDTO(
            stages=[stage1],
            status="PASS",
            dataset_label="rollout_001",
        )
        data = summary.model_dump()
        assert isinstance(data, dict)
        assert data["status"] == "PASS"
        assert len(data["stages"]) == 1
        assert data["stages"][0]["mode"] == "bc"

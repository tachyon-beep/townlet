"""Unit tests for BCStrategy."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from townlet.config import SimulationConfig, load_config
from townlet.dto.policy import BCTrainingResultDTO
from townlet.policy.training.contexts import TrainingContext
from townlet.policy.training.strategies import BCStrategy


@pytest.fixture
def test_config() -> SimulationConfig:
    """Provide test configuration."""
    return load_config(Path("configs/examples/poc_hybrid.yaml"))


@pytest.fixture
def test_context(test_config: SimulationConfig) -> TrainingContext:
    """Provide test training context."""
    return TrainingContext.from_config(test_config)


class TestBCStrategy:
    """Tests for BCStrategy."""

    def test_strategy_protocol_conformance(self):
        """Verify BCStrategy conforms to TrainingStrategy protocol."""
        from townlet.policy.training.strategies.base import TrainingStrategy

        strategy = BCStrategy()
        assert isinstance(strategy, TrainingStrategy)

    @patch("townlet.policy.models.torch_available")
    def test_torch_not_available_raises_error(
        self,
        mock_torch_available: MagicMock,
        test_context: TrainingContext,
    ):
        """Verify strategy raises error when PyTorch unavailable."""
        from townlet.policy.models import TorchNotAvailableError

        mock_torch_available.return_value = False
        strategy = BCStrategy()

        with pytest.raises(
            TorchNotAvailableError,
            match="PyTorch is required for behaviour cloning",
        ):
            strategy.run(test_context)

    @patch("townlet.policy.models.torch_available")
    def test_missing_manifest_raises_error(
        self,
        mock_torch_available: MagicMock,
        test_config: SimulationConfig,
    ):
        """Verify strategy raises error when manifest not configured."""
        mock_torch_available.return_value = True
        test_config.training.bc.manifest = None

        context = TrainingContext.from_config(test_config)
        strategy = BCStrategy()

        with pytest.raises(ValueError, match="BC manifest is required"):
            strategy.run(context)

    @patch("townlet.policy.models.torch_available")
    @patch("townlet.policy.bc.load_bc_samples")
    @patch("townlet.policy.bc.BCTrajectoryDataset")
    @patch("townlet.policy.bc.BCTrainer")
    def test_strategy_returns_valid_dto(
        self,
        mock_trainer_cls: MagicMock,
        mock_dataset_cls: MagicMock,
        mock_load_samples: MagicMock,
        mock_torch_available: MagicMock,
        test_context: TrainingContext,
    ):
        """Verify strategy returns valid BCTrainingResultDTO."""
        mock_torch_available.return_value = True

        # Configure BC manifest
        test_context.config.training.bc.manifest = Path("data/bc_manifest.json")

        # Mock dataset
        mock_dataset = MagicMock()
        mock_dataset.feature_dim = 128
        mock_dataset.map_shape = (9, 9, 3)
        mock_dataset.action_dim = 10
        mock_dataset_cls.return_value = mock_dataset

        # Mock trainer
        mock_trainer = MagicMock()
        mock_trainer.fit.return_value = {
            "accuracy": 0.92,
            "loss": 0.18,
            "val_accuracy": 0.90,
            "val_loss": 0.20,
        }
        mock_trainer_cls.return_value = mock_trainer

        # Execute
        strategy = BCStrategy()
        result = strategy.run(test_context)

        # Verify result type
        assert isinstance(result, BCTrainingResultDTO)

        # Verify required fields
        assert result.mode == "bc"
        assert result.manifest == str(test_context.config.training.bc.manifest)
        assert result.accuracy == 0.92
        assert result.loss == 0.18
        assert result.learning_rate == test_context.config.training.bc.learning_rate
        assert result.batch_size == test_context.config.training.bc.batch_size
        assert result.epochs == test_context.config.training.bc.epochs

        # Verify optional fields
        assert result.val_accuracy == 0.90
        assert result.val_loss == 0.20
        assert result.weight_decay == test_context.config.training.bc.weight_decay
        assert result.device == test_context.config.training.bc.device

        # Verify duration tracking
        assert result.duration_sec is not None
        assert result.duration_sec >= 0.0

    @patch("townlet.policy.models.torch_available")
    @patch("townlet.policy.bc.load_bc_samples")
    @patch("townlet.policy.bc.BCTrajectoryDataset")
    @patch("townlet.policy.bc.BCTrainer")
    def test_strategy_handles_minimal_metrics(
        self,
        mock_trainer_cls: MagicMock,
        mock_dataset_cls: MagicMock,
        mock_load_samples: MagicMock,
        mock_torch_available: MagicMock,
        test_context: TrainingContext,
    ):
        """Verify strategy handles metrics without validation fields."""
        mock_torch_available.return_value = True

        # Configure BC manifest
        test_context.config.training.bc.manifest = Path("data/bc_manifest.json")

        # Mock dataset
        mock_dataset = MagicMock()
        mock_dataset.feature_dim = 128
        mock_dataset.map_shape = (9, 9, 3)
        mock_dataset.action_dim = 10
        mock_dataset_cls.return_value = mock_dataset

        # Mock trainer with minimal metrics (no validation)
        mock_trainer = MagicMock()
        mock_trainer.fit.return_value = {
            "accuracy": 0.92,
            "loss": 0.18,
        }
        mock_trainer_cls.return_value = mock_trainer

        # Execute
        strategy = BCStrategy()
        result = strategy.run(test_context)

        # Verify optional fields are None
        assert result.val_accuracy is None
        assert result.val_loss is None

    @patch("townlet.policy.models.torch_available")
    @patch("townlet.policy.bc.load_bc_samples")
    @patch("townlet.policy.bc.BCTrajectoryDataset")
    @patch("townlet.policy.bc.BCTrainer")
    def test_strategy_creates_correct_trainer_params(
        self,
        mock_trainer_cls: MagicMock,
        mock_dataset_cls: MagicMock,
        mock_load_samples: MagicMock,
        mock_torch_available: MagicMock,
        test_context: TrainingContext,
    ):
        """Verify strategy passes correct parameters to BCTrainer."""
        mock_torch_available.return_value = True

        # Configure BC manifest
        test_context.config.training.bc.manifest = Path("data/bc_manifest.json")

        # Mock dataset
        mock_dataset = MagicMock()
        mock_dataset.feature_dim = 128
        mock_dataset.map_shape = (9, 9, 3)
        mock_dataset.action_dim = 10
        mock_dataset_cls.return_value = mock_dataset

        # Mock trainer
        mock_trainer = MagicMock()
        mock_trainer.fit.return_value = {"accuracy": 0.92, "loss": 0.18}
        mock_trainer_cls.return_value = mock_trainer

        # Execute
        strategy = BCStrategy()
        strategy.run(test_context)

        # Verify trainer was created with correct params
        mock_trainer_cls.assert_called_once()
        call_args = mock_trainer_cls.call_args

        # Check BCTrainingParams
        params = call_args[0][0]
        assert params.learning_rate == test_context.config.training.bc.learning_rate
        assert params.batch_size == test_context.config.training.bc.batch_size
        assert params.epochs == test_context.config.training.bc.epochs
        assert params.weight_decay == test_context.config.training.bc.weight_decay
        assert params.device == test_context.config.training.bc.device

        # Check policy config
        policy_cfg = call_args[0][1]
        assert policy_cfg.feature_dim == 128
        assert policy_cfg.map_shape == (9, 9, 3)
        assert policy_cfg.action_dim == 10

    @patch("townlet.policy.models.torch_available")
    @patch("townlet.policy.bc.load_bc_samples")
    @patch("townlet.policy.bc.BCTrajectoryDataset")
    @patch("townlet.policy.bc.BCTrainer")
    def test_dto_serialization(
        self,
        mock_trainer_cls: MagicMock,
        mock_dataset_cls: MagicMock,
        mock_load_samples: MagicMock,
        mock_torch_available: MagicMock,
        test_context: TrainingContext,
    ):
        """Verify DTO can be serialized to dict."""
        mock_torch_available.return_value = True

        # Configure BC manifest
        test_context.config.training.bc.manifest = Path("data/bc_manifest.json")

        # Mock dataset and trainer
        mock_dataset = MagicMock()
        mock_dataset.feature_dim = 128
        mock_dataset.map_shape = (9, 9, 3)
        mock_dataset.action_dim = 10
        mock_dataset_cls.return_value = mock_dataset

        mock_trainer = MagicMock()
        mock_trainer.fit.return_value = {"accuracy": 0.92, "loss": 0.18}
        mock_trainer_cls.return_value = mock_trainer

        # Execute
        strategy = BCStrategy()
        result = strategy.run(test_context)

        # Serialize
        result_dict = result.model_dump()

        # Verify serialization
        assert isinstance(result_dict, dict)
        assert result_dict["mode"] == "bc"
        assert result_dict["accuracy"] == 0.92
        assert result_dict["loss"] == 0.18
        assert "duration_sec" in result_dict

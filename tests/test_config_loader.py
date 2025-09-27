from pathlib import Path

import pytest
import yaml

from townlet.config import SimulationConfig, load_config


@pytest.fixture()
def poc_config(tmp_path: Path) -> Path:
    source = Path("configs/examples/poc_hybrid.yaml")
    target = tmp_path / "config.yaml"
    target.write_text(source.read_text())
    return target


def test_load_config(poc_config: Path) -> None:
    config = load_config(poc_config)
    assert isinstance(config, SimulationConfig)
    assert config.config_id == "v1.3.0"
    assert config.features.systems.observations == "hybrid"
    assert config.rewards.needs_weights.hunger == pytest.approx(1.0)
    assert config.queue_fairness.cooldown_ticks == 60
    assert config.embedding_allocator.cooldown_ticks == 2000
    assert config.embedding_allocator.max_slots == 64
    assert config.affordances.affordances_file.endswith("core.yaml")
    assert config.stability.affordance_fail_threshold == 5
    assert config.stability.lateness_threshold == 3
    assert config.rewards.decay_rates == {
        "hunger": 0.01,
        "hygiene": 0.005,
        "energy": 0.008,
    }
    assert config.economy == {
        "meal_cost": 0.4,
        "cook_energy_cost": 0.05,
        "cook_hygiene_cost": 0.02,
        "wage_income": 0.02,
        "ingredients_cost": 0.15,
        "stove_stock_replenish": 2,
    }
    assert "grocer" in config.jobs and "barista" in config.jobs
    assert config.behavior.job_arrival_buffer == 20
    assert config.employment.grace_ticks == 5
    assert config.employment.absent_cutoff == 30
    assert config.employment.max_absent_shifts == 3
    assert config.employment.daily_exit_cap == 2
    assert config.employment.enforce_job_loop is True
    assert config.observations_config.hybrid.local_window == 11
    assert config.observations_config.hybrid.include_targets is False
    assert config.ppo is None

    rivalry = config.conflict.rivalry
    assert rivalry.increment_per_conflict == pytest.approx(0.15)
    assert rivalry.decay_per_tick == pytest.approx(0.005)
    assert rivalry.ghost_step_boost == pytest.approx(1.5)
    assert rivalry.handover_boost == pytest.approx(0.4)
    assert rivalry.queue_length_boost == pytest.approx(0.25)
    assert rivalry.avoid_threshold == pytest.approx(0.7)
    assert rivalry.eviction_threshold == pytest.approx(0.05)
    assert rivalry.max_edges == 6


def test_invalid_queue_cooldown_rejected(tmp_path: Path) -> None:
    source = Path("configs/examples/poc_hybrid.yaml")
    config_data = yaml.safe_load(source.read_text())
    config_data["queue_fairness"]["cooldown_ticks"] = -1
    target = tmp_path / "config.yaml"
    target.write_text(yaml.safe_dump(config_data))

    with pytest.raises(ValueError):
        load_config(target)


def test_invalid_embedding_threshold_rejected(tmp_path: Path) -> None:
    source = Path("configs/examples/poc_hybrid.yaml")
    config_data = yaml.safe_load(source.read_text())
    config_data["embedding_allocator"]["reuse_warning_threshold"] = 0.9
    target = tmp_path / "config.yaml"
    target.write_text(yaml.safe_dump(config_data))

    with pytest.raises(ValueError):
        load_config(target)


def test_invalid_embedding_slot_count(tmp_path: Path) -> None:
    source = Path("configs/examples/poc_hybrid.yaml")
    config_data = yaml.safe_load(source.read_text())
    config_data["embedding_allocator"]["max_slots"] = 0
    target = tmp_path / "config.yaml"
    target.write_text(yaml.safe_dump(config_data))

    with pytest.raises(ValueError):
        load_config(target)


def test_invalid_affordance_file_absent(tmp_path: Path) -> None:
    source = Path("configs/examples/poc_hybrid.yaml")
    config_data = yaml.safe_load(source.read_text())
    config_data["affordances"]["affordances_file"] = "configs/affordances/missing.yaml"
    target = tmp_path / "config.yaml"
    target.write_text(yaml.safe_dump(config_data))

    config = load_config(target)
    assert config.affordances.affordances_file.endswith("missing.yaml")


def test_observation_variant_guard(tmp_path: Path) -> None:
    source = Path("configs/examples/poc_hybrid.yaml")
    config_data = yaml.safe_load(source.read_text())
    config_data["features"]["systems"]["observations"] = "unsupported"
    target = tmp_path / "config.yaml"
    target.write_text(yaml.safe_dump(config_data))

    with pytest.raises(ValueError, match="Input should be 'full', 'hybrid' or 'compact'"):
        load_config(target)


def test_ppo_config_defaults_roundtrip(tmp_path: Path) -> None:
    source = Path("configs/examples/poc_hybrid.yaml")
    config_data = yaml.safe_load(source.read_text())
    config_data["ppo"] = {}
    target = tmp_path / "config.yaml"
    target.write_text(yaml.safe_dump(config_data))

    config = load_config(target)
    assert config.ppo is not None
    assert config.ppo.learning_rate == pytest.approx(3e-4)
    assert config.ppo.max_grad_norm == pytest.approx(0.5)
    assert config.ppo.value_clip == pytest.approx(0.2)
    assert config.ppo.advantage_normalization is True
    assert config.ppo.num_mini_batches == 4


def test_observation_variant_full_supported(tmp_path: Path) -> None:
    source = Path("configs/examples/poc_hybrid.yaml")
    config_data = yaml.safe_load(source.read_text())
    config_data["features"]["systems"]["observations"] = "full"
    target = tmp_path / "config.yaml"
    target.write_text(yaml.safe_dump(config_data))

    config = load_config(target)
    assert config.observation_variant == "full"


def test_observation_variant_compact_supported(tmp_path: Path) -> None:
    source = Path("configs/examples/poc_hybrid.yaml")
    config_data = yaml.safe_load(source.read_text())
    config_data["features"]["systems"]["observations"] = "compact"
    target = tmp_path / "config.yaml"
    target.write_text(yaml.safe_dump(config_data))

    config = load_config(target)
    assert config.observation_variant == "compact"

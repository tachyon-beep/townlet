import sys
import types
from pathlib import Path

import pytest
import yaml

from townlet.config import SimulationConfig, load_config
from townlet.snapshots.migrations import clear_registry, migration_registry


@pytest.fixture()
def poc_config(tmp_path: Path) -> Path:
    source = Path("configs/examples/poc_hybrid.yaml")
    target = tmp_path / "config.yaml"
    target.write_text(source.read_text())
    return target


def test_demo_config_uses_file_transport() -> None:
    config = load_config(Path("configs/demo/poc_demo.yaml"))
    transport = config.telemetry.transport
    assert transport.type == "file"
    assert transport.file_path == Path("logs/demo_stream.jsonl")
    assert transport.buffer.max_batch_size == 32
    assert transport.buffer.flush_interval_ticks == 1



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
    assert config.lifecycle.respawn_delay_ticks == 0
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


def test_tcp_transport_requires_tls_or_explicit_plaintext(tmp_path: Path) -> None:
    source = Path("configs/examples/poc_hybrid.yaml")
    config_data = yaml.safe_load(source.read_text())
    config_data["telemetry"]["transport"] = {
        "type": "tcp",
        "endpoint": "localhost:5555",
    }
    target = tmp_path / "config.yaml"
    target.write_text(yaml.safe_dump(config_data))

    with pytest.raises(ValueError, match="requires enable_tls=true or allow_plaintext=true"):
        load_config(target)


def test_tcp_transport_tls_requires_cert_and_key_pair(tmp_path: Path) -> None:
    source = Path("configs/examples/poc_hybrid.yaml")
    config_data = yaml.safe_load(source.read_text())
    config_data["telemetry"]["transport"] = {
        "type": "tcp",
        "endpoint": "localhost:5555",
        "enable_tls": True,
        "key_file": "certs/client.key",
    }
    target = tmp_path / "config.yaml"
    target.write_text(yaml.safe_dump(config_data))

    with pytest.raises(ValueError, match="cert_file must be provided when key_file is set"):
        load_config(target)


def test_tcp_transport_tls_loads_with_hostname_disabled(tmp_path: Path) -> None:
    source = Path("configs/examples/poc_hybrid.yaml")
    config_data = yaml.safe_load(source.read_text())
    config_data["telemetry"]["transport"] = {
        "type": "tcp",
        "endpoint": "localhost:5555",
        "enable_tls": True,
        "verify_hostname": False,
        "allow_plaintext": False,
    }
    target = tmp_path / "config.yaml"
    target.write_text(yaml.safe_dump(config_data))

    config = load_config(target)
    transport = config.telemetry.transport
    assert transport.type == "tcp"
    assert transport.enable_tls is True
    assert transport.verify_hostname is False


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


def test_snapshot_autosave_cadence_validation(tmp_path: Path) -> None:
    source = Path("configs/examples/poc_hybrid.yaml")
    config_data = yaml.safe_load(source.read_text())
    config_data["snapshot"] = {
        "autosave": {"cadence_ticks": 50, "retain": 3},
    }
    target = tmp_path / "config.yaml"
    target.write_text(yaml.safe_dump(config_data))

    with pytest.raises(ValueError, match="cadence_ticks"):
        load_config(target)


def test_snapshot_identity_overrides_take_precedence(poc_config: Path) -> None:
    config = load_config(poc_config)
    config_payload = config.model_dump()
    config_payload["snapshot"] = {
        **config_payload.get("snapshot", {}),
        "identity": {
            "policy_hash": "abcde" * 8,
            "policy_artifact": "artifacts/policy.pt",
            "observation_variant": "full",
            "anneal_ratio": 0.75,
        },
    }
    override = SimulationConfig.model_validate(config_payload)

    identity = override.build_snapshot_identity(
        policy_hash=None,
        runtime_observation_variant="hybrid",
        runtime_anneal_ratio=0.2,
    )
    assert identity["policy_hash"] == "abcde" * 8
    assert identity["observation_variant"] == "full"
    assert identity["anneal_ratio"] == pytest.approx(0.75)
    assert identity["policy_artifact"] == "artifacts/policy.pt"


def test_register_snapshot_migrations_from_config(poc_config: Path) -> None:
    module_name = "tests.snapshot_fake_migration"
    fake_module = types.ModuleType(module_name)

    def migrate(state, config):
        state.config_id = config.config_id
        return state

    fake_module.migrate = migrate
    sys.modules[module_name] = fake_module

    config = load_config(poc_config)
    payload = config.model_dump()
    payload["snapshot"] = {
        **payload.get("snapshot", {}),
        "migrations": {
            "handlers": {"legacy-config": f"{module_name}:migrate"},
            "auto_apply": True,
        },
    }
    config_with_handler = SimulationConfig.model_validate(payload)

    try:
        clear_registry()
        config_with_handler.register_snapshot_migrations()
        path = migration_registry.find_path("legacy-config", config_with_handler.config_id)
        assert len(path) == 1
    finally:
        clear_registry()
        sys.modules.pop(module_name, None)


def test_telemetry_transport_defaults(poc_config: Path) -> None:
    config = load_config(poc_config)
    transport = config.telemetry.transport
    assert transport.type == "stdout"
    assert transport.retry.max_attempts == 3
    assert transport.buffer.max_batch_size == 32
    assert transport.buffer.flush_interval_ticks == 1


def test_telemetry_file_transport_requires_path(tmp_path: Path) -> None:
    source = Path("configs/examples/poc_hybrid.yaml")
    config_data = yaml.safe_load(source.read_text())
    config_data["telemetry"]["transport"] = {"type": "file"}
    target = tmp_path / "config.yaml"
    target.write_text(yaml.safe_dump(config_data))

    with pytest.raises(ValueError, match="file_path is required"):
        load_config(target)


def test_telemetry_tcp_transport_requires_endpoint(tmp_path: Path) -> None:
    source = Path("configs/examples/poc_hybrid.yaml")
    config_data = yaml.safe_load(source.read_text())
    config_data["telemetry"]["transport"] = {"type": "tcp", "endpoint": "  "}
    target = tmp_path / "config.yaml"
    target.write_text(yaml.safe_dump(config_data))

    with pytest.raises(ValueError, match="endpoint is required"):
        load_config(target)

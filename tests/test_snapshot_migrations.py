from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import SimulationConfig, load_config
from townlet.dto.world import (
    EmploymentSnapshot,
    IdentitySnapshot,
    QueueSnapshot,
    SimulationSnapshot,
)
from townlet.snapshots import SnapshotManager
from townlet.snapshots.migrations import clear_registry, register_migration


@pytest.fixture(scope="module")
def sample_config() -> SimulationConfig:
    config_path = Path("configs/examples/poc_hybrid.yaml")
    if not config_path.exists():
        pytest.skip("example config not found")
    return load_config(config_path)


@pytest.fixture(autouse=True)
def reset_registry() -> None:
    clear_registry()
    yield
    clear_registry()


def _basic_state(config: SimulationConfig) -> SimulationSnapshot:
    return SimulationSnapshot(
        config_id=config.config_id,
        tick=0,
        agents={},
        objects={},
        queues=QueueSnapshot(),
        employment=EmploymentSnapshot(),
        relationships={},
        identity=IdentitySnapshot(config_id=config.config_id),
    )


def test_snapshot_migration_applied(
    tmp_path: Path, sample_config: SimulationConfig
) -> None:
    source_config_id = "legacy-config"
    state = _basic_state(sample_config).model_copy(
        update={
            "config_id": source_config_id,
            "identity": IdentitySnapshot(config_id=source_config_id),
        }
    )
    manager = SnapshotManager(tmp_path)
    path = manager.save(state)

    def migrate(state: dict, config: SimulationConfig) -> dict:
        # Update both config_id and identity to match target config
        migrated = dict(state)
        migrated["config_id"] = config.config_id
        identity = dict(migrated.get("identity", {}))
        identity["config_id"] = config.config_id
        migrated["identity"] = identity
        return migrated

    register_migration(source_config_id, sample_config.config_id, migrate)

    loaded = manager.load(path, sample_config, allow_migration=True)
    assert loaded.config_id == sample_config.config_id
    # Access identity DTO attribute
    assert sample_config.config_id == loaded.identity.config_id
    # Access migrations DTO attribute
    assert len(loaded.migrations.applied) > 0


def test_snapshot_migration_multi_step(
    tmp_path: Path, sample_config: SimulationConfig
) -> None:
    manager = SnapshotManager(tmp_path)
    initial_state = _basic_state(sample_config).model_copy(
        update={
            "config_id": "v1.0",
            "identity": IdentitySnapshot(config_id="v1.0"),
        }
    )
    snapshot_path = manager.save(initial_state)

    def migrate_v1_to_v1_1(
        state: dict, config: SimulationConfig
    ) -> dict:
        migrated = dict(state)
        migrated["config_id"] = "v1.1"
        identity = dict(migrated.get("identity", {}))
        identity["config_id"] = "v1.1"
        migrated["identity"] = identity
        return migrated

    register_migration("v1.0", "v1.1", migrate_v1_to_v1_1)

    def migrate_to_target(
        state: dict, config: SimulationConfig
    ) -> dict:
        migrated = dict(state)
        migrated["config_id"] = config.config_id
        identity = dict(migrated.get("identity", {}))
        identity["config_id"] = config.config_id
        migrated["identity"] = identity
        return migrated

    register_migration("v1.1", sample_config.config_id, migrate_to_target)

    loaded = manager.load(snapshot_path, sample_config, allow_migration=True)
    assert loaded.config_id == sample_config.config_id
    # Access migrations DTO attribute
    assert len(loaded.migrations.applied) == 2


def test_snapshot_migration_missing_path_raises(
    tmp_path: Path, sample_config: SimulationConfig
) -> None:
    manager = SnapshotManager(tmp_path)
    state = _basic_state(sample_config).model_copy(
        update={
            "config_id": "unmatched",
            "identity": IdentitySnapshot(config_id="unmatched"),
        }
    )
    path = manager.save(state)

    with pytest.raises(ValueError):
        manager.load(path, sample_config)

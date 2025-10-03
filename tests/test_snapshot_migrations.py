from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from townlet.config import SimulationConfig, load_config
from townlet.snapshots import SnapshotManager, SnapshotState
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


def _basic_state(config: SimulationConfig) -> SnapshotState:
    return SnapshotState(config_id=config.config_id, tick=0)


def test_snapshot_migration_applied(
    tmp_path: Path, sample_config: SimulationConfig
) -> None:
    source_config_id = "legacy-config"
    state = replace(_basic_state(sample_config), config_id=source_config_id)
    manager = SnapshotManager(tmp_path)
    path = manager.save(state)

    def migrate(state: SnapshotState, config: SimulationConfig) -> SnapshotState:
        return replace(state, config_id=config.config_id)

    register_migration(source_config_id, sample_config.config_id, migrate)

    loaded = manager.load(path, sample_config, allow_migration=True)
    assert loaded.config_id == sample_config.config_id
    assert sample_config.config_id == loaded.identity.get("config_id")
    assert loaded.migrations["applied"]


def test_snapshot_migration_multi_step(
    tmp_path: Path, sample_config: SimulationConfig
) -> None:
    manager = SnapshotManager(tmp_path)
    initial_state = replace(_basic_state(sample_config), config_id="v1.0")
    snapshot_path = manager.save(initial_state)

    register_migration(
        "v1.0", "v1.1", lambda state, config: replace(state, config_id="v1.1")
    )

    def migrate_to_target(
        state: SnapshotState, config: SimulationConfig
    ) -> SnapshotState:
        return replace(state, config_id=config.config_id)

    register_migration("v1.1", sample_config.config_id, migrate_to_target)

    loaded = manager.load(snapshot_path, sample_config, allow_migration=True)
    assert loaded.config_id == sample_config.config_id
    assert len(loaded.migrations["applied"]) == 2


def test_snapshot_migration_missing_path_raises(
    tmp_path: Path, sample_config: SimulationConfig
) -> None:
    manager = SnapshotManager(tmp_path)
    state = replace(_basic_state(sample_config), config_id="unmatched")
    path = manager.save(state)

    with pytest.raises(ValueError):
        manager.load(path, sample_config)

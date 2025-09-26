from __future__ import annotations

import json
from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.snapshots.state import SNAPSHOT_SCHEMA_VERSION, SnapshotManager, SnapshotState


@pytest.fixture(scope="module")
def sample_config() -> object:
    config_path = Path("configs/examples/poc_hybrid.yaml")
    if not config_path.exists():
        pytest.skip("example config not found")
    return load_config(config_path)


def test_snapshot_round_trip(tmp_path: Path, sample_config) -> None:
    manager = SnapshotManager(root=tmp_path)
    state = SnapshotState(
        config_id=sample_config.config_id,
        tick=42,
        relationships={
            "alice": {"bob": 0.5, "carol": -0.2},
            "bob": {"alice": 0.4},
        },
    )
    path = manager.save(state)
    loaded = manager.load(path, sample_config)
    assert loaded == state


def test_snapshot_config_mismatch_raises(tmp_path: Path, sample_config) -> None:
    manager = SnapshotManager(root=tmp_path)
    state = SnapshotState(config_id="other-config", tick=3)
    path = manager.save(state)
    with pytest.raises(ValueError):
        manager.load(path, sample_config)


def test_snapshot_missing_relationships_field_rejected(tmp_path: Path, sample_config) -> None:
    manager = SnapshotManager(root=tmp_path)
    path = tmp_path / "snapshot-1.json"
    payload = {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "state": {"config_id": sample_config.config_id, "tick": 1},
    }
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        manager.load(path, sample_config)


def test_snapshot_schema_version_mismatch(tmp_path: Path, sample_config) -> None:
    manager = SnapshotManager(root=tmp_path)
    state = SnapshotState(config_id=sample_config.config_id, tick=1)
    path = manager.save(state)
    data = json.loads(path.read_text())
    data["schema_version"] = "0.9"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        manager.load(path, sample_config)

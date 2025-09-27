from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from townlet.config import SimulationConfig, load_config
from townlet.telemetry.publisher import TelemetryPublisher
from townlet.world.grid import WorldState


def _configure_with_manifest(manifest_path: Path) -> SimulationConfig:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    data = config.model_dump()
    data["affordances"]["affordances_file"] = str(manifest_path)
    return SimulationConfig.model_validate(data)


def test_affordance_manifest_loads_and_exposes_metadata(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text(
        """
- type: object
  id: bench_1
  object_type: bench
  stock:
    seats: 2
- id: sit_down
  object_type: bench
  duration: 5
  effects:
    energy: 0.1

"""
    )

    config = _configure_with_manifest(manifest)
    world = WorldState.from_config(config)

    assert "bench_1" in world.objects
    assert "sit_down" in world.affordances

    metadata = world.affordance_manifest_metadata()
    assert metadata["path"] == str(manifest)
    assert metadata["object_count"] == 1
    assert metadata["affordance_count"] == 1
    expected_checksum = hashlib.sha256(manifest.read_bytes()).hexdigest()
    assert metadata["checksum"] == expected_checksum


def test_affordance_manifest_duplicate_ids_fail(tmp_path: Path) -> None:
    manifest = tmp_path / "duplicate.yaml"
    manifest.write_text(
        """
- type: object
  id: fridge_1
  object_type: fridge
- id: fridge_1
  object_type: fridge
  duration: 10
  effects:
    hunger: 0.2
"""
    )

    config = _configure_with_manifest(manifest)
    with pytest.raises(RuntimeError, match="duplicate"):
        WorldState.from_config(config)


def test_affordance_manifest_missing_duration_fails(tmp_path: Path) -> None:
    manifest = tmp_path / "invalid.yaml"
    manifest.write_text(
        """
- id: cook
  object_type: stove
  effects:
    hunger: 0.1
"""
    )
    config = _configure_with_manifest(manifest)
    with pytest.raises(RuntimeError, match="duration"):
        WorldState.from_config(config)


def test_affordance_manifest_checksum_exposed_in_telemetry(tmp_path: Path) -> None:
    manifest = tmp_path / "telemetry.yaml"
    manifest.write_text(
        """
- type: object
  id: stove_1
  object_type: stove
- id: cook_omelette
  object_type: stove
  duration: 12
  effects:
    hunger: 0.3
    energy: -0.05
"""
    )
    config = _configure_with_manifest(manifest)
    world = WorldState.from_config(config)
    publisher = TelemetryPublisher(config)
    publisher.publish_tick(
        tick=1,
        world=world,
        observations={},
        rewards={},
        events=[],
    )
    meta = publisher.latest_affordance_manifest()
    assert meta["path"] == str(manifest)
    assert meta["checksum"] == hashlib.sha256(manifest.read_bytes()).hexdigest()

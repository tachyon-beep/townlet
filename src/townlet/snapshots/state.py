"""Snapshot persistence scaffolding."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Mapping

from townlet.config import SimulationConfig


SNAPSHOT_SCHEMA_VERSION = "1.0"


@dataclass
class SnapshotState:
    config_id: str
    tick: int
    relationships: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        return {
            "config_id": self.config_id,
            "tick": self.tick,
            "relationships": {
                owner: dict(edges) for owner, edges in self.relationships.items()
            },
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "SnapshotState":
        if "config_id" not in payload or "tick" not in payload:
            raise ValueError("Snapshot payload missing required fields")
        config_id = str(payload["config_id"])
        tick = int(payload["tick"])
        if "relationships" not in payload:
            raise ValueError("Snapshot payload missing relationships field")
        relationships_obj = payload["relationships"]
        if not isinstance(relationships_obj, Mapping):
            raise ValueError("Snapshot relationships field must be a mapping")
        relationships: Dict[str, Dict[str, float]] = {}
        for owner, edges in relationships_obj.items():
            if not isinstance(edges, Mapping):
                raise ValueError("Relationship edges must be mappings")
            relationships[str(owner)] = {
                str(other): float(value) for other, value in edges.items()
            }
        return cls(config_id=config_id, tick=tick, relationships=relationships)


class SnapshotManager:
    """Handles save/load of simulation state and RNG streams."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def save(self, state: SnapshotState) -> Path:
        document = {
            "schema_version": SNAPSHOT_SCHEMA_VERSION,
            "state": state.as_dict(),
        }
        self.root.mkdir(parents=True, exist_ok=True)
        target = self.root / f"snapshot-{state.tick}.json"
        target.write_text(json.dumps(document, indent=2, sort_keys=True))
        return target

    def load(self, path: Path, config: SimulationConfig) -> SnapshotState:
        if not path.exists():
            raise FileNotFoundError(path)
        payload = json.loads(path.read_text())
        schema_version = payload.get("schema_version")
        if schema_version != SNAPSHOT_SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported snapshot schema version: {schema_version}"
            )
        state_payload = payload.get("state")
        if not isinstance(state_payload, Mapping):
            raise ValueError("Snapshot document missing state payload")
        state = SnapshotState.from_dict(state_payload)
        if state.config_id != config.config_id:
            raise ValueError(
                "Snapshot config_id mismatch: expected %s, got %s"
                % (config.config_id, state.config_id)
            )
        return state

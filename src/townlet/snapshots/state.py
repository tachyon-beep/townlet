"""Snapshot persistence scaffolding."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from townlet.config import SimulationConfig


@dataclass
class SnapshotState:
    config_id: str
    tick: int


class SnapshotManager:
    """Handles save/load of simulation state and RNG streams."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def save(self, state: SnapshotState) -> Path:
        # TODO(@townlet): Persist world state, RNG seeds, and policy hash.
        target = self.root / f"snapshot-{state.tick}.json"
        target.write_text("{}")
        return target

    def load(self, path: Path, config: SimulationConfig) -> SnapshotState:
        # TODO(@townlet): Validate config_id and reconstruct world state.
        _ = path, config
        raise NotImplementedError

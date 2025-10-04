from __future__ import annotations

from pathlib import Path

import numpy as np

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world.grid import AgentSnapshot

BASE_CONFIG = Path("configs/examples/poc_hybrid.yaml")
DATA_DIR = Path("tests/data/observations")


def _build_payload(variant: str) -> dict[str, object]:
    config = load_config(BASE_CONFIG)
    systems = config.features.systems.model_copy(update={"observations": variant})
    features = config.features.model_copy(update={"systems": systems})
    config = config.model_copy(update={"features": features})

    loop = SimulationLoop(config)
    world = loop.world
    world.agents.clear()
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.4, "hygiene": 0.6, "energy": 0.8},
        wallet=5.0,
    )

    builder = loop.observations
    batch = builder.build_batch(world, terminated={})
    return batch["alice"]


REQUIRED_FEATURES = {
    "need_hunger",
    "need_hygiene",
    "need_energy",
    "wallet",
    "time_sin",
    "time_cos",
    "ctx_reset_flag",
}


def test_observation_baselines_match_recorded_snapshots() -> None:
    for variant in ("hybrid", "full", "compact"):
        payload = _build_payload(variant)
        path = DATA_DIR / f"baseline_{variant}.npz"
        stored = np.load(path, allow_pickle=True)

        np.testing.assert_allclose(payload["map"], stored["map"])
        np.testing.assert_allclose(payload["features"], stored["features"])

        stored_metadata = stored["metadata"][0]
        assert payload["metadata"] == stored_metadata

        assert payload["map"].dtype == np.float32
        assert payload["features"].dtype == np.float32
        assert payload["metadata"]["variant"] == variant

        feature_names = payload["metadata"].get("feature_names", [])
        assert REQUIRED_FEATURES.issubset(set(feature_names))

        if variant == "compact":
            assert payload["map"].size == 0
        else:
            channels, height, width = payload["map"].shape
            assert channels == len(payload["metadata"]["map_channels"])
            assert height == width == 11

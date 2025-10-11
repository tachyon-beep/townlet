from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pytest

from townlet.config.loader import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.observations import ObservationBuilder
from townlet.world.core.runtime_adapter import ensure_world_adapter

torch = pytest.importorskip("torch")


def _normalise_features(payload: Iterable[float] | None, width: int) -> torch.Tensor:
    if payload is None:
        return torch.zeros(width, dtype=torch.float32)
    if isinstance(payload, np.ndarray):
        vector = torch.from_numpy(payload.astype(np.float32).reshape(-1))
    else:
        vector = torch.tensor(list(payload), dtype=torch.float32)
    if vector.numel() == width:
        return vector
    if vector.numel() > width:
        return vector[:width]
    return torch.nn.functional.pad(vector, (0, width - vector.numel()))


def test_dto_ml_smoke_parity() -> None:
    config_path = Path("configs/examples/poc_hybrid.yaml")
    config = load_config(config_path)
    loop = SimulationLoop(
        config,
        policy_provider="scripted",
        telemetry_provider="stub",
    )
    dto_history = []
    reward_history = []
    legacy_batches = []
    observation_builder = ObservationBuilder(config=config)
    try:
        for _ in range(5):
            artifacts = loop.step()
            envelope = artifacts.envelope
            dto_history.append(envelope)
            reward_history.append(dict(artifacts.rewards))
            adapter = ensure_world_adapter(loop.world)
            legacy_batch = observation_builder.build_batch(adapter, {})
            legacy_batches.append(legacy_batch)
    finally:
        loop.close()

    baseline_path = Path("docs/architecture_review/WP_NOTES/WP3/dto_parity/ml_dimensions.txt")
    feature_dim_baseline = None
    map_shape_baseline = None
    if baseline_path.exists():
        text = baseline_path.read_text(encoding="utf-8").strip().splitlines()
        for line in text:
            if line.startswith("feature_dim="):
                feature_dim_baseline = int(line.split("=", 1)[1])
            if line.startswith("map_shape="):
                value = line.split("=", 1)[1].strip().strip("()")
                map_shape_baseline = tuple(int(part) for part in value.split(",") if part)

    feature_dim = 0
    map_dim = 0
    for envelope, legacy_batch in zip(dto_history, legacy_batches):
        for agent in envelope.agents:
            legacy_payload = legacy_batch.get(agent.agent_id, {})
            legacy_features = legacy_payload.get("features")
            if legacy_features is not None:
                feature_dim = max(feature_dim, np.asarray(legacy_features).size)
            elif agent.features:
                feature_dim = max(feature_dim, len(agent.features))
            legacy_map = legacy_payload.get("map")
            if legacy_map is not None:
                map_dim = max(map_dim, np.asarray(legacy_map, dtype=np.float32).size)
            elif agent.map is not None:
                map_dim = max(map_dim, np.asarray(agent.map, dtype=np.float32).size)
    if feature_dim_baseline is not None:
        feature_dim = feature_dim_baseline
    else:
        if feature_dim == 0:
            feature_dim = map_dim
        if feature_dim == 0:
            feature_dim = 1
    assert feature_dim > 0

    action_dim = 6
    if map_shape_baseline is not None and map_dim > 0:
        assert map_dim == int(np.prod(map_shape_baseline))

    torch.manual_seed(42)
    model = torch.nn.Linear(feature_dim, action_dim)
    softmax = torch.nn.Softmax(dim=-1)

    for idx, envelope in enumerate(dto_history):
        legacy_batch = legacy_batches[idx]
        for agent in envelope.agents:
            agent_id = agent.agent_id
            dto_source: Iterable[float] | None
            dto_source = agent.features or (
                np.asarray(agent.map, dtype=np.float32).reshape(-1)
                if agent.map is not None
                else None
            )
            dto_features = _normalise_features(dto_source, feature_dim)

            legacy_payload = legacy_batch.get(agent_id, {})
            legacy_vector = legacy_payload.get("features")
            if legacy_vector is None:
                legacy_map = legacy_payload.get("map")
                if legacy_map is not None:
                    legacy_vector = np.asarray(legacy_map, dtype=np.float32).reshape(-1)
            legacy_features = _normalise_features(legacy_vector, feature_dim)

            np.testing.assert_allclose(
                dto_features.detach().numpy(),
                legacy_features.detach().numpy(),
                atol=1e-6,
            )

            with torch.no_grad():
                dto_logits = model(dto_features)
                legacy_logits = model(legacy_features)
            np.testing.assert_allclose(
                dto_logits.detach().numpy(),
                legacy_logits.detach().numpy(),
                atol=1e-6,
            )

            dto_probs = softmax(dto_logits)
            dto_arr = dto_probs.detach().numpy()
            dto_action = int(torch.argmax(dto_probs).item())
            assert np.isfinite(dto_arr).all()
            assert 0 <= dto_action < action_dim

    # Ensure reward stream remains sane across ticks for the smoke scenario.
    assert reward_history
    for reward_tick in reward_history:
        assert all(np.isfinite(value) for value in reward_tick.values())

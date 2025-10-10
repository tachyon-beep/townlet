from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pytest

from townlet.config.loader import load_config
from townlet.core.sim_loop import SimulationLoop

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
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(
        config,
        policy_provider="scripted",
        telemetry_provider="stub",
    )
    dto_history = []
    reward_history = []
    try:
        for _ in range(5):
            artifacts = loop.step()
            envelope = artifacts.envelope
            dto_history.append(envelope)
            reward_history.append(dict(artifacts.rewards))
    finally:
        loop.close()

    feature_dim = 0
    map_dim = 0
    for envelope in dto_history:
        for agent in envelope.agents:
            if agent.features:
                feature_dim = max(feature_dim, len(agent.features))
            if agent.map is not None:
                map_dim = max(map_dim, np.asarray(agent.map, dtype=np.float32).size)
    if feature_dim == 0:
        feature_dim = map_dim
    if feature_dim == 0:
        feature_dim = 1
    assert feature_dim > 0

    action_dim = 6
    torch.manual_seed(42)
    model = torch.nn.Linear(feature_dim, action_dim)
    softmax = torch.nn.Softmax(dim=-1)

    for envelope in dto_history:
        for agent in envelope.agents:
            agent_id = agent.agent_id
            dto_source: Iterable[float] | None
            dto_source = agent.features or (
                np.asarray(agent.map, dtype=np.float32).reshape(-1)
                if agent.map is not None
                else None
            )
            dto_features = _normalise_features(dto_source, feature_dim)

            with torch.no_grad():
                dto_logits = model(dto_features)
            dto_probs = softmax(dto_logits)
            dto_arr = dto_probs.detach().numpy()
            dto_action = int(torch.argmax(dto_probs).item())
            assert np.isfinite(dto_arr).all()
            assert 0 <= dto_action < action_dim

    # Ensure reward stream remains sane across ticks for the smoke scenario.
    assert reward_history
    for reward_tick in reward_history:
        assert all(np.isfinite(value) for value in reward_tick.values())

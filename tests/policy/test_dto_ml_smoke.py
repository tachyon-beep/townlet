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
    legacy_history = []
    reward_history = []
    try:
        for _ in range(5):
            artifacts = loop.step()
            envelope = loop._policy_observation_envelope  # type: ignore[attr-defined]
            assert envelope is not None
            dto_history.append(envelope)
            legacy_history.append(artifacts.observations)
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
    for legacy in legacy_history:
        for payload in legacy.values():
            features = payload.get("features") if isinstance(payload, dict) else None
            if isinstance(features, (list, tuple)) and features:
                feature_dim = max(feature_dim, len(features))
            map_payload = payload.get("map") if isinstance(payload, dict) else None
            if map_payload is not None:
                map_dim = max(map_dim, np.asarray(map_payload, dtype=np.float32).size)
    if feature_dim == 0:
        feature_dim = map_dim
    if feature_dim == 0:
        feature_dim = 1
    assert feature_dim > 0

    action_dim = 6
    torch.manual_seed(42)
    model = torch.nn.Linear(feature_dim, action_dim)
    softmax = torch.nn.Softmax(dim=-1)

    for envelope, legacy in zip(dto_history, legacy_history):
        for agent in envelope.agents:
            agent_id = agent.agent_id
            legacy_payload = legacy.get(agent_id)
            assert isinstance(legacy_payload, dict)
            dto_source: Iterable[float] | None
            legacy_source: Iterable[float] | None
            dto_source = agent.features or (
                np.asarray(agent.map, dtype=np.float32).reshape(-1)
                if agent.map is not None
                else None
            )
            legacy_features_raw = legacy_payload.get("features")
            if isinstance(legacy_features_raw, (list, tuple)):
                legacy_source = legacy_features_raw
            else:
                map_payload = legacy_payload.get("map")
                legacy_source = (
                    np.asarray(map_payload, dtype=np.float32).reshape(-1)
                    if map_payload is not None
                    else None
                )
            dto_features = _normalise_features(dto_source, feature_dim)
            legacy_features = _normalise_features(legacy_source, feature_dim)

            with torch.no_grad():
                dto_logits = model(dto_features)
                legacy_logits = model(legacy_features)
            dto_probs = softmax(dto_logits)
            legacy_probs = softmax(legacy_logits)
            dto_arr = dto_probs.detach().numpy()
            legacy_arr = legacy_probs.detach().numpy()
            try:
                np.testing.assert_allclose(
                    dto_arr,
                    legacy_arr,
                    rtol=1e-5,
                    atol=1e-5,
                )
            except AssertionError as exc:
                diff = np.abs(dto_arr - legacy_arr)
                summary = {
                    "agent": agent_id,
                    "tick": envelope.tick,
                    "max_abs_diff": float(diff.max(initial=0.0)),
                    "dto_probs": dto_arr.tolist(),
                    "legacy_probs": legacy_arr.tolist(),
                }
                pytest.fail(f"DTO vs legacy probability mismatch: {summary}")  # pragma: no cover
            dto_action = int(torch.argmax(dto_probs).item())
            legacy_action = int(torch.argmax(legacy_probs).item())
            assert dto_action == legacy_action

    # Ensure reward stream remains sane across ticks for the smoke scenario.
    assert reward_history
    for reward_tick in reward_history:
        assert all(np.isfinite(value) for value in reward_tick.values())

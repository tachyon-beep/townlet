import pytest

from townlet.policy.models import (
    ConflictAwarePolicyConfig,
    ConflictAwarePolicyNetwork,
    TorchNotAvailableError,
    torch_available,
)


def test_conflict_policy_network_requires_torch_when_unavailable() -> None:
    if torch_available():
        pytest.skip("Torch present; run torch-specific tests separately")
    cfg = ConflictAwarePolicyConfig(feature_dim=36, map_shape=(4, 11, 11), action_dim=5)
    with pytest.raises(TorchNotAvailableError):
        ConflictAwarePolicyNetwork(cfg)  # type: ignore[call-arg]


@pytest.mark.skipif(not torch_available(), reason="Torch not installed")
def test_conflict_policy_network_forward() -> None:
    import torch

    cfg = ConflictAwarePolicyConfig(
        feature_dim=36, map_shape=(4, 11, 11), action_dim=5, hidden_dim=16
    )
    net = ConflictAwarePolicyNetwork(cfg)  # type: ignore[call-arg]
    batch = 3
    map_tensor = torch.randn(batch, *cfg.map_shape)
    features = torch.randn(batch, cfg.feature_dim)
    logits, value = net(map_tensor, features)
    assert logits.shape == (batch, cfg.action_dim)
    assert value.shape == (batch,)

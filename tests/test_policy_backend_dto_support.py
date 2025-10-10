from __future__ import annotations

import pytest

from townlet.policy.api import resolve_policy_backend
from townlet.policy.fallback import StubPolicyBackend


def test_resolve_policy_backend_exposes_dto_capability() -> None:
    backend = resolve_policy_backend(provider="stub")
    assert isinstance(backend, StubPolicyBackend)
    assert backend.supports_observation_envelope() is True


def test_stub_backend_warns_on_legacy_observations() -> None:
    backend = StubPolicyBackend()
    with pytest.deprecated_call(match="legacy observation batches"):
        backend.decide(world=None, tick=0, observations={"agent-1": {}})


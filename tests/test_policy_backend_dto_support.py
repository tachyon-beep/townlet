from __future__ import annotations

from townlet.dto.observations import ObservationEnvelope
from townlet.policy.api import resolve_policy_backend
from townlet.policy.fallback import StubPolicyBackend


def test_resolve_policy_backend_exposes_dto_capability() -> None:
    backend = resolve_policy_backend(provider="stub")
    assert isinstance(backend, StubPolicyBackend)
    assert backend.supports_observation_envelope() is True


def test_stub_backend_accepts_dto_envelope() -> None:
    backend = StubPolicyBackend()
    envelope = ObservationEnvelope(tick=0, agents=[])
    assert backend.decide(world=None, tick=0, envelope=envelope) == {}

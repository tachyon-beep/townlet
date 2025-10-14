"""Stub policy backend used when optional ML dependencies are unavailable."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from townlet.core.interfaces import PolicyBackendProtocol

if TYPE_CHECKING:  # pragma: no cover
    from townlet.dto.observations import ObservationEnvelope

logger = logging.getLogger(__name__)


class StubPolicyBackend(PolicyBackendProtocol):
    """Minimal policy backend that emits wait actions and logs capability gaps."""

    def __init__(self, config: Any | None = None, backend: Any | None = None) -> None:
        self.config = config
        self.backend = backend
        logger.warning("policy_backend_stub_active provider=stub message='PyTorch extras missing; scripted decisions only.'")
        self._reset_callback: Any | None = None

    def register_ctx_reset_callback(self, callback: Any | None) -> None:
        self._reset_callback = callback

    def enable_anneal_blend(self, enabled: bool) -> None:
        _ = enabled

    def set_anneal_ratio(self, ratio: float | None) -> None:
        _ = ratio

    def reset_state(self) -> None:
        return None

    def supports_observation_envelope(self) -> bool:
        """Stub backend tolerates envelopes but does not require them."""

        return True

    def decide(
        self,
        world: Any,
        tick: int,
        *,
        envelope: ObservationEnvelope,
    ) -> Mapping[str, object]:
        _ = world, tick, envelope
        return {}

    def post_step(self, rewards: Mapping[str, float], terminated: Mapping[str, bool]) -> None:
        _ = rewards, terminated

    def flush_transitions(
        self,
        *,
        envelope: ObservationEnvelope,
    ) -> None:
        _ = envelope

    def latest_policy_snapshot(self) -> Mapping[str, Mapping[str, object]]:
        return {}

    def possessed_agents(self) -> list[str]:
        return []

    def consume_option_switch_counts(self) -> Mapping[str, int]:
        return {}

    def active_policy_hash(self) -> str | None:
        return None

    def current_anneal_ratio(self) -> float | None:
        return None


def is_stub_policy(policy: PolicyBackendProtocol, provider: str | None = None) -> bool:
    """Check if a policy backend is a stub implementation.

    Args:
        policy: Policy backend to check
        provider: Optional provider name hint

    Returns:
        True if policy is a stub backend
    """
    # Check if policy is directly a stub
    if isinstance(policy, StubPolicyBackend):
        return True
    # Check if policy is an adapter wrapping a stub backend
    backend = getattr(policy, "_backend", None)
    if backend is not None and isinstance(backend, StubPolicyBackend):
        return True
    # Check if provider name indicates stub
    if provider is None:
        return False
    return provider == "stub"

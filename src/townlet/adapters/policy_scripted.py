"""Adapter wiring the scripted policy backend to the policy port."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import TYPE_CHECKING, Any

from townlet.core.interfaces import PolicyBackendProtocol
from townlet.ports.policy import PolicyBackend

if TYPE_CHECKING:  # pragma: no cover
    from townlet.world.dto.observation import ObservationEnvelope


class ScriptedPolicyAdapter(PolicyBackend):
    """Adapter forwarding decisions to the scripted policy runtime."""

    def __init__(
        self,
        backend: PolicyBackendProtocol,
    ) -> None:
        self._backend = backend
        self._tick: int = 0
        self._world_provider: Callable[[], Any] | None = None

    def on_episode_start(self, agent_ids: Iterable[str]) -> None:  # pragma: no cover - thin bridge
        _ = agent_ids
        self._backend.reset_state()
        self._tick = 0

    def supports_observation_envelope(self) -> bool:
        """Expose DTO envelope support expected by the policy controller."""

        return True

    def decide(
        self,
        *,
        tick: int,
        envelope: ObservationEnvelope,
    ) -> Mapping[str, Any]:
        if self._world_provider is None:
            raise RuntimeError("Policy adapter world provider not configured")
        world = self._world_provider()
        actions = self._backend.decide(
            world,
            tick,
            envelope=envelope,
        )
        self._tick = tick + 1
        return actions

    def on_episode_end(self) -> None:  # pragma: no cover - thin bridge
        envelope = getattr(self._backend, "latest_envelope", None)
        if callable(envelope):
            latest = envelope()
            if latest is not None:
                self._backend.flush_transitions(envelope=latest)

    def flush_transitions(
        self,
        *,
        envelope: ObservationEnvelope,
    ) -> Mapping[str, object] | list[dict[str, object]] | None:
        return self._backend.flush_transitions(envelope=envelope)

    def attach_world(self, provider: Callable[[], Any]) -> None:
        """Transitional hook for legacy paths that still expect world access."""

        self._world_provider = provider


__all__ = ["ScriptedPolicyAdapter"]

"""Facade that centralises interactions with the legacy policy backend."""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable, Mapping
from typing import Any, TYPE_CHECKING

from townlet.core.interfaces import PolicyBackendProtocol
from townlet.ports.policy import PolicyBackend

if TYPE_CHECKING:  # pragma: no cover
    from townlet.world.dto.observation import ObservationEnvelope


logger = logging.getLogger(__name__)


class PolicyController:
    """Transitional facade that keeps SimulationLoop decoupled from PolicyRuntime."""

    def __init__(self, *, backend: PolicyBackendProtocol, port: PolicyBackend) -> None:
        self._backend = backend
        self._port = port
        self._world_supplier: Callable[[], Any] | None = None
        self._legacy_observation_warning_emitted = False
        self._attach_world_supplier()

    # ------------------------------------------------------------------
    # Lifetime & environment wiring
    # ------------------------------------------------------------------
    def bind_world_supplier(self, supplier: Callable[[], Any]) -> None:
        """Provide a callable that returns the current world view."""

        self._world_supplier = supplier
        self._attach_world_supplier()

    def register_ctx_reset_callback(self, callback: Callable[[str], None] | None) -> None:
        self._backend.register_ctx_reset_callback(callback)

    def enable_anneal_blend(self, enabled: bool) -> None:
        if hasattr(self._backend, "enable_anneal_blend"):
            self._backend.enable_anneal_blend(enabled)

    def set_anneal_ratio(self, ratio: float | None) -> None:
        self._backend.set_anneal_ratio(ratio)

    def reset_state(self) -> None:
        self._backend.reset_state()

    # ------------------------------------------------------------------
    # Decision loop
    # ------------------------------------------------------------------
    def on_episode_start(self, agent_ids: Iterable[str]) -> None:
        self._port.on_episode_start(agent_ids)

    def decide(
        self,
        world: Any,
        tick: int,
        *,
        observations: Mapping[str, Any] | None = None,
        envelope: "ObservationEnvelope | None" = None,
    ) -> Mapping[str, Any]:
        """Return policy actions for the given world/tick."""

        if envelope is None:
            latest = getattr(self._backend, "latest_envelope", None)
            if callable(latest):
                envelope = latest()
        if envelope is None:
            raise RuntimeError(
                "PolicyController.decide requires an observation DTO envelope; "
                "ensure SimulationLoop prepared the Stage 3 DTO payload.",
            )

        if observations and not self._legacy_observation_warning_emitted:
            logger.warning(
                "PolicyController received legacy observation batches alongside DTO "
                "envelopes; this compatibility path will be removed during WP3C Stage 5.",
            )
            self._legacy_observation_warning_emitted = True

        payload = observations or {}
        try:
            return self._port.decide(payload, tick=tick, envelope=envelope)
        except TypeError as exc:  # pragma: no cover - transitional fallback
            raise RuntimeError(
                "Policy backend must accept DTO envelopes. Update the policy provider "
                "to match the Stage 3 contract."
            ) from exc

    def post_step(self, rewards: Mapping[str, float], terminated: Mapping[str, bool]) -> None:
        self._backend.post_step(rewards, terminated)

    def flush_transitions(
        self,
        observations: Mapping[str, object],
        *,
        envelope: "ObservationEnvelope | None" = None,
    ) -> Mapping[str, object] | list[dict[str, object]] | None:
        return self._backend.flush_transitions(observations, envelope=envelope)

    # ------------------------------------------------------------------
    # Diagnostics / telemetry helpers
    # ------------------------------------------------------------------
    def latest_policy_snapshot(self) -> Mapping[str, Mapping[str, object]]:
        return self._backend.latest_policy_snapshot()

    def possessed_agents(self) -> list[str]:
        return self._backend.possessed_agents()

    def consume_option_switch_counts(self) -> Mapping[str, int]:
        return self._backend.consume_option_switch_counts()

    def active_policy_hash(self) -> str | None:
        return self._backend.active_policy_hash()

    def current_anneal_ratio(self) -> float | None:
        return self._backend.current_anneal_ratio()

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------
    @property
    def backend(self) -> PolicyBackendProtocol:
        return self._backend

    @property
    def port(self) -> PolicyBackend:
        return self._port

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _attach_world_supplier(self) -> None:
        attach = getattr(self._port, "attach_world", None)
        if callable(attach) and self._world_supplier is not None:
            attach(self._world_supplier)


__all__ = ["PolicyController"]

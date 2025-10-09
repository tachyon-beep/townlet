"""Facade that centralises interactions with the legacy policy backend."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from townlet.ports.policy import PolicyBackend
from townlet.policy.runner import PolicyRuntime


class PolicyController:
    """Transitional facade that keeps SimulationLoop decoupled from PolicyRuntime."""

    def __init__(self, *, backend: PolicyRuntime, port: PolicyBackend) -> None:
        self._backend = backend
        self._port = port
        self._world_supplier: Callable[[], Any] | None = None
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

    def decide(self, world: Any, tick: int) -> Mapping[str, Any]:
        """Return policy actions for the given world/tick."""

        # For now defer to the legacy backend; future revisions will rely on the port.
        return self._backend.decide(world, tick)

    def post_step(self, rewards: Mapping[str, float], terminated: Mapping[str, bool]) -> None:
        self._backend.post_step(rewards, terminated)

    def flush_transitions(self, observations: Mapping[str, object]) -> None:
        self._backend.flush_transitions(observations)

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
    def backend(self) -> PolicyRuntime:
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

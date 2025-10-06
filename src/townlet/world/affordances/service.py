"""Affordance runtime service extracted from WorldState."""

from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from .runtime import AffordanceCoordinator
from .core import (
    AffordanceEnvironment,
    AffordanceRuntimeContext,
    DefaultAffordanceRuntime,
    HookPayload,
    RunningAffordanceState,
    build_hook_payload,
)


@dataclass
class AffordanceRuntimeService:
    """Coordinates affordance runtime, hooks, and reservations for a world."""

    environment: AffordanceEnvironment
    context: AffordanceRuntimeContext
    coordinator: AffordanceCoordinator
    hook_registry: Any

    # ------------------------------------------------------------------
    # Hook management
    # ------------------------------------------------------------------
    def register_hook(self, name: str, handler) -> None:
        self.hook_registry.register(name, handler)

    def clear_hooks(self, name: str | None = None) -> None:
        self.hook_registry.clear(name)

    def handlers_for(self, hook_name: str) -> tuple:
        return self.hook_registry.handlers_for(hook_name)

    # ------------------------------------------------------------------
    # Runtime accessors
    # ------------------------------------------------------------------
    def runtime(self) -> DefaultAffordanceRuntime:
        return self.coordinator.runtime

    def running_snapshot(self) -> dict[str, RunningAffordanceState]:
        return self.coordinator.running_snapshot()

    def remove_agent(self, agent_id: str) -> None:
        self.coordinator.remove_agent(agent_id)

    def resolve(self, tick: int) -> None:
        self.coordinator.resolve(tick=tick)

    def start(
        self,
        agent_id: str,
        object_id: str,
        affordance_id: str,
        *,
        tick: int,
    ) -> tuple[bool, dict[str, Any]]:
        return self.coordinator.start(agent_id, object_id, affordance_id, tick=tick)

    def release(
        self,
        agent_id: str,
        object_id: str,
        *,
        success: bool,
        reason: str | None,
        requested_affordance_id: str | None,
        tick: int,
    ) -> tuple[str | None, dict[str, Any]]:
        return self.coordinator.release(
            agent_id,
            object_id,
            success=success,
            reason=reason,
            requested_affordance_id=requested_affordance_id,
            tick=tick,
        )

    def handle_blocked(self, object_id: str, tick: int) -> None:
        self.coordinator.handle_blocked(object_id, tick)

    # ------------------------------------------------------------------
    # Hook invocation helper
    # ------------------------------------------------------------------
    def dispatch_hooks(
        self,
        stage: str,
        hook_names: Iterable[str],
        *,
        agent_id: str,
        object_id: str,
        spec,
        extra: Mapping[str, Any] | None = None,
        debug_enabled: bool = False,
    ) -> bool:
        continue_execution = True
        for hook_name in hook_names:
            handlers = self.hook_registry.handlers_for(hook_name)
            if not handlers:
                continue
            hook_timer = None
            if debug_enabled:
                import time

                hook_timer = time.perf_counter()
            base_payload: HookPayload = build_hook_payload(
                stage=stage,
                hook=hook_name,
                tick=self.environment.tick_supplier(),
                agent_id=agent_id,
                object_id=object_id,
                affordance_id=spec.affordance_id if spec else None,
                environment=self.environment,
                spec=spec,
                extra=extra,
            )
            for handler in handlers:
                try:
                    result = handler(base_payload)
                    if result is False:
                        continue_execution = False
                except Exception:  # pragma: no cover - defensive logging
                    logging.getLogger(__name__).exception(
                        "affordance_hook_failed hook=%s agent=%s object=%s",
                        hook_name,
                        agent_id,
                        object_id,
                    )

            if base_payload.get("cancel"):
                continue_execution = False
            if hook_timer is not None:
                duration = (time.perf_counter() - hook_timer) * 1000
                logging.getLogger(__name__).debug(
                    "affordance_hook_duration hook=%s ms=%.3f",
                    hook_name,
                    duration,
                )
        return continue_execution

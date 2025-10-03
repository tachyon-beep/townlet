"""Stub affordance runtime implementations used by tests."""
from __future__ import annotations

from typing import Any, Mapping

from townlet.world.affordances import AffordanceRuntimeContext


class StubAffordanceRuntime:
    """Minimal affordance runtime used for testing configuration plumbing."""

    def __init__(
        self,
        context: AffordanceRuntimeContext,
        *,
        instrumentation: str = "off",
        options: Mapping[str, object] | None = None,
    ) -> None:
        self.context = context
        self.instrumentation_level = instrumentation
        self.options = dict(options or {})
        self.started: list[tuple[str, str, str]] = []

    def start(
        self,
        agent_id: str,
        object_id: str,
        affordance_id: str,
        *,
        tick: int,
    ) -> tuple[bool, dict[str, object]]:
        self.started.append((agent_id, object_id, affordance_id))
        return True, {}

    def release(
        self,
        agent_id: str,
        object_id: str,
        *,
        success: bool,
        reason: str | None,
        requested_affordance_id: str | None,
        tick: int,
    ) -> tuple[str | None, dict[str, object]]:
        return requested_affordance_id, {}

    def resolve(self, *, tick: int) -> None:  # pragma: no cover - intentionally empty
        return None

    def running_snapshot(self) -> dict[str, Any]:
        return {}

    def clear(self) -> None:
        self.started.clear()

    def remove_agent(self, agent_id: str) -> None:  # pragma: no cover - intentionally empty
        return None

    def handle_blocked(self, object_id: str, tick: int) -> None:  # pragma: no cover - intentionally empty
        return None


def build_runtime(
    *,
    world: Any,
    context: AffordanceRuntimeContext,
    config: Any,
) -> StubAffordanceRuntime:
    """Factory used by runtime configuration tests."""

    return StubAffordanceRuntime(
        context,
        instrumentation=getattr(config, "instrumentation", "off"),
        options=getattr(config, "options", {}),
    )

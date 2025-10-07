"""Stub policy backend used when optional ML dependencies are unavailable."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from townlet.core.interfaces import PolicyBackendProtocol

logger = logging.getLogger(__name__)


class StubPolicyBackend(PolicyBackendProtocol):
    """Minimal policy backend that emits wait actions and logs capability gaps."""

    def __init__(self, config: Any | None = None) -> None:
        self.config = config
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

    def decide(self, world: Any, tick: int) -> Mapping[str, object]:
        _ = world, tick
        return {}

    def post_step(self, rewards: Mapping[str, float], terminated: Mapping[str, bool]) -> None:
        _ = rewards, terminated

    def flush_transitions(self, observations: Mapping[str, object]) -> None:
        _ = observations

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

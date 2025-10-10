from __future__ import annotations

import pytest

from townlet.orchestration.policy import PolicyController
from townlet.core.interfaces import PolicyBackendProtocol
from townlet.ports.policy import PolicyBackend


class _BackendStub(PolicyBackendProtocol):
    def __init__(self) -> None:
        self.reset_state()

    def register_ctx_reset_callback(self, callback):  # pragma: no cover - not used
        self._reset_callback = callback

    def enable_anneal_blend(self, enabled: bool) -> None:  # pragma: no cover
        self._anneal_blend = bool(enabled)

    def set_anneal_ratio(self, ratio: float | None) -> None:  # pragma: no cover
        self._anneal_ratio = ratio

    def reset_state(self) -> None:
        self._reset_callback = None
        self._anneal_blend = False
        self._anneal_ratio = None

    def supports_observation_envelope(self) -> bool:
        return True

    def decide(self, world, tick, *, envelope):
        return {}

    def post_step(self, rewards, terminated) -> None:  # pragma: no cover
        return None

    def flush_transitions(self, *, envelope):
        return []

    def latest_policy_snapshot(self):
        return {}

    def possessed_agents(self):
        return []

    def consume_option_switch_counts(self):
        return {}

    def active_policy_hash(self):
        return None

    def current_anneal_ratio(self):
        return None

    def latest_envelope(self):  # pragma: no cover - explicit guard
        return None


class _PortStub(PolicyBackend):
    def on_episode_start(self, agent_ids):  # pragma: no cover
        self._agents = tuple(agent_ids)

    def supports_observation_envelope(self) -> bool:
        return True

    def decide(self, *, tick, envelope):
        return {}


def test_policy_controller_requires_dto_envelope() -> None:
    controller = PolicyController(backend=_BackendStub(), port=_PortStub())

    with pytest.raises(RuntimeError, match="requires an observation DTO envelope"):
        controller.decide(world=object(), tick=0, envelope=None)

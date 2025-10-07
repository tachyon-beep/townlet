"""Scripted policy adapter implementing :class:`PolicyBackend`."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from townlet.factories.registry import register
from townlet.ports.policy import PolicyBackend


class ScriptedPolicyAdapter(PolicyBackend):
    """Policy backend that emits static actions for all agents."""

    def __init__(self, action: Any | None = None) -> None:
        self._action = action if action is not None else {"kind": "wait"}
        self._agent_ids: tuple[str, ...] = ()

    def on_episode_start(self, agent_ids: Iterable[str]) -> None:
        self._agent_ids = tuple(agent_ids)

    def decide(self, observations: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self._agent_ids:
            self._agent_ids = tuple(observations.keys())
        return dict.fromkeys(self._agent_ids, self._action)

    def on_episode_end(self) -> None:
        self._agent_ids = ()


@register("policy", "scripted")
def _build_scripted_policy(**kwargs: Any) -> PolicyBackend:
    return ScriptedPolicyAdapter(**kwargs)


@register("policy", "dummy")
def _build_dummy_policy(**kwargs: Any) -> PolicyBackend:
    return ScriptedPolicyAdapter(**kwargs)

"""Factories for creating policy backend adapters."""

from __future__ import annotations

from typing import Any, Callable

from townlet.adapters.policy_scripted import ScriptedPolicyAdapter
from townlet.policy.fallback import StubPolicyBackend
from townlet.testing import DummyPolicyBackend
from townlet.policy.runner import PolicyRuntime

from .registry import register, resolve


def create_policy(provider: str = "scripted", **kwargs: Any):
    return resolve("policy", provider, **kwargs)


@register("policy", "scripted")
@register("policy", "default")
def _build_scripted_policy(
    *,
    backend: PolicyRuntime,
) -> ScriptedPolicyAdapter:
    adapter = ScriptedPolicyAdapter(backend)
    return adapter


@register("policy", "stub")
def _build_stub_policy(**kwargs: Any) -> StubPolicyBackend:
    return StubPolicyBackend(**kwargs)


@register("policy", "dummy")
def _build_dummy_policy(**kwargs: Any) -> DummyPolicyBackend:
    if kwargs:
        raise TypeError(
            "Unsupported arguments for dummy policy provider: {}".format(
                ", ".join(map(str, kwargs))
            )
        )
    return DummyPolicyBackend()


__all__ = ["create_policy"]

"""Scripted policy backend alias package.

Provides a stable import path symmetric to the PyTorch backend. The scripted
backend uses the existing `PolicyRuntime` implementation.
"""

from __future__ import annotations

from townlet.policy.runner import PolicyRuntime as ScriptedPolicyBackend

__all__ = ["ScriptedPolicyBackend"]


"""Sample hook module for tests."""

from __future__ import annotations


def register_hooks(world):
    markers = list(getattr(world, "_test_hook_markers", []))
    markers.append("sample")
    world._test_hook_markers = markers

from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop


def _load_config() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    return config


def test_config_parses_hook_allowlist_defaults():
    config = _load_config()
    runtime_cfg = config.affordances.runtime
    assert runtime_cfg.hook_allowlist == ("townlet.world.hooks.default",)
    assert runtime_cfg.allow_env_hooks is True


def test_hook_allowlist_allows_custom_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("TOWNLET_AFFORDANCE_HOOK_MODULES", raising=False)
    config = _load_config()
    config.affordances.runtime.hook_allowlist = (
        "townlet.world.hooks.default",
        "tests.hooks.sample",
    )
    loop = SimulationLoop(config)
    world = loop.world
    assert "tests.hooks.sample" in world.loaded_hook_modules
    assert hasattr(world, "_test_hook_markers")
    assert "sample" in world._test_hook_markers


def test_env_module_not_in_allowlist_rejected(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TOWNLET_AFFORDANCE_HOOK_MODULES", "tests.hooks.sample")
    config = _load_config()
    config.affordances.runtime.hook_allowlist = ("townlet.world.hooks.default",)
    loop = SimulationLoop(config)
    world = loop.world
    assert ("tests.hooks.sample", "not in hook_allowlist") in world.rejected_hook_modules
    assert "tests.hooks.sample" not in world.loaded_hook_modules
    assert not hasattr(world, "_test_hook_markers")


def test_env_override_disabled_records_rejection(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TOWNLET_AFFORDANCE_HOOK_MODULES", "tests.hooks.sample")
    config = _load_config()
    config.affordances.runtime.hook_allowlist = (
        "townlet.world.hooks.default",
        "tests.hooks.sample",
    )
    config.affordances.runtime.allow_env_hooks = False
    loop = SimulationLoop(config)
    world = loop.world
    assert any(
        module == "env@TOWNLET_AFFORDANCE_HOOK_MODULES" and reason == "environment overrides disabled"
        for module, reason in world.rejected_hook_modules
    )
    assert "tests.hooks.sample" in world.loaded_hook_modules
    assert hasattr(world, "_test_hook_markers")


def test_import_error_rejected(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("TOWNLET_AFFORDANCE_HOOK_MODULES", raising=False)
    config = _load_config()
    config.affordances.runtime.hook_allowlist = (
        "townlet.world.hooks.default",
        "tests.hooks.missing",
    )
    loop = SimulationLoop(config)
    world = loop.world
    assert any(
        module == "tests.hooks.missing" and reason.startswith("import_error")
        for module, reason in world.rejected_hook_modules
    )
    assert "tests.hooks.missing" not in world.loaded_hook_modules

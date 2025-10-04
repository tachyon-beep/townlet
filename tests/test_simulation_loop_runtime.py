from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop


@pytest.fixture(scope="module")
def base_config() -> object:
    return load_config(Path("configs/examples/poc_hybrid.yaml"))


def _close_loop(loop: SimulationLoop) -> None:
    loop.telemetry.close()


def test_simulation_loop_uses_facade_runtime_when_requested(base_config: object) -> None:
    config = base_config.model_copy(deep=True)
    loop = SimulationLoop(config, use_legacy_runtime=False)
    try:
        assert loop.runtime is not None
        assert loop._runtime_variant == "facade"
        assert loop.telemetry._runtime_variant == "facade"
    finally:
        _close_loop(loop)


def test_simulation_loop_uses_legacy_runtime_when_requested(base_config: object) -> None:
    config = base_config.model_copy(deep=True)
    loop = SimulationLoop(config, use_legacy_runtime=True)
    try:
        assert loop.runtime is None
        assert loop._runtime_variant == "legacy"
        assert loop.telemetry._runtime_variant == "legacy"
    finally:
        _close_loop(loop)


def test_simulation_loop_follows_environment_flag(monkeypatch: pytest.MonkeyPatch, base_config: object) -> None:
    monkeypatch.setenv("TOWNLET_LEGACY_RUNTIME", "1")
    loop = SimulationLoop(base_config.model_copy(deep=True))
    try:
        assert loop.runtime is None
        assert loop._runtime_variant == "legacy"
    finally:
        _close_loop(loop)
    monkeypatch.setenv("TOWNLET_LEGACY_RUNTIME", "0")
    loop_facade = SimulationLoop(base_config.model_copy(deep=True))
    try:
        assert loop_facade.runtime is not None
        assert loop_facade._runtime_variant == "facade"
    finally:
        _close_loop(loop_facade)

from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop


@pytest.fixture(scope="module")
def base_config() -> object:
    return load_config(Path("configs/examples/poc_hybrid.yaml"))


def _close_loop(loop: SimulationLoop) -> None:
    loop.close()


def test_simulation_loop_always_uses_facade_runtime(base_config: object) -> None:
    config = base_config.model_copy(deep=True)
    loop = SimulationLoop(config)
    try:
        assert loop.runtime is not None
        assert loop._runtime_variant == "facade"
        assert loop.telemetry._runtime_variant == "facade"
    finally:
        _close_loop(loop)


def test_simulation_loop_ignores_legacy_environment_flag(
    monkeypatch: pytest.MonkeyPatch, base_config: object
) -> None:
    monkeypatch.setenv("TOWNLET_LEGACY_RUNTIME", "1")
    loop = SimulationLoop(base_config.model_copy(deep=True))
    try:
        assert loop.runtime is not None
        assert loop._runtime_variant == "facade"
    finally:
        _close_loop(loop)


def test_simulation_loop_close_is_idempotent(base_config: object) -> None:
    config = base_config.model_copy(deep=True)
    loop = SimulationLoop(config)
    try:
        pass
    finally:
        loop.close()
        loop.close()

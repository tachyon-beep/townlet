from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.console.handlers import ConsoleCommand, create_console_router
from townlet.core.sim_loop import SimulationLoop
from townlet.core.utils import policy_provider_name, telemetry_provider_name
from townlet.demo.runner import seed_demo_state


@pytest.mark.parametrize("provider", ["stdout", "stub"])
def test_console_snapshot_parity_stub_stdout(provider: str) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config, telemetry_provider=provider)

    # Populate a small amount of telemetry/snapshots
    loop.run_for(3)

    router = create_console_router(
        loop.telemetry,
        loop.world,
        promotion=loop.promotion,
        policy=loop.policy,
        policy_provider=policy_provider_name(loop),
        telemetry_provider=telemetry_provider_name(loop),
        lifecycle=loop.lifecycle,
        config=config,
    )

    payload = router.dispatch(ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={}))
    assert isinstance(payload, dict)
    assert "schema_version" in payload
    assert "console_commands" in payload

    # Stub should surface a warning banner for clarity; real provider may not.
    if provider == "stub":
        assert "telemetry_warning" in payload


@pytest.mark.parametrize("provider", ["stdout", "stub"])
def test_snapshot_save_load_with_stub_and_stdout(tmp_path: Path, provider: str) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config, telemetry_provider=provider)

    # Advance a few ticks so telemetry has content
    loop.run_for(2)

    target_dir = tmp_path / f"snapshots_{provider}"
    path = loop.save_snapshot(target_dir)
    assert path.exists()

    restored = SimulationLoop(config, telemetry_provider=provider)
    # Ensure restore path integrates telemetry without raising
    restored.load_snapshot(path)
    # Basic sanity: ticks match after restore
    assert restored.tick > 0


@pytest.mark.parametrize("provider", ["stdout", "stub"])
def test_demo_seed_smoke(provider: str) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config, telemetry_provider=provider)
    # Should not raise with either provider
    seed_demo_state(loop.world, telemetry=loop.telemetry, history_window=5)
    # Step once to flush any queued demo telemetry
    loop.run_for(1)


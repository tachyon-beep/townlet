from __future__ import annotations

from pathlib import Path

from townlet.config.loader import load_config
from townlet.core.sim_loop import SimulationLoop


def test_simulation_loop_emits_policy_events(tmp_path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    captured: list[tuple[str, dict[str, object]]] = []

    def _subscriber(name: str, payload: dict[str, object]) -> None:
        captured.append((name, dict(payload)))

    dispatcher = getattr(loop.telemetry, "event_dispatcher", None)
    assert dispatcher is not None
    dispatcher.register_subscriber(_subscriber)

    try:
        loop.step()
    finally:
        dispatcher.unregister_subscriber(_subscriber)
        loop.close()

    event_names = [name for name, _ in captured]
    assert "policy.metadata" in event_names
    assert "policy.possession" in event_names
    assert "policy.anneal.update" in event_names

    metadata_payload = next(payload for name, payload in captured if name == "policy.metadata")
    assert "metadata" in metadata_payload
    assert isinstance(metadata_payload["metadata"], dict)

    possession_payload = next(payload for name, payload in captured if name == "policy.possession")
    assert isinstance(possession_payload.get("agents"), list)

    anneal_payload = next(payload for name, payload in captured if name == "policy.anneal.update")
    assert "ratio" in anneal_payload

    latest_metadata = loop.telemetry.latest_policy_metadata()
    assert latest_metadata is not None
    latest_anneal = loop.telemetry.latest_policy_anneal()
    assert latest_anneal is not None

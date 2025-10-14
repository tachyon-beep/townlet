from __future__ import annotations

from pathlib import Path

from townlet.config.loader import load_config
from townlet.dto.telemetry import TelemetryEventDTO, TelemetryMetadata
from townlet.telemetry.publisher import TelemetryPublisher


def test_telemetry_publisher_ingests_policy_events() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    publisher = TelemetryPublisher(config)

    metadata_payload = {
        "tick": 5,
        "provider": "scripted",
        "metadata": {
            "identity": {
                "config_id": config.config_id,
                "policy_hash": "abc123",
                "observation_variant": config.observation_variant,
                "anneal_ratio": 0.0,
            },
            "anneal_ratio": 0.0,
            "possessed_agents": ["alice"],
            "option_switch_counts": {"alice": 1},
        },
    }
    metadata_event = TelemetryEventDTO(
        event_type="policy.metadata",
        tick=5,
        payload=metadata_payload,
        metadata=TelemetryMetadata(),
    )
    publisher.emit_event(metadata_event)
    latest_metadata = publisher.latest_policy_metadata()
    assert latest_metadata is not None
    assert latest_metadata["metadata"]["anneal_ratio"] == 0.0
    identity = publisher.latest_policy_identity()
    assert identity is not None
    assert identity["policy_hash"] == "abc123"

    anneal_payload = {
        "tick": 5,
        "provider": "scripted",
        "ratio": 0.0,
        "context": {"cycle": 1, "mode": "ppo"},
    }
    anneal_event = TelemetryEventDTO(
        event_type="policy.anneal.update",
        tick=5,
        payload=anneal_payload,
        metadata=TelemetryMetadata(),
    )
    publisher.emit_event(anneal_event)
    latest_anneal = publisher.latest_policy_anneal()
    assert latest_anneal is not None
    assert latest_anneal["ratio"] == 0.0
    assert latest_anneal["context"]["cycle"] == 1

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from pytest import approx

from townlet.world.actions import Action
from townlet.world.dto import (
    DTO_SCHEMA_VERSION,
    ObservationEnvelope,
    build_observation_envelope,
)


def test_build_observation_envelope_coerces_numpy_payloads(tmp_path: Path) -> None:
    observations = {
        "alice": {
            "map": np.zeros((1, 2, 2), dtype=np.float32),
            "features": np.array([1.0, 2.0], dtype=np.float32),
            "metadata": {
                "feature_names": ["a", "b"],
                "local_summary": np.array([0.1, 0.2], dtype=np.float32),
            },
        },
        "bob": {
            "map": np.ones((1, 1, 1), dtype=np.float32),
            "features": np.array([3.0], dtype=np.float32),
            "metadata": {},
        },
    }
    rewards = {"alice": 0.5, "bob": -0.25}
    reward_breakdown = {
        "alice": {"total": 0.5, "clip_adjustment": 0.0},
        "bob": {"total": -0.25},
    }

    envelope = build_observation_envelope(
        tick=5,
        observations=observations,
        actions={
            "alice": Action(agent_id="alice", kind="move", payload={"position": (1, 2)}),
            "bob": {"kind": "noop"},
        },
        terminated={"bob": True},
        termination_reasons={"bob": "fatigue"},
        queue_metrics={"cooldown_events": 1},
        rewards=rewards,
        reward_breakdown=reward_breakdown,
        perturbations={"active": {"storm": {"duration": 10}}},
        policy_snapshot={"policy": "scripted"},
        policy_metadata={"identity": {"hash": "abc123"}, "possessed_agents": ["spectator"]},
        rivalry_events=[{"tick": 5, "agent_a": "alice", "agent_b": "bob", "intensity": np.float32(0.5)}],
        stability_metrics={"alerts": []},
        promotion_state={"window_start": 0, "window_end": 10},
        rng_seed=np.int64(7),
    )

    data = envelope.model_dump(by_alias=True)
    assert data["dto_schema_version"] == DTO_SCHEMA_VERSION
    assert [agent["agent_id"] for agent in data["agents"]] == ["alice", "bob"]
    assert isinstance(data["agents"][0]["map"], list)
    assert data["agents"][0]["features"] == [1.0, 2.0]
    assert data["agents"][0]["rewards"] == reward_breakdown["alice"]
    assert data["agents"][0]["metadata"]["local_summary"] == approx([0.1, 0.2])
    assert data["agents"][0]["position"] is None
    assert data["agents"][0]["needs"] is None
    assert data["agents"][0]["wallet"] is None
    assert data["agents"][0]["job"] is None
    assert data["agents"][0]["queue_state"] is None
    assert data["actions"]["alice"]["payload"]["position"] == [1, 2]
    assert data["terminated"]["bob"] is True
    assert data["termination_reasons"]["bob"] == "fatigue"
    assert data["global"]["queue_metrics"] == {"cooldown_events": 1}
    assert data["global"]["policy_metadata"]["identity"]["hash"] == "abc123"
    assert data["global"]["rng_seed"] == 7
    assert data["global"].get("queues") == {}
    assert data["global"].get("running_affordances") == {}
    assert data["global"].get("relationship_snapshot") == {}
    assert data["global"].get("relationship_metrics") == {}
    assert data["global"].get("employment_snapshot") == {}
    assert data["global"].get("queue_affinity_metrics") == {}
    assert data["global"].get("economy_snapshot") == {}
    assert data["global"].get("anneal_context") == {}


@pytest.mark.parametrize(
    "fixture_name",
    ["dto_example_tick.json", "dto_sample_tick.json"],
)
def test_observation_envelope_parses_reference_fixtures(fixture_name: str) -> None:
    fixture_path = Path("docs/architecture_review/WP_NOTES/WP3") / fixture_name
    payload = json.loads(fixture_path.read_text())
    envelope = ObservationEnvelope.model_validate(payload)
    serialized = envelope.model_dump(by_alias=True)
    assert serialized["dto_schema_version"] == DTO_SCHEMA_VERSION

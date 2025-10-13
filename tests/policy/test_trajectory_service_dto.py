from __future__ import annotations

from townlet.dto.observations import (
    DTO_SCHEMA_VERSION,
    AgentObservationDTO,
    GlobalObservationDTO,
    ObservationEnvelope,
)
from townlet.policy.replay import frames_to_replay_sample
from townlet.policy.trajectory_service import TrajectoryService


def test_flush_transitions_with_dto_envelope() -> None:
    service = TrajectoryService()
    service.begin_tick(42)
    action_payload = {"kind": "move", "target": (5, 5)}
    entry = service.record_action("agent_1", action_payload, action_id=3)
    assert entry["action_id"] == 3
    service.append_reward("agent_1", reward=1.5, done=False)

    agent = AgentObservationDTO(
        agent_id="agent_1",
        map=[[[0.0]]],
        features=[0.25, 0.75],
        metadata={"foo": "bar"},
        queue_state={"active": False},
        pending_intent={"kind": "move"},
    )
    envelope = ObservationEnvelope(
        tick=42,
        agents=[agent],
        global_context=GlobalObservationDTO(
            anneal_context={"ratio": 0.25},
        ),
        actions={},
        terminated={},
        termination_reasons={},
    )

    frames = service.flush_transitions(envelope=envelope)

    assert len(frames) == 1
    frame = frames[0]
    assert frame["tick"] == 42
    assert frame["agent_id"] == "agent_1"
    assert frame["map"] == agent.map
    assert frame["features"] == agent.features
    metadata = frame["metadata"]
    assert metadata["foo"] == "bar"
    dto_meta = metadata.get("dto")
    assert dto_meta is not None
    assert dto_meta["schema_version"] == DTO_SCHEMA_VERSION
    assert dto_meta["queue_state"] == {"active": False}
    assert dto_meta["pending_intent"] == {"kind": "move"}
    assert frame["anneal_context"] == {"ratio": 0.25}
    assert frame["action"] == action_payload
    assert frame["action_id"] == 3
    assert frame["rewards"] == [1.5]
    assert frame["dones"] == [False]
    assert service.transitions == {}


def test_frames_to_replay_sample_preserves_dto_metadata() -> None:
    frame = {
        "tick": 7,
        "agent_id": "agent_1",
        "map": [[[0.0]]],
        "features": [0.3, 0.7],
        "action": {"kind": "move"},
        "action_id": 2,
        "rewards": [0.5],
        "dones": [False],
        "metadata": {
            "feature_names": ["foo", "bar"],
            "dto": {
                "schema_version": DTO_SCHEMA_VERSION,
                "needs": {"hunger": 0.4},
                "wallet": 12.0,
                "queue_state": {"active": False},
            },
        },
        "anneal_context": {"ratio": 0.4},
    }

    sample = frames_to_replay_sample([frame])

    assert sample.metadata["dto"]["schema_version"] == DTO_SCHEMA_VERSION
    assert sample.metadata["dto"]["needs"]["hunger"] == 0.4
    assert sample.metadata["dto"]["wallet"] == 12.0
    assert sample.metadata["dto"]["queue_state"] == {"active": False}
    assert sample.metadata["anneal_context"] == {"ratio": 0.4}

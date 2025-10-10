from __future__ import annotations

from townlet.policy.trajectory_service import TrajectoryService
from townlet.world.dto.observation import (
    AgentObservationDTO,
    GlobalObservationDTO,
    ObservationEnvelope,
)


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

    frames = service.flush_transitions(envelope)

    assert len(frames) == 1
    frame = frames[0]
    assert frame["tick"] == 42
    assert frame["agent_id"] == "agent_1"
    assert frame["map"] == agent.map
    assert frame["features"] == agent.features
    assert frame["metadata"] == {"foo": "bar"}
    assert frame["anneal_context"] == {"ratio": 0.25}
    assert frame["action"] == action_payload
    assert frame["action_id"] == 3
    assert frame["rewards"] == [1.5]
    assert frame["dones"] == [False]
    assert service.transitions == {}

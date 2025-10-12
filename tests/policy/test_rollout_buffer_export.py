from __future__ import annotations

import json

from townlet.policy.rollout import RolloutBuffer
from townlet.policy.trajectory_service import TrajectoryService
from townlet.world.dto.observation import (
    DTO_SCHEMA_VERSION,
    AgentObservationDTO,
    GlobalObservationDTO,
    ObservationEnvelope,
)


def test_rollout_buffer_emits_dto_export(tmp_path) -> None:
    service = TrajectoryService()
    service.begin_tick(7)
    action_payload = {"kind": "move", "target": (1, 2)}
    service.record_action("agent_1", action_payload, action_id=3)
    service.append_reward("agent_1", reward=0.75, done=False)

    agent = AgentObservationDTO(
        agent_id="agent_1",
        map=[[[0.0]]],
        features=[0.4, 0.6],
        metadata={"feature_names": ["rivalry_max"]},
        needs={"hunger": 0.4},
        wallet=12.0,
        queue_state={"active": False},
    )
    envelope = ObservationEnvelope(
        tick=7,
        agents=[agent],
        global_context=GlobalObservationDTO(anneal_context={"ratio": 0.1}),
        actions={},
        terminated={},
        termination_reasons={},
    )
    frames = service.flush_transitions(envelope=envelope)

    buffer = RolloutBuffer()
    buffer.extend(frames)
    buffer.set_tick_count(1)
    buffer.save(tmp_path, prefix="rollout", compress=False)

    manifest_path = tmp_path / "rollout_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    assert manifest
    entry = manifest[0]
    dto_filename = entry["dto"]
    dto_path = tmp_path / dto_filename
    payload = json.loads(dto_path.read_text())
    assert payload["schema_version"] == DTO_SCHEMA_VERSION
    assert payload["agent_id"] == "agent_1"
    assert payload["frame_count"] == 1
    frame_payload = payload["frames"][0]
    assert frame_payload["tick"] == 7
    assert frame_payload["action"]["kind"] == action_payload["kind"]
    assert frame_payload["action"]["target"] == [1, 2]
    metadata = frame_payload["metadata"]["dto"]
    assert metadata["needs"]["hunger"] == 0.4
    assert metadata["wallet"] == 12.0
    assert metadata["queue_state"] == {"active": False}

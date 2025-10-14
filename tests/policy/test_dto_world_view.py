from __future__ import annotations

from townlet.dto.observations import ObservationEnvelope
from townlet.policy.dto_view import DTOWorldView


def _make_view() -> tuple[DTOWorldView, list[tuple[str, dict[str, object]]]]:
    envelope = ObservationEnvelope(tick=0)
    captured: list[tuple[str, dict[str, object]]] = []

    def emitter(name: str, payload: dict[str, object]) -> None:
        captured.append((name, dict(payload)))

    view = DTOWorldView(
        envelope=envelope,
        world=None,
        guardrail_emitter=emitter,
    )
    return view, captured


def test_record_chat_failure_emits_guardrail_request() -> None:
    view, captured = _make_view()

    view.record_chat_failure("alice", "bob")

    assert captured
    name, payload = captured[0]
    assert name == "policy.guardrail.request"
    assert payload["variant"] == "chat_failure"
    assert payload["speaker"] == "alice"
    assert payload["listener"] == "bob"


def test_record_relationship_guard_block_emits_guardrail_request() -> None:
    view, captured = _make_view()

    view.record_relationship_guard_block(
        agent_id="alice",
        reason="queue_rival",
        object_id="fridge_1",
    )

    assert captured
    name, payload = captured[-1]
    assert name == "policy.guardrail.request"
    assert payload["variant"] == "relationship_block"
    assert payload["agent_id"] == "alice"
    assert payload["reason"] == "queue_rival"
    assert payload["object_id"] == "fridge_1"

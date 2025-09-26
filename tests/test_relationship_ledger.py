from __future__ import annotations

from townlet.world.relationships import RelationshipLedger, RelationshipParameters


def test_apply_delta_clamps_and_prunes() -> None:
    params = RelationshipParameters(max_edges=2)
    ledger = RelationshipLedger(params=params)
    ledger.apply_delta("bob", trust=0.8, familiarity=0.2)
    ledger.apply_delta("carol", rivalry=0.4)
    ledger.apply_delta("dave", trust=0.9)

    snapshot = ledger.snapshot()
    assert len(snapshot) == 2
    assert "dave" in snapshot
    assert snapshot["dave"]["trust"] <= 1.0


def test_decay_removes_zero_ties() -> None:
    params = RelationshipParameters(max_edges=3, trust_decay=0.5, familiarity_decay=0.5, rivalry_decay=0.5)
    ledger = RelationshipLedger(params=params)
    ledger.apply_delta("bob", trust=0.4)
    ledger.apply_delta("carol", rivalry=0.4)
    ledger.decay()
    snapshot = ledger.snapshot()
    assert snapshot == {}


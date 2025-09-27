import pytest

from townlet.world.rivalry import RivalryLedger, RivalryParameters


def test_increment_and_clamp_and_eviction() -> None:
    params = RivalryParameters(increment_per_conflict=0.6, max_edges=2, max_value=1.0)
    ledger = RivalryLedger(owner_id="alice", params=params)

    ledger.apply_conflict("bob", intensity=1.0)
    ledger.apply_conflict("cara", intensity=1.0)
    ledger.apply_conflict("dave", intensity=1.0)

    snapshot = ledger.snapshot()
    assert len(snapshot) == 2
    assert max(snapshot.values()) <= params.max_value
    assert set(snapshot) <= {"bob", "cara", "dave"}


def test_decay_and_eviction_threshold() -> None:
    params = RivalryParameters(decay_per_tick=0.2, eviction_threshold=0.1)
    ledger = RivalryLedger(owner_id="alice", params=params)
    ledger.inject([("bob", 0.5), ("cara", 0.3)])

    ledger.decay(ticks=1)
    assert ledger.score_for("bob") == pytest.approx(0.3)
    # `cara` should fall to the eviction threshold and be removed
    assert ledger.score_for("cara") == 0.0
    assert "cara" not in ledger.snapshot()


def test_should_avoid_toggle() -> None:
    params = RivalryParameters(avoid_threshold=0.4)
    ledger = RivalryLedger(owner_id="alice", params=params)
    ledger.inject([("bob", 0.35)])
    assert ledger.should_avoid("bob") is False
    ledger.apply_conflict("bob", intensity=1.0)
    assert ledger.should_avoid("bob") is True

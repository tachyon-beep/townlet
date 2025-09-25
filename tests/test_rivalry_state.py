from __future__ import annotations

from townlet.world.rivalry import RivalryLedger, RivalryParameters


def test_apply_conflict_clamps_to_max() -> None:
    params = RivalryParameters(max_value=0.5, increment_per_conflict=0.4)
    ledger = RivalryLedger(params=params)

    value = ledger.apply_conflict("bob")
    assert value == 0.4

    value = ledger.apply_conflict("bob")
    assert value == 0.5  # clamped to max


def test_decay_evicts_low_scores() -> None:
    params = RivalryParameters(decay_per_tick=0.1, eviction_threshold=0.05)
    ledger = RivalryLedger(params=params)
    ledger.apply_conflict("bob")
    ledger.decay(ticks=5)
    assert ledger.score_for("bob") == 0.0
    assert ledger.snapshot() == {}


def test_should_avoid_threshold() -> None:
    params = RivalryParameters(avoid_threshold=0.6, increment_per_conflict=0.3)
    ledger = RivalryLedger(params=params)
    ledger.apply_conflict("bob")
    assert ledger.should_avoid("bob") is False
    ledger.apply_conflict("bob")
    assert ledger.should_avoid("bob") is True


def test_encode_features_fixed_width() -> None:
    params = RivalryParameters()
    ledger = RivalryLedger(params=params)
    ledger.inject([("bob", 0.3), ("charlie", 0.7), ("dana", 0.2)])
    features = ledger.encode_features(limit=3)
    assert features == [0.7, 0.3, 0.2]

    padded = ledger.encode_features(limit=5)
    assert padded == [0.7, 0.3, 0.2, 0.0, 0.0]

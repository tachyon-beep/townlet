from __future__ import annotations

import random

import pytest

from townlet.utils import decode_rng_state, encode_rng_state


def test_encode_decode_rng_state_round_trip() -> None:
    rng = random.Random(1234)
    original_state = rng.getstate()

    payload = encode_rng_state(original_state)
    decoded_state = decode_rng_state(payload)

    assert decoded_state == original_state


def test_decode_rng_state_invalid_payload() -> None:
    with pytest.raises(Exception):
        decode_rng_state("not-base64!")

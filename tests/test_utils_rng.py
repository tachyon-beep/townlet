from __future__ import annotations

import random
from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.utils import decode_rng_state, encode_rng_state

BASE_CONFIG = Path("configs/examples/poc_hybrid.yaml")


def test_encode_decode_rng_state_round_trip() -> None:
    rng = random.Random(1234)
    original_state = rng.getstate()

    payload = encode_rng_state(original_state)
    decoded_state = decode_rng_state(payload)

    assert decoded_state == original_state


def test_decode_rng_state_invalid_payload() -> None:
    with pytest.raises(Exception):
        decode_rng_state("not-base64!")


def test_world_rng_state_round_trip() -> None:
    config = load_config(BASE_CONFIG)
    loop = SimulationLoop(config)

    original_state = loop.world.get_rng_state()
    first_value = loop.world.rng.random()
    # Mutate RNG then restore the captured state.
    _ = loop.world.rng.random()

    loop.world.set_rng_state(original_state)
    repeat_value = loop.world.rng.random()

    assert first_value == repeat_value

"""Utility helpers for serialising deterministic RNG state."""

from __future__ import annotations

import base64
import pickle
import random


def encode_rng_state(state: tuple[object, ...]) -> str:
    """Encode a Python ``random`` state tuple into a base64 string."""

    return base64.b64encode(pickle.dumps(state)).decode("ascii")


def decode_rng_state(payload: str) -> tuple[object, ...]:
    """Decode a base64-encoded RNG state back into a Python tuple."""

    state = pickle.loads(base64.b64decode(payload.encode("ascii")))
    if not isinstance(state, tuple):
        raise TypeError("decoded RNG state must be a tuple")
    return tuple(state)


def encode_rng(rng: random.Random) -> str:
    """Capture the current state of ``rng`` as a serialisable string."""

    return encode_rng_state(rng.getstate())

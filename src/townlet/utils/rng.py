"""Utility helpers for serialising deterministic RNG state."""

from __future__ import annotations

import base64
import pickle
import random
from typing import Tuple


def encode_rng_state(state: Tuple[object, ...]) -> str:
    """Encode a Python ``random`` state tuple into a base64 string."""

    return base64.b64encode(pickle.dumps(state)).decode("ascii")


def decode_rng_state(payload: str) -> Tuple[object, ...]:
    """Decode a base64-encoded RNG state back into a Python tuple."""

    return pickle.loads(base64.b64decode(payload.encode("ascii")))


def encode_rng(rng: random.Random) -> str:
    """Capture the current state of ``rng`` as a serialisable string."""

    return encode_rng_state(rng.getstate())

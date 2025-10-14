"""Utility helpers for serialising deterministic RNG state."""

from __future__ import annotations

import json
import random


def encode_rng_state(state: tuple[object, ...]) -> str:
    """Encode a Python ``random`` state tuple into a JSON string.

    Python's RNG state is a 3-tuple: (version, inner_state, gauss_next)
    - version: int (MT19937 version, typically 3)
    - inner_state: tuple of 625 integers
    - gauss_next: float | None (cached Gaussian value)

    This encodes to JSON as: {"v": version, "s": [int...], "g": float | null}
    """
    if not isinstance(state, tuple) or len(state) != 3:
        raise TypeError(f"RNG state must be 3-tuple, got {type(state)}")

    version, inner_state, gauss_next = state

    if not isinstance(version, int):
        raise TypeError(f"RNG state version must be int, got {type(version)}")
    if not isinstance(inner_state, tuple):
        raise TypeError(f"RNG inner state must be tuple, got {type(inner_state)}")

    # Convert inner state to list for JSON serialization
    inner_list = [int(x) for x in inner_state]

    # Build compact JSON representation
    # gauss_next is float | None in Python's RNG state
    gauss_value: float | None = None
    if gauss_next is not None:
        if not isinstance(gauss_next, (int, float)):
            raise TypeError(f"RNG gauss_next must be float, got {type(gauss_next)}")
        gauss_value = float(gauss_next)

    payload = {
        "v": version,
        "s": inner_list,
        "g": gauss_value,
    }

    return json.dumps(payload, separators=(",", ":"))


def decode_rng_state(payload: str) -> tuple[object, ...]:
    """Decode a JSON-encoded RNG state back into a Python tuple.

    Accepts JSON format: {"v": int, "s": [int...], "g": float | null}
    Returns: (version, tuple(inner_state), gauss_next)
    """
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in RNG state payload: {exc}") from exc

    if not isinstance(data, dict):
        raise TypeError(f"RNG state payload must be JSON object, got {type(data)}")

    version = data.get("v")
    inner_list = data.get("s")
    gauss_next = data.get("g")

    if not isinstance(version, int):
        raise TypeError(f"RNG version must be int, got {type(version)}")
    if not isinstance(inner_list, list):
        raise TypeError(f"RNG inner state must be list, got {type(inner_list)}")

    # Convert list back to tuple for Python's RNG
    inner_state = tuple(int(x) for x in inner_list)

    return (version, inner_state, gauss_next)


def encode_rng(rng: random.Random) -> str:
    """Capture the current state of ``rng`` as a serialisable JSON string."""

    return encode_rng_state(rng.getstate())

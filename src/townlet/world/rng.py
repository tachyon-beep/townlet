"""Random number helpers (skeleton)."""

from __future__ import annotations

import random
from typing import Optional


def make(seed: Optional[int] = None) -> random.Random:
    """Return a seeded PRNG instance."""

    return random.Random(seed)


__all__ = ["make"]

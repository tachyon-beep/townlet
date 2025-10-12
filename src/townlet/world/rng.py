"""Random number helpers providing named deterministic streams."""

from __future__ import annotations

import hashlib
import pickle
import random
from dataclasses import dataclass, field
from typing import Any


def make(seed: int | None = None) -> random.Random:
    """Return a seeded PRNG instance."""

    return random.Random(seed)


@dataclass(slots=True)
class RngStreamManager:
    """Manage deterministic RNG streams keyed by name."""

    base_seed: int
    _streams: dict[str, random.Random] = field(default_factory=dict, init=False, repr=False)

    @classmethod
    def from_seed(cls, seed: int | None) -> RngStreamManager:
        if seed is None:
            seed = random.randrange(0, 2**63)
        return cls(base_seed=int(seed))

    def seed(self, seed: int) -> None:
        """Reset the manager with a new base seed, clearing derived streams."""

        self.base_seed = int(seed)
        self._streams.clear()

    def stream(self, name: str) -> random.Random:
        """Return (and lazily create) the RNG stream for ``name``."""

        if name not in self._streams:
            self._streams[name] = random.Random(self._derive_seed(name))
        return self._streams[name]

    def _derive_seed(self, name: str) -> int:
        data = f"{self.base_seed}:{name}".encode("utf-8", "strict")
        digest = hashlib.sha256(data).digest()
        return int.from_bytes(digest[:8], "big", signed=False)


def seed_from_state(state: tuple[Any, ...]) -> int:
    """Derive a deterministic seed from a Python RNG state tuple."""

    def _normalise(obj: Any) -> Any:
        if isinstance(obj, tuple):
            return tuple(_normalise(item) for item in obj)
        if isinstance(obj, list):
            return tuple(_normalise(item) for item in obj)
        return obj

    normalised = _normalise(state)
    payload = repr(normalised).encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


__all__ = ["RngStreamManager", "make", "seed_from_state"]

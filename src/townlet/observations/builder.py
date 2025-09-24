"""Observation encoding across variants."""
from __future__ import annotations

from typing import Dict, TYPE_CHECKING

from townlet.config import ObservationVariant, SimulationConfig

if TYPE_CHECKING:
    from townlet.world.grid import WorldState


class ObservationBuilder:
    """Constructs per-agent observation payloads."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.variant: ObservationVariant = config.observation_variant

    def build_batch(self, world: "WorldState", terminated: Dict[str, bool]) -> Dict[str, Dict[str, float]]:
        """Return a mapping from agent_id to an observation tensor-like payload."""
        observations: Dict[str, Dict[str, float]] = {}
        for agent_id, snapshot in world.snapshot().items():
            slot = world.embedding_allocator.allocate(agent_id, world.tick)
            observations[agent_id] = self._build_single(snapshot, slot)
            if terminated.get(agent_id):
                observations[agent_id]["ctx_reset_flag"] = 1.0
                world.embedding_allocator.release(agent_id, world.tick)
        return observations

    def _build_single(self, snapshot: object, slot: int) -> Dict[str, float]:
        # TODO(@townlet): Emit real tensors per variant.
        return {
            "variant": {"full": 0.0, "hybrid": 0.5, "compact": 1.0}[self.variant],
            "embedding_slot": float(slot),
        }

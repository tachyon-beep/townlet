"""Golden tests for RNG determinism.

These tests verify that loading a baseline snapshot and advancing N ticks
produces the same world state every time. They serve as the safety net for
RNG migration in WP5 Phase 1.1.

IMPORTANT: These tests MUST pass with the current pickle-based RNG implementation
before starting the JSON migration. Any failures after migration indicate
determinism was broken.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop


# Test fixtures use baseline snapshots from Phase 0.1
BASELINE_SNAPSHOTS = Path("tests/fixtures/baselines/snapshots")


def compute_world_hash(loop: SimulationLoop) -> str:
    """Compute a deterministic hash of the world state.

    This captures:
    - Agent positions and needs
    - Object states
    - Tick counter
    - Economy settings
    """
    state = {
        "tick": loop.tick,
        "agents": {
            agent_id: {
                "position": (agent.x, agent.y),
                "needs": {
                    "hunger": agent.hunger,
                    "hygiene": agent.hygiene,
                    "energy": agent.energy,
                },
                "cash": agent.cash,
            }
            for agent_id, agent in loop.world.agents.items()
        },
    }

    # Serialize to JSON for consistent hashing
    serialized = json.dumps(state, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()


class TestRNGDeterminism:
    """Test suite for RNG deterministic replay."""

    def test_rng_determinism_from_tick_10(self) -> None:
        """Golden test: Load snapshot at tick 10, advance 10 ticks, verify hash."""
        config = load_config(Path("configs/examples/poc_hybrid.yaml"))
        loop = SimulationLoop(config)
        loop.load_snapshot(BASELINE_SNAPSHOTS / "snapshot-10.json")

        assert loop.tick == 10, "Snapshot should restore to tick 10"

        # Advance 10 ticks
        for _ in range(10):
            loop.step()

        # Compute world hash
        world_hash = compute_world_hash(loop)

        
        expected_hash = "4784f575921386e00e1b1ad819404adb92b1c780681755355be1c59246a077c3"  
        assert world_hash == expected_hash, f"RNG determinism broken! Expected {expected_hash}, got {world_hash}"



    def test_rng_determinism_from_tick_25(self) -> None:
        """Golden test: Load snapshot at tick 25, advance 15 ticks, verify hash."""
        config = load_config(Path("configs/examples/poc_hybrid.yaml"))
        loop = SimulationLoop(config)
        loop.load_snapshot(BASELINE_SNAPSHOTS / "snapshot-25.json")

        assert loop.tick == 25

        for _ in range(15):
            loop.step()

        world_hash = compute_world_hash(loop)
        expected_hash = "0303d5aa35f6cba9337801e4d31bf2efdbe419e02fa175bed6d22eaceaf7975c"  
        assert world_hash == expected_hash, f"RNG determinism broken! Expected {expected_hash}, got {world_hash}"



    def test_rng_determinism_from_tick_50(self) -> None:
        """Golden test: Load snapshot at tick 50, advance 20 ticks, verify hash."""
        config = load_config(Path("configs/examples/poc_hybrid.yaml"))
        loop = SimulationLoop(config)
        loop.load_snapshot(BASELINE_SNAPSHOTS / "snapshot-50.json")

        assert loop.tick == 50

        for _ in range(20):
            loop.step()

        world_hash = compute_world_hash(loop)
        expected_hash = "dac1476dfec0e2ae01af720e33fa87a08d2249db89a8d63ca4776a0b5ba6e2e7"  
        assert world_hash == expected_hash, f"RNG determinism broken! Expected {expected_hash}, got {world_hash}"



    def test_rng_streams_are_independent(self) -> None:
        """Verify the three RNG streams produce different sequences (different seeds)."""
        config = load_config(Path("configs/examples/poc_hybrid.yaml"))
        loop = SimulationLoop(config)
        
        # The three RNG streams should have different states (seeded differently)
        world_state = loop._rng_world.getstate()
        events_state = loop._rng_events.getstate()
        policy_state = loop._rng_policy.getstate()
        
        # They should all be different from each other
        assert world_state != events_state, "World and Events RNG should have different states"
        assert world_state != policy_state, "World and Policy RNG should have different states"
        assert events_state != policy_state, "Events and Policy RNG should have different states"
        
        # Generate samples from each to verify they produce different sequences
        world_samples = [loop._rng_world.random() for _ in range(5)]
        events_samples = [loop._rng_events.random() for _ in range(5)]
        policy_samples = [loop._rng_policy.random() for _ in range(5)]
        
        # All three sequences should be different
        assert world_samples != events_samples, "World and Events RNG should produce different sequences"
        assert world_samples != policy_samples, "World and Policy RNG should produce different sequences"
        assert events_samples != policy_samples, "Events and Policy RNG should produce different sequences"

    def test_rng_determinism_repeated_replay(self) -> None:
        """Verify replaying the same snapshot twice produces identical results."""
        config = load_config(Path("configs/examples/poc_hybrid.yaml"))

        # First replay
        loop1 = SimulationLoop(config)
        loop1.load_snapshot(BASELINE_SNAPSHOTS / "snapshot-10.json")
        for _ in range(10):
            loop1.step()
        hash1 = compute_world_hash(loop1)

        # Second replay
        loop2 = SimulationLoop(config)
        loop2.load_snapshot(BASELINE_SNAPSHOTS / "snapshot-10.json")
        for _ in range(10):
            loop2.step()
        hash2 = compute_world_hash(loop2)

        # Hashes must be identical
        assert hash1 == hash2, f"Repeated replay must be deterministic! {hash1} != {hash2}"

    def test_rng_state_serialization_roundtrip(self) -> None:
        """Verify RNG state survives encode→decode roundtrip."""
        from townlet.utils.rng import decode_rng_state, encode_rng_state

        config = load_config(Path("configs/examples/poc_hybrid.yaml"))
        loop = SimulationLoop(config)

        # Get initial state
        original_state = loop._rng_world.getstate()

        # Encode → Decode
        encoded = encode_rng_state(original_state)
        decoded = decode_rng_state(encoded)

        # States should be identical
        assert decoded == original_state, "RNG state must survive encode/decode roundtrip"

        # Using decoded state should produce same random numbers
        rng1 = loop._rng_world
        rng2 = loop._rng_events  # Use different RNG for comparison

        rng2.setstate(decoded)

        # Both should produce same sequence
        samples1 = [rng1.random() for _ in range(10)]
        samples2 = [rng2.random() for _ in range(10)]

        assert samples1 == samples2, "RNG with restored state must produce identical sequence"

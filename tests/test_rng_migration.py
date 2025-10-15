"""JSON RNG implementation verification tests.

These tests verify that the JSON-based RNG encoding/decoding implementation
works correctly and preserves determinism.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop


BASELINE_SNAPSHOTS = Path("tests/fixtures/baselines/snapshots")


def compute_world_hash(loop: SimulationLoop) -> str:
    """Compute deterministic hash of world state."""
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

    serialized = json.dumps(state, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()


class TestRNGMigration:
    """Acceptance tests for JSON-based RNG migration."""

    def test_json_rng_encode_decode(self) -> None:
        """Verify JSON-based RNG encoding preserves state (Phase 1.1 requirement)."""
        # This test will guide the implementation of JSON RNG encoding
        # Expected new functions: encode_rng_state_json(), decode_rng_state_json()

        from townlet.utils.rng import encode_rng_state_json, decode_rng_state_json

        config = load_config(Path("configs/examples/poc_hybrid.yaml"))
        loop = SimulationLoop(config)

        # Get RNG state
        original_state = loop._rng_world.getstate()

        # Encode to JSON (should NOT use pickle)
        encoded_json = encode_rng_state_json(original_state)

        # Verify it's valid JSON
        parsed = json.loads(encoded_json)
        assert isinstance(parsed, dict), "JSON RNG should encode to a dict"
        assert "v" in parsed, "JSON RNG should have version field ('v')"
        assert "s" in parsed, "JSON RNG should have state field ('s')"
        assert "g" in parsed, "JSON RNG should have gauss_next field ('g')"

        # Decode back
        decoded_state = decode_rng_state_json(encoded_json)

        # States should match
        assert decoded_state == original_state, "JSON encode/decode should preserve RNG state"

    def test_json_rng_produces_same_sequence(self) -> None:
        """Verify JSON RNG encode/decode preserves random sequence."""
        import random

        from townlet.utils.rng import decode_rng_state_json, encode_rng_state_json

        config = load_config(Path("configs/examples/poc_hybrid.yaml"))
        loop = SimulationLoop(config)

        # Capture state
        original_state = loop._rng_world.getstate()

        # Encode to JSON
        encoded_json = encode_rng_state_json(original_state)

        # Create two RNGs: one from original state, one from JSON roundtrip
        rng_original = random.Random()
        rng_original.setstate(original_state)

        rng_json = random.Random()
        decoded_json = decode_rng_state_json(encoded_json)
        rng_json.setstate(decoded_json)

        # Generate samples from both
        samples_original = [rng_original.random() for _ in range(20)]
        samples_json = [rng_json.random() for _ in range(20)]

        # Sequences must be identical
        assert samples_original == samples_json, "JSON encode/decode must preserve random sequence"

    def test_json_rng_no_pickle_imports(self) -> None:
        """Verify JSON RNG implementation doesn't use pickle (security requirement)."""
        import inspect

        from townlet.utils import rng

        # Check that encode/decode functions don't use pickle
        if hasattr(rng, "encode_rng_state"):
            source = inspect.getsource(rng.encode_rng_state)
            assert "pickle" not in source.lower(), "JSON RNG encode must not use pickle"

        if hasattr(rng, "decode_rng_state"):
            source = inspect.getsource(rng.decode_rng_state)
            assert "pickle" not in source.lower(), "JSON RNG decode must not use pickle"

        # Verify the implementation uses json module
        module_source = inspect.getsource(rng)
        assert "import json" in module_source, "RNG module should use json for serialization"

    def test_migration_preserves_all_three_rng_streams(self) -> None:
        """Verify JSON encoding preserves world, events, and policy RNG streams."""
        from townlet.utils.rng import decode_rng_state_json, encode_rng_state_json

        config = load_config(Path("configs/examples/poc_hybrid.yaml"))
        loop = SimulationLoop(config)

        # Advance to get interesting RNG states
        for _ in range(10):
            loop.step()

        # Capture all three streams
        world_state = loop._rng_world.getstate()
        events_state = loop._rng_events.getstate()
        policy_state = loop._rng_policy.getstate()

        # Encode all three to JSON
        world_json = encode_rng_state_json(world_state)
        events_json = encode_rng_state_json(events_state)
        policy_json = encode_rng_state_json(policy_state)

        # All should be valid JSON
        json.loads(world_json)
        json.loads(events_json)
        json.loads(policy_json)

        # Decode back
        world_decoded = decode_rng_state_json(world_json)
        events_decoded = decode_rng_state_json(events_json)
        policy_decoded = decode_rng_state_json(policy_json)

        # All should match original states
        assert world_decoded == world_state, "World RNG encode/decode failed"
        assert events_decoded == events_state, "Events RNG encode/decode failed"
        assert policy_decoded == policy_state, "Policy RNG encode/decode failed"

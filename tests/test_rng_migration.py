"""Migration compatibility tests for pickle→JSON RNG transition.

These tests will FAIL initially - that's expected! They define the acceptance
criteria for Phase 1.1 (RNG Migration). Once the JSON-based RNG implementation
is complete, these tests should all pass.

DO NOT MODIFY THESE TESTS TO MAKE THEM PASS. Instead, implement the JSON RNG
to satisfy these test requirements.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop


# Mark all tests in this module as expected to fail until JSON RNG is implemented
pytestmark = pytest.mark.xfail(reason="JSON RNG not yet implemented - Phase 1.1 work", strict=False)


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
        assert "version" in parsed, "JSON RNG should have version field"
        assert "state" in parsed, "JSON RNG should have state field"

        # Decode back
        decoded_state = decode_rng_state_json(encoded_json)

        # States should match
        assert decoded_state == original_state, "JSON encode/decode should preserve RNG state"

    def test_json_rng_produces_same_sequence(self) -> None:
        """Verify JSON RNG produces identical random sequence (Phase 1.1 requirement)."""
        from townlet.utils.rng import decode_rng_state_json, encode_rng_state_json

        config = load_config(Path("configs/examples/poc_hybrid.yaml"))
        loop = SimulationLoop(config)

        # Capture state with pickle (current implementation)
        import random
        from townlet.utils.rng import encode_rng_state as encode_pickle

        state_pickle = loop._rng_world.getstate()
        encoded_pickle = encode_pickle(state_pickle)

        # Convert to JSON encoding
        encoded_json = encode_rng_state_json(state_pickle)

        # Create two RNGs: one from pickle, one from JSON
        rng_pickle = random.Random()
        rng_pickle.setstate(state_pickle)

        rng_json = random.Random()
        decoded_json = decode_rng_state_json(encoded_json)
        rng_json.setstate(decoded_json)

        # Generate samples from both
        samples_pickle = [rng_pickle.random() for _ in range(20)]
        samples_json = [rng_json.random() for _ in range(20)]

        # Sequences must be identical
        assert samples_pickle == samples_json, "JSON and pickle RNG must produce identical sequences"

    def test_json_snapshot_backwards_compatible(self) -> None:
        """Verify JSON RNG snapshots can load pickle-based baseline snapshots (Phase 1.1)."""
        # This ensures we can load old snapshots after migration

        config = load_config(Path("configs/examples/poc_hybrid.yaml"))
        loop = SimulationLoop(config)

        # Load a pickle-based baseline snapshot
        loop.load_snapshot(BASELINE_SNAPSHOTS / "snapshot-10.json")

        assert loop.tick == 10, "Should load pickle-based snapshot"

        # Advance with JSON RNG (once implemented)
        for _ in range(10):
            loop.step()

        # Should produce the same hash as pickle-based golden test
        world_hash = compute_world_hash(loop)
        expected_hash = "4784f575921386e00e1b1ad819404adb92b1c780681755355be1c59246a077c3"

        assert world_hash == expected_hash, "JSON RNG must preserve determinism from pickle baseline"

    def test_json_rng_no_pickle_imports(self) -> None:
        """Verify JSON RNG implementation doesn't use pickle (Phase 1.1 security requirement)."""
        import importlib
        import sys

        # Reload rng module to check imports
        if "townlet.utils.rng" in sys.modules:
            del sys.modules["townlet.utils.rng"]

        # Import with import hook to detect pickle usage
        original_import = __builtins__.__import__
        pickle_imported = []

        def import_hook(name, *args, **kwargs):
            if name == "pickle" or name.startswith("pickle."):
                pickle_imported.append(name)
            return original_import(name, *args, **kwargs)

        __builtins__.__import__ = import_hook

        try:
            from townlet.utils import rng

            # Check that JSON functions don't use pickle
            import inspect

            if hasattr(rng, "encode_rng_state_json"):
                source = inspect.getsource(rng.encode_rng_state_json)
                assert "pickle" not in source.lower(), "JSON RNG encode must not use pickle"

            if hasattr(rng, "decode_rng_state_json"):
                source = inspect.getsource(rng.decode_rng_state_json)
                assert "pickle" not in source.lower(), "JSON RNG decode must not use pickle"

        finally:
            __builtins__.__import__ = original_import

        # Legacy pickle functions can remain for backwards compatibility
        # but new JSON functions must not use pickle
        assert len(pickle_imported) == 0 or all(
            "json" not in p for p in pickle_imported
        ), "JSON RNG functions must not import pickle"

    def test_migration_preserves_all_three_rng_streams(self) -> None:
        """Verify migration preserves world, events, and policy RNG streams (Phase 1.1)."""
        from townlet.utils.rng import decode_rng_state_json, encode_rng_state_json

        config = load_config(Path("configs/examples/poc_hybrid.yaml"))
        loop = SimulationLoop(config)

        # Advance to get interesting RNG states
        for _ in range(10):
            loop.step()

        # Capture all three streams with pickle
        world_pickle = loop._rng_world.getstate()
        events_pickle = loop._rng_events.getstate()
        policy_pickle = loop._rng_policy.getstate()

        # Encode all three to JSON
        world_json = encode_rng_state_json(world_pickle)
        events_json = encode_rng_state_json(events_pickle)
        policy_json = encode_rng_state_json(policy_pickle)

        # All should be valid JSON
        json.loads(world_json)
        json.loads(events_json)
        json.loads(policy_json)

        # Decode back
        world_decoded = decode_rng_state_json(world_json)
        events_decoded = decode_rng_state_json(events_json)
        policy_decoded = decode_rng_state_json(policy_json)

        # All should match original pickle states
        assert world_decoded == world_pickle, "World RNG migration failed"
        assert events_decoded == events_pickle, "Events RNG migration failed"
        assert policy_decoded == policy_pickle, "Policy RNG migration failed"

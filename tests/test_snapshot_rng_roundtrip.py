"""Round-trip tests for snapshot RNG serialization.

These tests verify that saving and loading snapshots preserves RNG state perfectly.
This ensures that snapshot save→load cycles don't introduce non-determinism.
"""

from __future__ import annotations

from pathlib import Path
import tempfile

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop


class TestSnapshotRNGRoundtrip:
    """Test suite for snapshot RNG round-trip integrity."""

    def test_snapshot_roundtrip_preserves_determinism(self) -> None:
        """Verify that save→load→advance produces same result as just advance."""
        config = load_config(Path("configs/examples/poc_hybrid.yaml"))

        # Path 1: Advance 20 ticks directly
        loop1 = SimulationLoop(config)
        for _ in range(20):
            loop1.step()

        # Capture final state
        final_tick_1 = loop1.tick
        final_agents_1 = {
            agent_id: (agent.x, agent.y, agent.hunger, agent.hygiene, agent.energy)
            for agent_id, agent in loop1.world.agents.items()
        }

        # Path 2: Advance 10 ticks, save, load, advance 10 more
        loop2 = SimulationLoop(config)
        for _ in range(10):
            loop2.step()

        # Save snapshot
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot_path = loop2.save_snapshot(Path(tmpdir))

            # Load snapshot into new loop
            loop3 = SimulationLoop(config)
            loop3.load_snapshot(snapshot_path)

            # Advance 10 more ticks
            for _ in range(10):
                loop3.step()

        # Capture final state from path 2
        final_tick_2 = loop3.tick
        final_agents_2 = {
            agent_id: (agent.x, agent.y, agent.hunger, agent.hygiene, agent.energy)
            for agent_id, agent in loop3.world.agents.items()
        }

        # Both paths should produce identical results
        assert final_tick_1 == final_tick_2, f"Tick mismatch: {final_tick_1} != {final_tick_2}"
        assert final_agents_1 == final_agents_2, "Agent states differ after snapshot round-trip"

    def test_snapshot_roundtrip_rng_states(self) -> None:
        """Verify that snapshot preserves exact RNG states for all three streams."""
        config = load_config(Path("configs/examples/poc_hybrid.yaml"))

        loop = SimulationLoop(config)
        for _ in range(15):
            loop.step()

        # Capture RNG states before snapshot
        world_state_before = loop._rng_world.getstate()
        events_state_before = loop._rng_events.getstate()
        policy_state_before = loop._rng_policy.getstate()

        # Save and load snapshot
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot_path = loop.save_snapshot(Path(tmpdir))

            loop2 = SimulationLoop(config)
            loop2.load_snapshot(snapshot_path)

        # RNG states should be identical after round-trip
        assert loop2._rng_world.getstate() == world_state_before, "World RNG state not preserved"
        assert loop2._rng_events.getstate() == events_state_before, "Events RNG state not preserved"
        assert loop2._rng_policy.getstate() == policy_state_before, "Policy RNG state not preserved"

    def test_multiple_roundtrips_preserve_determinism(self) -> None:
        """Verify that multiple save→load cycles don't accumulate errors."""
        config = load_config(Path("configs/examples/poc_hybrid.yaml"))

        loop = SimulationLoop(config)

        # Perform 3 cycles of: advance 5 ticks → save → load
        for cycle in range(3):
            for _ in range(5):
                loop.step()

            # Save and reload
            with tempfile.TemporaryDirectory() as tmpdir:
                snapshot_path = loop.save_snapshot(Path(tmpdir))

                # Capture state before reload
                tick_before = loop.tick
                agents_before = {
                    agent_id: (agent.x, agent.y, agent.hunger)
                    for agent_id, agent in loop.world.agents.items()
                }

                # Load into same loop
                loop.load_snapshot(snapshot_path)

                # State should be unchanged
                assert loop.tick == tick_before, f"Tick changed after reload in cycle {cycle}"
                agents_after = {
                    agent_id: (agent.x, agent.y, agent.hunger)
                    for agent_id, agent in loop.world.agents.items()
                }
                assert agents_before == agents_after, f"Agent state changed after reload in cycle {cycle}"

        # After 3 cycles (15 ticks total), verify we can still advance deterministically
        rng_state = loop._rng_world.getstate()

        # Advance 5 more ticks
        for _ in range(5):
            loop.step()

        final_tick = loop.tick
        assert final_tick == 20, f"Expected tick 20, got {final_tick}"


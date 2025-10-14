#!/usr/bin/env python3
"""Capture golden hashes for RNG determinism tests."""
import sys
sys.path.insert(0, "src")

import hashlib
import json
from pathlib import Path

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop

BASELINE_SNAPSHOTS = Path("tests/fixtures/baselines/snapshots")


def compute_world_hash(loop: SimulationLoop) -> str:
    """Compute a deterministic hash of the world state."""
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


print("Capturing golden hashes for RNG determinism tests...")
print()

config = load_config(Path("configs/examples/poc_hybrid.yaml"))

# Test 1: tick 10 → 20
print("Test 1: Loading snapshot at tick 10, advancing 10 ticks...")
loop1 = SimulationLoop(config)
loop1.load_snapshot(BASELINE_SNAPSHOTS / "snapshot-10.json")
for _ in range(10):
    loop1.step()
hash1 = compute_world_hash(loop1)
print(f"✓ Golden hash (tick 10 → 20): {hash1}")
print()

# Test 2: tick 25 → 40
print("Test 2: Loading snapshot at tick 25, advancing 15 ticks...")
loop2 = SimulationLoop(config)
loop2.load_snapshot(BASELINE_SNAPSHOTS / "snapshot-25.json")
for _ in range(15):
    loop2.step()
hash2 = compute_world_hash(loop2)
print(f"✓ Golden hash (tick 25 → 40): {hash2}")
print()

# Test 3: tick 50 → 70
print("Test 3: Loading snapshot at tick 50, advancing 20 ticks...")
loop3 = SimulationLoop(config)
loop3.load_snapshot(BASELINE_SNAPSHOTS / "snapshot-50.json")
for _ in range(20):
    loop3.step()
hash3 = compute_world_hash(loop3)
print(f"✓ Golden hash (tick 50 → 70): {hash3}")
print()

print("Done! Update tests/test_rng_golden.py with these hashes:")
print(f'  expected_hash = "{hash1}"  # tick 10 → 20')
print(f'  expected_hash = "{hash2}"  # tick 25 → 40')
print(f'  expected_hash = "{hash3}"  # tick 50 → 70')

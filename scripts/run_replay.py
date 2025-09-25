"""Utility to replay observation/telemetry samples for analysis or tutorials."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import numpy as np

from townlet.policy.replay import load_replay_sample


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay Townlet observation/telemetry samples")
    parser.add_argument(
        "sample",
        type=Path,
        help="Path to observation sample npz (e.g. docs/samples/observation_hybrid_sample.npz)",
    )
    parser.add_argument(
        "--meta",
        type=Path,
        default=None,
        help="Optional metadata JSON path (defaults to alongside sample)",
    )
    parser.add_argument(
        "--telemetry",
        type=Path,
        default=None,
        help="Optional telemetry snapshot JSON to inspect",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate sample schema (conflict features) without printing tensors",
    )
    return parser.parse_args()


def render_observation(sample: Dict[str, Any]) -> None:
    feature_names = sample["metadata"].get("feature_names") if sample.get("metadata") else None
    features = sample["features"]
    if feature_names:
        print("Key features (including rivalry metrics):")
        for key in ("need_hunger", "need_hygiene", "need_energy", "rivalry_max", "rivalry_avoid_count"):
            if key in feature_names:
                idx = feature_names.index(key)
                print(f"  {key}: {features[idx]:.3f}")
    else:
        print("Feature tensor length (consider using metadata carriers):", len(features))


def inspect_telemetry(path: Path) -> None:
    data = json.loads(path.read_text())
    conflict = data.get("conflict") or data.get("conflict_snapshot")
    if conflict:
        print("Conflict queues:", conflict.get("queues"))
        rivalry = conflict.get("rivalry", {})
        for agent, rivals in rivalry.items():
            print(f"  {agent}: {rivals}")
    events = data.get("events")
    if events:
        queue_events = [event for event in events if event.get("event") == "queue_conflict"]
        if queue_events:
            print("Queue conflict events:")
            for event in queue_events:
                print("  ", event)


def main() -> None:
    args = parse_args()
    sample = load_replay_sample(args.sample, args.meta)
    if args.validate:
        print("Sample validation successful.")
        return
    obs = {"map": sample.map, "features": sample.features, "metadata": sample.metadata}
    render_observation(obs)
    if args.telemetry:
        inspect_telemetry(args.telemetry)


if __name__ == "__main__":
    main()

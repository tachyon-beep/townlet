"""CLI to capture Townlet rollout trajectories into replay samples."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import numpy as np

from townlet.config.loader import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.policy.metrics import compute_sample_metrics
from townlet.policy.replay import ReplaySample, frames_to_replay_sample
from townlet.policy.scenario_utils import apply_scenario, seed_default_agents


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture rollout trajectories as replay samples.")
    parser.add_argument("config", type=Path, help="Simulation config path")
    parser.add_argument(
        "--ticks",
        type=int,
        default=100,
        help="Number of ticks to simulate before saving frames.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Directory to store replay samples (NPZ + JSON metadata).",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="rollout_sample",
        help="Filename prefix for generated samples.",
    )
    parser.add_argument(
        "--auto-seed-agents",
        action="store_true",
        help="Populate the world with placeholder agents if the scenario lacks agent definitions.",
    )
    parser.add_argument(
        "--agent-id",
        type=str,
        default=None,
        help="Only export frames for the specified agent id.",
    )
    parser.add_argument(
        "--compress",
        action="store_true",
        help="Use numpy.savez_compressed for output NPZ files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    loop = SimulationLoop(config)
    scenario_config: dict[str, Any] | None = getattr(config, "scenario", None)
    if scenario_config:
        apply_scenario(loop, scenario_config)
    elif args.auto_seed_agents and not loop.world.agents:
        seed_default_agents(loop)
    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    total_ticks = int(scenario_config.get("ticks", args.ticks) if scenario_config else args.ticks)
    for _ in range(max(0, total_ticks)):
        loop.step()

    capture_metadata: Dict[str, Any] = {
        "config_path": str(args.config.resolve()),
        "config_id": getattr(config, "config_id", None),
        "scenario_name": args.config.stem,
        "scenario_description": scenario_config.get("description") if scenario_config else None,
        "ticks": total_ticks,
        "seed": getattr(config, "seed", None) or (scenario_config.get("seed") if isinstance(scenario_config, dict) else None),
        "policy_hash": loop.policy.active_policy_hash() if hasattr(loop, "policy") else None,
        "capture_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    frames = loop.policy.collect_trajectory(clear=True)
    if args.agent_id is not None:
        frames = [frame for frame in frames if frame.get("agent_id") == args.agent_id]

    by_agent: dict[str, list[dict[str, object]]] = {}
    for frame in frames:
        agent_id = frame.get("agent_id", "unknown")
        by_agent.setdefault(agent_id, []).append(frame)

    manifest_entries = []
    metrics_map: dict[str, dict[str, float]] = {}
    for index, (agent_id, agent_frames) in enumerate(by_agent.items(), start=1):
        if not agent_frames:
            continue
        sample: ReplaySample = frames_to_replay_sample(agent_frames)
        stem = f"{args.prefix}_{agent_id}_{index:03d}"
        sample_path = output_dir / f"{stem}.npz"
        save_fn = np.savez_compressed if args.compress else np.savez
        save_fn(
            sample_path,
            map=sample.map,
            features=sample.features,
            actions=sample.actions,
            old_log_probs=sample.old_log_probs,
            value_preds=sample.value_preds,
            rewards=sample.rewards,
            dones=sample.dones,
        )
        meta_path = output_dir / f"{stem}.json"
        meta = sample.metadata.copy()
        meta.update({
            "agent_id": agent_id,
            "frame_count": len(agent_frames),
            "capture_metadata": capture_metadata,
        })
        sample_metrics = compute_sample_metrics(sample)
        metrics_map[sample_path.name] = sample_metrics
        meta["metrics"] = sample_metrics
        meta_path.write_text(json.dumps(meta, indent=2))
        manifest_entries.append({
            "sample": str(sample_path.name),
            "meta": str(meta_path.name),
            "agent_id": agent_id,
            "frame_count": len(agent_frames),
        })

    manifest_path = output_dir / f"{args.prefix}_manifest.json"
    manifest_payload = {"metadata": capture_metadata, "samples": manifest_entries}
    manifest_path.write_text(json.dumps(manifest_payload, indent=2))
    metrics_path = output_dir / f"{args.prefix}_metrics.json"
    metrics_payload = {"metadata": capture_metadata, "samples": metrics_map}
    metrics_path.write_text(json.dumps(metrics_payload, indent=2))
    print(f"Captured {len(manifest_entries)} replay samples to {output_dir}")
if __name__ == "__main__":
    main()

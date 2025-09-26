#!/usr/bin/env python
"""Filter and summarise behaviour-cloning trajectories."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Mapping

import numpy as np

from townlet.policy.replay import load_replay_sample


@dataclass
class EvaluationResult:
    sample_path: Path
    meta_path: Path
    metrics: Mapping[str, float]
    accepted: bool


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Curate scripted trajectories for BC datasets")
    parser.add_argument("input", type=Path, help="Directory containing trajectory NPZ/JSON pairs")
    parser.add_argument("--output", type=Path, required=True, help="Output manifest JSON path")
    parser.add_argument("--min-timesteps", type=int, default=10, help="Minimum timesteps to accept")
    parser.add_argument("--min-reward", type=float, default=None, help="Minimum total reward (optional)")
    return parser.parse_args(argv)


def _pair_files(directory: Path) -> Iterable[tuple[Path, Path]]:
    for json_path in sorted(directory.glob("*.json")):
        npz_path = json_path.with_suffix(".npz")
        if npz_path.exists():
            yield npz_path, json_path


def evaluate_sample(npz_path: Path, json_path: Path) -> EvaluationResult:
    sample = load_replay_sample(npz_path, json_path)
    rewards = sample.rewards.astype(float)
    timesteps = int(sample.metadata.get("timesteps", rewards.shape[0]))
    reward_sum = float(np.sum(rewards))
    mean_reward = float(reward_sum / timesteps) if timesteps else 0.0
    done_count = int(np.count_nonzero(sample.dones))

    metrics = {
        "timesteps": timesteps,
        "reward_sum": reward_sum,
        "mean_reward": mean_reward,
        "done_count": done_count,
    }
    return EvaluationResult(npz_path, json_path, metrics, accepted=False)


def curate(result: EvaluationResult, *, min_timesteps: int, min_reward: float | None) -> EvaluationResult:
    accepted = result.metrics["timesteps"] >= min_timesteps
    if min_reward is not None:
        accepted = accepted and (result.metrics["reward_sum"] >= min_reward)
    result.accepted = bool(accepted)
    return result


def write_manifest(results: Iterable[EvaluationResult], output: Path) -> None:
    manifest = []
    for result in results:
        entry = {
            "sample": str(result.sample_path),
            "meta": str(result.meta_path),
            "metrics": dict(result.metrics),
            "accepted": result.accepted,
        }
        manifest.append(entry)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2))


def summarise(results: Iterable[EvaluationResult]) -> Mapping[str, float]:
    accepted = [r for r in results if r.accepted]
    rejected = [r for r in results if not r.accepted]
    return {
        "total": float(len(accepted) + len(rejected)),
        "accepted": float(len(accepted)),
        "rejected": float(len(rejected)),
    }


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv)
    results: List[EvaluationResult] = []
    for npz_path, json_path in _pair_files(args.input):
        result = evaluate_sample(npz_path, json_path)
        result = curate(result, min_timesteps=args.min_timesteps, min_reward=args.min_reward)
        results.append(result)

    write_manifest(results, args.output)
    summary = summarise(results)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":  # pragma: no cover
    main()


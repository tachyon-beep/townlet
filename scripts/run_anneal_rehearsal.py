#!/usr/bin/env python
"""Run BC + anneal rehearsal using production manifests and capture artefacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

from townlet.config import load_config
from townlet.policy.runner import TrainingHarness
from townlet.policy.replay import ReplayDatasetConfig


DEFAULT_CONFIG = Path("artifacts/m5/acceptance/config_idle_v1.yaml")
DEFAULT_MANIFEST = Path("data/bc_datasets/manifests/idle_v1.json")
DEFAULT_LOG_DIR = Path("artifacts/m5/acceptance/logs")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run anneal rehearsal and emit summary")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Training config YAML")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="BC manifest to use for BC stages",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=DEFAULT_LOG_DIR,
        help="Directory to store anneal_results.json",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("artifacts/m5/acceptance/summary_idle_v1.json"),
        help="Path to write rehearsal summary JSON",
    )
    parser.add_argument(
        "--exit-on-failure",
        action="store_true",
        help="Return non-zero exit code if BC gate fails or drift flags trigger",
    )
    return parser.parse_args()


def run_rehearsal(config_path: Path, manifest_path: Path, log_dir: Path) -> Dict[str, object]:
    config = load_config(config_path)
    harness = TrainingHarness(config)
    dataset = ReplayDatasetConfig.from_manifest(manifest_path)
    results = harness.run_anneal(
        dataset_config=dataset,
        bc_manifest=manifest_path,
        log_dir=log_dir,
    )
    latest = results[-1] if results else {}
    summary = {
        "bc": next((stage for stage in results if stage.get("mode") == "bc"), {}),
        "ppo": latest,
        "results": results,
    }
    return summary


def evaluate_summary(summary: Dict[str, object]) -> Dict[str, object]:
    bc_stage = summary.get("bc", {})
    ppo_stage = summary.get("ppo", {})
    bc_passed = bool(bc_stage.get("passed", False))
    loss_flag = bool(ppo_stage.get("anneal_loss_flag", False))
    queue_flag = bool(ppo_stage.get("anneal_queue_flag", False))
    intensity_flag = bool(ppo_stage.get("anneal_intensity_flag", False))
    status = "PASS"
    if not bc_passed:
        status = "FAIL"
    elif loss_flag or queue_flag or intensity_flag:
        status = "HOLD"
    summary.update(
        {
            "status": status,
            "bc_passed": bc_passed,
            "loss_flag": loss_flag,
            "queue_flag": queue_flag,
            "intensity_flag": intensity_flag,
        }
    )
    return summary


def main() -> None:
    args = parse_args()
    summary = run_rehearsal(args.config, args.manifest, args.log_dir)
    final = evaluate_summary(summary)
    args.summary.write_text(json.dumps(final, indent=2))
    print(json.dumps(final, indent=2))
    if args.exit_on_failure and final.get("status") != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":  # pragma: no cover
    main()

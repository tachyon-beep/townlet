#!/usr/bin/env python
"""Run BC + anneal rehearsal using production manifests and capture artefacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from townlet.config import load_config
from townlet.policy.replay import ReplayDatasetConfig
from townlet.policy.training_orchestrator import PolicyTrainingOrchestrator

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


def run_rehearsal(config_path: Path, manifest_path: Path, log_dir: Path) -> dict[str, object]:
    config = load_config(config_path)
    harness = PolicyTrainingOrchestrator(config)
    dataset = ReplayDatasetConfig.from_manifest(manifest_path)
    results = harness.run_anneal(
        dataset_config=dataset,
        bc_manifest=manifest_path,
        log_dir=log_dir,
    )
    status = harness.last_anneal_status or harness.evaluate_anneal_results(results)
    bc_stage = next((stage for stage in results if stage.get("mode") == "bc"), {})
    ppo_stage = results[-1] if results else {}
    summary = {
        "status": status,
        "results": results,
        "promotion": harness.promotion.snapshot(),
        "bc": bc_stage,
        "ppo": ppo_stage,
        "bc_passed": bool(bc_stage.get("passed", False)),
        "loss_flag": bool(ppo_stage.get("anneal_loss_flag", False)),
        "queue_flag": bool(ppo_stage.get("anneal_queue_flag", False)),
        "intensity_flag": bool(ppo_stage.get("anneal_intensity_flag", False)),
    }
    return summary



def evaluate_summary(summary: dict[str, object]) -> dict[str, object]:
    if __package__:
        from . import promotion_evaluate as _promotion_eval  # type: ignore[attr-defined]
    else:  # pragma: no cover - script execution path
        import importlib.util
        import sys
        module_path = Path(__file__).with_name("promotion_evaluate.py")
        spec = importlib.util.spec_from_file_location("promotion_evaluate", module_path)
        if spec is None or spec.loader is None:  # pragma: no cover - defensive
            raise ModuleNotFoundError("Could not load promotion_evaluate module")
        _promotion_eval = importlib.util.module_from_spec(spec)  # type: ignore[assignment]
        sys.modules.setdefault("promotion_evaluate", _promotion_eval)
        spec.loader.exec_module(_promotion_eval)  # type: ignore[arg-type]

    decision = _promotion_eval.evaluate(summary)
    combined = dict(summary)
    combined.update(decision)
    if "status" in combined:
        combined["status"] = str(combined["status"]).upper()
    if "decision" in combined:
        combined["decision"] = str(combined["decision"]).upper()
    return combined


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

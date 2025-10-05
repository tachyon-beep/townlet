"""Run alternating replay/rollout PPO cycles for soak testing."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.is_dir():
    sys.path.insert(0, str(SRC))

from townlet.config.loader import load_config  # noqa: E402
from townlet.policy.replay import ReplayDatasetConfig  # noqa: E402
from townlet.policy.training_orchestrator import PolicyTrainingOrchestrator  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Alternating replay/rollout PPO soak harness")
    parser.add_argument("config", type=Path, help="Training config YAML (scenario-driven)")
    parser.add_argument(
        "--baseline-dir",
        type=Path,
        required=True,
        help="Directory containing rollout manifest/metrics for replay baseline",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory to write soak telemetry artefacts",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=12,
        help="Total cycles to run (alternates replay, rollout)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=1,
        help="Epochs per cycle (default: 1)",
    )
    parser.add_argument(
        "--rollout-ticks",
        type=int,
        default=40,
        help="Tick count for rollout cycles",
    )
    parser.add_argument(
        "--replay-batch-size",
        type=int,
        default=1,
        help="Batch size for replay cycles",
    )
    parser.add_argument(
        "--rollout-batch-size",
        type=int,
        default=2,
        help="Batch size for rollout cycles",
    )
    parser.add_argument(
        "--log-frequency",
        type=int,
        default=1,
        help="Epoch logging cadence for both modes",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    harness = PolicyTrainingOrchestrator(config)

    dataset_config = ReplayDatasetConfig.from_capture_dir(
        args.baseline_dir,
        batch_size=args.replay_batch_size,
        shuffle=False,
    )

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "ppo_soak.jsonl"
    if log_path.exists():
        log_path.unlink()

    for cycle in range(max(args.cycles, 0)):
        if cycle % 2 == 0:
            harness.run_ppo(
                dataset_config=dataset_config,
                epochs=args.epochs,
                log_path=log_path,
                log_frequency=args.log_frequency,
            )
        else:
            harness.run_rollout_ppo(
                ticks=args.rollout_ticks,
                batch_size=args.rollout_batch_size,
                epochs=args.epochs,
                log_path=log_path,
                log_frequency=args.log_frequency,
            )

    print(f"Soak run complete. Telemetry log written to {log_path}")


if __name__ == "__main__":
    main()

"""CLI entry point for training Townlet policies."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Optional

from townlet.config import PPOConfig
from townlet.config.loader import load_config
from townlet.policy.replay import ReplayDatasetConfig
from townlet.policy.runner import TrainingHarness


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Townlet PPO policies.")
    parser.add_argument(
        "config",
        type=Path,
        help="Path to the simulation configuration YAML.",
    )
    parser.add_argument(
        "--replay-sample",
        type=Path,
        default=None,
        help="Optional observation sample NPZ to replay instead of training.",
    )
    parser.add_argument(
        "--replay-meta",
        type=Path,
        default=None,
        help="Optional metadata JSON path for the replay sample.",
    )
    parser.add_argument(
        "--replay-manifest",
        type=Path,
        default=None,
        help="Manifest (json/yaml) listing replay samples to batch.",
    )
    parser.add_argument("--replay-batch-size", type=int, default=1, help="Batch size for replay dataset.")
    parser.add_argument("--replay-shuffle", action="store_true", help="Shuffle replay dataset each epoch.")
    parser.add_argument("--replay-seed", type=int, default=None, help="Seed for replay shuffling.")
    parser.add_argument("--replay-drop-last", action="store_true", help="Drop final incomplete batch.")
    parser.add_argument("--replay-streaming", action="store_true", help="Stream samples from disk instead of preloading.")
    parser.add_argument("--train-ppo", action="store_true", help="Run PPO stub using replay dataloader.")
    parser.add_argument("--rollout-save-dir", type=Path, default=None, help="Directory to save replay samples captured from live rollouts.")
    parser.add_argument("--rollout-ticks", type=int, default=0, help="Number of ticks to run for rollout capture (0 disables).")
    parser.add_argument("--epochs", type=int, default=1, help="Number of epochs for PPO replay runs.")
    parser.add_argument("--ppo-log", type=Path, default=None, help="Optional JSONL file to log PPO epoch summaries.")
    ppo_group = parser.add_argument_group("PPO overrides")
    ppo_group.add_argument("--ppo-learning-rate", type=float, default=None, help="Override PPO learning rate.")
    ppo_group.add_argument("--ppo-clip-param", type=float, default=None, help="Override PPO clip parameter.")
    ppo_group.add_argument("--ppo-value-loss-coef", type=float, default=None, help="Override PPO value loss coefficient.")
    ppo_group.add_argument("--ppo-entropy-coef", type=float, default=None, help="Override PPO entropy coefficient.")
    ppo_group.add_argument("--ppo-num-epochs", type=int, default=None, help="Override PPO epoch count.")
    ppo_group.add_argument("--ppo-mini-batch-size", type=int, default=None, help="Override PPO mini-batch size.")
    ppo_group.add_argument("--ppo-num-mini-batches", type=int, default=None, help="Override PPO number of mini-batches per epoch.")
    ppo_group.add_argument("--ppo-gae-lambda", type=float, default=None, help="Override PPO GAE lambda.")
    ppo_group.add_argument("--ppo-gamma", type=float, default=None, help="Override PPO discount factor.")
    ppo_group.add_argument("--ppo-max-grad-norm", type=float, default=None, help="Override PPO gradient clipping norm.")
    ppo_group.add_argument("--ppo-value-clip", type=float, default=None, help="Override PPO value clipping parameter.")
    ppo_group.add_argument(
        "--ppo-normalize-advantages",
        dest="ppo_normalize_advantages",
        action="store_true",
        help="Force advantage normalization on.",
    )
    ppo_group.add_argument(
        "--ppo-no-normalize-advantages",
        dest="ppo_normalize_advantages",
        action="store_false",
        help="Force advantage normalization off.",
    )
    ppo_group.set_defaults(ppo_normalize_advantages=None)
    return parser.parse_args()


def _collect_ppo_overrides(args: argparse.Namespace) -> Dict[str, object]:
    overrides: Dict[str, object] = {}
    maybe_fields = {
        "learning_rate": args.ppo_learning_rate,
        "clip_param": args.ppo_clip_param,
        "value_loss_coef": args.ppo_value_loss_coef,
        "entropy_coef": args.ppo_entropy_coef,
        "num_epochs": args.ppo_num_epochs,
        "mini_batch_size": args.ppo_mini_batch_size,
        "num_mini_batches": args.ppo_num_mini_batches,
        "gae_lambda": args.ppo_gae_lambda,
        "gamma": args.ppo_gamma,
        "max_grad_norm": args.ppo_max_grad_norm,
        "value_clip": args.ppo_value_clip,
    }
    for field, value in maybe_fields.items():
        if value is not None:
            overrides[field] = value
    if args.ppo_normalize_advantages is not None:
        overrides["advantage_normalization"] = bool(args.ppo_normalize_advantages)
    return overrides


def _apply_ppo_overrides(config, overrides: Dict[str, object]) -> None:
    if not overrides:
        return
    base = config.ppo or PPOConfig()
    config.ppo = base.model_copy(update=overrides)


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    _apply_ppo_overrides(config, _collect_ppo_overrides(args))
    harness = TrainingHarness(config=config)

    if args.train_ppo:
        entries: list[tuple[Path, Optional[Path]]] = []
        if args.replay_manifest is not None:
            dataset_config = ReplayDatasetConfig.from_manifest(
                args.replay_manifest,
                batch_size=args.replay_batch_size,
                shuffle=args.replay_shuffle,
                seed=args.replay_seed,
                drop_last=args.replay_drop_last,
                streaming=args.replay_streaming,
            )
        elif args.replay_sample is not None:
            entries = [(args.replay_sample, args.replay_meta)]
            dataset_config = ReplayDatasetConfig(
                entries=entries,
                batch_size=args.replay_batch_size,
                shuffle=args.replay_shuffle,
                seed=args.replay_seed,
                drop_last=args.replay_drop_last,
                streaming=args.replay_streaming,
            )
        else:
            raise ValueError("PPO run requires replay sample or manifest")
        harness.run_ppo(dataset_config, epochs=args.epochs, log_path=args.ppo_log)
    elif args.replay_manifest is not None:
        dataset_config = ReplayDatasetConfig.from_manifest(
            args.replay_manifest,
            batch_size=args.replay_batch_size,
            shuffle=args.replay_shuffle,
            seed=args.replay_seed,
            drop_last=args.replay_drop_last,
            streaming=args.replay_streaming,
        )
        harness.run_replay_dataset(dataset_config)
    elif args.replay_sample is not None:
        harness.run_replay(args.replay_sample, args.replay_meta)
    else:
        harness.run()


if __name__ == "__main__":
    main()

"""Quick-look plotting utility for PPO telemetry JSONL logs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot PPO telemetry (loss/KL) from JSONL logs.")
    parser.add_argument(
        "log",
        type=Path,
        nargs="?",
        default=Path("docs/samples/ppo_epoch_log.jsonl"),
        help="Path to the PPO JSONL log (defaults to docs sample).",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the plot interactively (requires matplotlib).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to save the plot as PNG (requires matplotlib).",
    )
    return parser.parse_args()


def load_entries(log_path: Path) -> list[dict[str, Any]]:
    if not log_path.exists():
        raise FileNotFoundError(log_path)
    entries: list[dict[str, Any]] = []
    with log_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            entries.append(json.loads(line))
    if not entries:
        raise ValueError(f"No telemetry entries found in {log_path}")
    return entries


def summarise(entries: list[dict[str, Any]]) -> None:
    epochs = [entry.get("epoch", idx + 1) for idx, entry in enumerate(entries)]
    loss_total = [float(entry.get("loss_total", 0.0)) for entry in entries]
    kl_divergence = [float(entry.get("kl_divergence", 0.0)) for entry in entries]
    print(f"Loaded {len(entries)} telemetry rows spanning epochs {epochs[0]} → {epochs[-1]}")
    print(f"Loss_total range: {min(loss_total):.4f} → {max(loss_total):.4f}")
    print(f"KL divergence range: {min(kl_divergence):.6f} → {max(kl_divergence):.6f}")


def plot(entries: list[dict[str, Any]], show: bool, output: Path | None) -> None:
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError:  # pragma: no cover - optional dependency
        print("matplotlib not installed; skipping plot generation.")
        if output is not None:
            print("Install matplotlib to enable --output rendering.")
        return

    epochs = [entry.get("epoch", idx + 1) for idx, entry in enumerate(entries)]
    loss_total = [float(entry.get("loss_total", 0.0)) for entry in entries]
    kl_divergence = [float(entry.get("kl_divergence", 0.0)) for entry in entries]

    fig, ax1 = plt.subplots()
    ax1.set_title("PPO Telemetry")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss (total)", color="tab:blue")
    ax1.plot(epochs, loss_total, label="loss_total", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    ax2 = ax1.twinx()
    ax2.set_ylabel("KL divergence", color="tab:orange")
    ax2.plot(epochs, kl_divergence, label="kl_divergence", color="tab:orange", linestyle="--")
    ax2.tick_params(axis="y", labelcolor="tab:orange")

    fig.tight_layout()

    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output)
        print(f"Saved plot to {output}")
    if show:
        plt.show()
    plt.close(fig)


def main() -> None:
    args = parse_args()
    entries = load_entries(args.log)
    summarise(entries)
    plot(entries, show=args.show, output=args.output)


if __name__ == "__main__":
    main()

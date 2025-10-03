#!/usr/bin/env python
"""Summarise behaviour cloning evaluation metrics."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarise BC evaluation metrics")
    parser.add_argument("metrics", type=Path, help="Path to evaluation metrics JSON (list or dict)")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    return parser.parse_args()


def load_metrics(path: Path) -> list[dict[str, float]]:
    data = json.loads(path.read_text())
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    raise ValueError("Metrics file must be JSON object or list")


def summarise(metrics: list[dict[str, float]]) -> dict[str, float]:
    if not metrics:
        return {"count": 0.0, "mean_accuracy": 0.0, "min_accuracy": 0.0}
    accuracies = [float(entry.get("accuracy", 0.0)) for entry in metrics]
    return {
        "count": float(len(metrics)),
        "mean_accuracy": float(sum(accuracies) / len(accuracies)),
        "min_accuracy": float(min(accuracies)),
    }


def main() -> None:
    args = parse_args()
    metrics = load_metrics(args.metrics)
    summary = summarise(metrics)
    if args.format == "json":
        print(json.dumps(summary, indent=2))
    else:
        lines = ["| Metric | Value |", "| --- | --- |"]
        for key, value in summary.items():
            lines.append(f"| {key} | {value:.4f} |")
        print("\n".join(lines))


if __name__ == "__main__":  # pragma: no cover
    main()


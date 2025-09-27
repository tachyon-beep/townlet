"""Utility helpers for replay and rollout metrics."""

from __future__ import annotations

import json
from typing import Any

import numpy as np

from .replay import ReplaySample


def compute_sample_metrics(sample: ReplaySample) -> dict[str, float]:
    """Compute summary metrics for a replay sample."""
    metrics: dict[str, float] = {}
    rewards = sample.rewards
    metrics["timesteps"] = float(rewards.shape[0])
    metrics["reward_sum"] = float(np.sum(rewards))
    metrics["reward_mean"] = float(np.mean(rewards)) if rewards.size else 0.0
    metrics["log_prob_mean"] = (
        float(np.mean(sample.old_log_probs)) if sample.old_log_probs.size else 0.0
    )
    metrics["value_pred_last"] = (
        float(sample.value_preds[-1]) if sample.value_preds.size else 0.0
    )

    names = sample.metadata.get("feature_names")
    if isinstance(names, list):
        features = sample.features
        if features.ndim == 1:
            features = features[np.newaxis, :]

        def add_stats(feature_name: str) -> None:
            if feature_name in names:
                idx = names.index(feature_name)
                column = features[:, idx]
                metrics[f"{feature_name}_mean"] = float(np.mean(column))
                metrics[f"{feature_name}_max"] = float(np.max(column))

        add_stats("rivalry_max")
        add_stats("rivalry_avoid_count")
        reward_idx = names.index("reward_total") if "reward_total" in names else None
        if reward_idx is not None:
            metrics["reward_feature_mean"] = float(np.mean(features[:, reward_idx]))
        lateness_idx = (
            names.index("lateness_counter") if "lateness_counter" in names else None
        )
        if lateness_idx is not None:
            metrics["lateness_mean"] = float(np.mean(features[:, lateness_idx]))

    action_ids = sample.actions.astype(int)
    action_counts = (
        np.bincount(action_ids, minlength=int(action_ids.max() + 1))
        if action_ids.size
        else np.array([])
    )
    total_actions = float(np.sum(action_counts)) if action_counts.size else 0.0
    metrics["action_nonzero"] = (
        float(np.count_nonzero(action_counts)) if action_counts.size else 0.0
    )
    metrics["action_total"] = total_actions
    if total_actions > 0:
        probs = action_counts / total_actions
        metrics["action_entropy"] = float(
            -np.sum(
                np.where(probs > 0, probs * np.log(np.clip(probs, 1e-8, None)), 0.0)
            )
        )
    else:
        metrics["action_entropy"] = 0.0

    action_lookup_meta = sample.metadata.get("action_lookup")
    kind_counts: dict[str, float] = {}
    blocked_total = 0.0
    if isinstance(action_lookup_meta, dict):
        id_to_payload: dict[int, dict[str, Any]] = {}
        for key, value in action_lookup_meta.items():
            if isinstance(value, int):
                action_id = value
                payload_str = key
            else:
                try:
                    action_id = int(key)
                    payload_str = value
                except (TypeError, ValueError):
                    continue
            try:
                payload = json.loads(payload_str)
            except json.JSONDecodeError:
                payload = {"raw": payload_str}
            id_to_payload[action_id] = payload

        for action_id, count in enumerate(action_counts):
            if count == 0:
                continue
            payload = id_to_payload.get(action_id, {})
            kind = payload.get("kind", "unknown")
            kind_counts[kind] = kind_counts.get(kind, 0.0) + float(count)
            if payload.get("blocked"):
                blocked_total += float(count)

    for kind, count in kind_counts.items():
        metrics[f"action_{kind}_count"] = count
    metrics["action_blocked_ratio"] = (
        float(blocked_total / total_actions) if total_actions else 0.0
    )

    return metrics

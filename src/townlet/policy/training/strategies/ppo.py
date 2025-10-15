"""PPO training strategy.

This module implements the PPO (Proximal Policy Optimization) training strategy,
extracting the complex training loop from PolicyTrainingOrchestrator into a
focused, testable, stateless class.

PPO is used for policy fine-tuning after BC warm-start, both standalone and
within anneal schedules.
"""

from __future__ import annotations

import math
import statistics
import time
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from pathlib import Path

    from townlet.dto.policy import PPOTrainingResultDTO
    from townlet.policy.replay import ReplayBatch, ReplayDataset
    from townlet.policy.replay_buffer import InMemoryReplayDataset
    from townlet.policy.training.contexts import TrainingContext

# Telemetry version constant
PPO_TELEMETRY_VERSION = 1.2


class PPOStrategy:
    """PPO training strategy.

    Trains a policy network using Proximal Policy Optimization with GAE,
    clipping, and comprehensive metric tracking. Returns typed DTOs with
    validation and duration tracking.

    Requires PyTorch to be installed. Checks availability before execution.

    Example:
        strategy = PPOStrategy()
        result = strategy.run(context)
        print(f"PPO loss: {result.loss_total:.4f}")
    """

    def run(
        self,
        context: TrainingContext,
        *,
        dataset_config: object | None = None,
        in_memory_dataset: InMemoryReplayDataset | None = None,
        epochs: int = 1,
        log_path: Path | None = None,
        log_frequency: int = 1,
        max_log_entries: int | None = None,
        device_str: str | None = None,
    ) -> PPOTrainingResultDTO:
        """Execute PPO training.

        Args:
            context: Training context with config, services, and anneal context.
            dataset_config: Replay dataset config (or None if using in_memory).
            in_memory_dataset: In-memory replay dataset (for rollouts).
            epochs: Number of training epochs.
            log_path: Optional path for JSONL training log.
            log_frequency: Log every N epochs.
            max_log_entries: Max entries per log file before rotation.
            device_str: Override device selection (e.g., 'cuda:1', 'cpu').

        Returns:
            PPO training result with losses, advantages, and metrics.

        Raises:
            TorchNotAvailableError: If PyTorch is not installed.
            ValueError: If dataset config is missing or invalid.
        """
        from townlet.config import PPOConfig
        from townlet.policy.models import (
            TorchNotAvailableError,
            torch_available,
        )
        from townlet.policy.replay import ReplayDataset, ReplayDatasetConfig

        # Guard: Check torch availability
        if not torch_available():
            raise TorchNotAvailableError(
                "PyTorch is required for PPO training. "
                "Install with: pip install -e .[ml]"
            )

        import torch

        start_time = time.perf_counter()

        # Resolve dataset
        if in_memory_dataset is not None:
            dataset: InMemoryReplayDataset | ReplayDataset = in_memory_dataset
        else:
            if dataset_config is None:
                # Try to resolve from context
                replay_manifest = context.config.training.replay_manifest
                if replay_manifest is None:
                    raise ValueError(
                        "Replay manifest required for PPO training. "
                        "Configure training.replay_manifest or provide dataset_config."
                    )
                dataset_config = ReplayDatasetConfig.from_manifest(replay_manifest)
            dataset = ReplayDataset(dataset_config)

        if len(dataset) == 0:
            raise ValueError("Replay dataset yielded no batches")

        batches: list[ReplayBatch] = list(dataset)
        if not batches:
            raise ValueError("Replay dataset yielded no batches")

        # Derive network dimensions from first batch
        example = batches[0]
        feature_dim = int(example.features.shape[2])
        map_shape = tuple(int(dim) for dim in example.maps.shape[2:])
        if map_shape is None:
            raise ValueError("Replay batch missing map shape metadata")
        action_dim_meta = example.metadata.get("action_dim")
        max_action = max(int(batch.actions.max()) for batch in batches)
        action_dim = int(action_dim_meta) if action_dim_meta is not None else max_action + 1
        if action_dim <= 0:
            raise ValueError("Derived action_dim must be positive")

        baseline_metrics = getattr(dataset, "baseline_metrics", {})

        # Get PPO config
        if context.config.ppo is None:
            context.config.ppo = PPOConfig()
        ppo_cfg = context.config.ppo

        # Select device
        device = self._select_device(device_str)
        self._log_device(device)

        # Build policy network
        policy = self._build_policy_network(feature_dim, map_shape, action_dim)
        policy.train()
        policy.to(device)

        # Create optimizer
        optimizer = torch.optim.Adam(policy.parameters(), lr=ppo_cfg.learning_rate)
        generator = torch.Generator(device=device)

        # Dataset label for logging
        dataset_label_str = self._get_dataset_label(dataset, dataset_config)

        # Training state
        data_mode, rollout_ticks = self._get_data_mode(
            dataset, in_memory_dataset, dataset_config
        )

        # Cycle tracking: For rollout datasets, increment; for replay, use max(cycle_id, 0)
        # This matches old orchestrator behavior (training_orchestrator.py:491-496)
        from townlet.policy.replay_buffer import InMemoryReplayDataset

        cycle_id = self._get_cycle_id(context)
        if isinstance(dataset, InMemoryReplayDataset):
            cycle_id += 1
        else:
            cycle_id = max(cycle_id, 0)

        # Save cycle_id to metadata for plain PPO runs (anneal doesn't need this)
        if context.anneal_context is None:
            context.metadata["cycle_id"] = cycle_id

        # Apply social reward schedule stage for this cycle
        self._apply_social_reward_stage(context, cycle_id)

        # Get or initialize persistent counters from context metadata
        log_stream_offset = int(context.metadata.get("log_stream_offset", 0))
        cumulative_steps = int(context.metadata.get("cumulative_steps", 0))

        # Training loop
        log_handle = None
        log_entries_written = 0
        rotation_index = 0

        last_summary: dict[str, float] = {}

        for epoch in range(epochs):
            epoch_start = time.perf_counter()

            # Increment log_stream_offset for this epoch
            log_stream_offset += 1

            epoch_result = self._train_epoch(
                epoch=epoch,
                batches=batches,
                policy=policy,
                optimizer=optimizer,
                generator=generator,
                device=device,
                ppo_cfg=ppo_cfg,
                dataset_label_str=dataset_label_str,
                cycle_id=cycle_id,
                data_mode=data_mode,
                rollout_ticks=rollout_ticks,
                baseline_metrics=baseline_metrics,
                context=context,
                log_stream_offset=log_stream_offset,
                dataset=dataset,
                cumulative_steps=cumulative_steps,
            )

            # Update cumulative steps with transitions processed in this epoch
            cumulative_steps += int(epoch_result["transitions"])

            epoch_result["epoch_duration_sec"] = float(time.perf_counter() - epoch_start)

            print(f"PPO epoch {epoch + 1}:", epoch_result)

            # Logging
            if log_path is not None and (epoch + 1) % log_frequency == 0:
                if log_handle is None:
                    log_handle = self._open_log(log_path)

                if max_log_entries is not None and log_entries_written >= max_log_entries:
                    log_handle.close()
                    rotation_index += 1
                    rotated_path = log_path.with_name(f"{log_path.name}.{rotation_index}")
                    log_handle = self._open_log(rotated_path)
                    log_entries_written = 0

                import json
                log_handle.write(json.dumps(epoch_result) + "\n")
                log_handle.flush()
                log_entries_written += 1

            last_summary = epoch_result

        if log_handle is not None:
            log_handle.close()

        # Save updated persistent counters back to context
        context.metadata["log_stream_offset"] = log_stream_offset
        context.metadata["cumulative_steps"] = cumulative_steps

        # Calculate duration
        duration_sec = time.perf_counter() - start_time

        # Build typed DTO
        result = self._build_result_dto(last_summary, duration_sec)

        return result

    def _select_device(self, device_str: str | None) -> object:
        """Select torch device (CUDA or CPU)."""
        import torch

        if device_str:
            return torch.device(device_str)

        if torch.cuda.is_available():
            # Pick CUDA device with most free memory
            try:
                best_idx = 0
                best_free = -1
                for i in range(torch.cuda.device_count()):
                    free_bytes, _total = torch.cuda.mem_get_info(i)  # type: ignore[attr-defined]
                    if free_bytes > best_free:
                        best_free = int(free_bytes)
                        best_idx = i
                return torch.device(f"cuda:{best_idx}")
            except Exception:
                return torch.device("cuda")
        else:
            return torch.device("cpu")

    def _log_device(self, device: object) -> None:
        """Log selected device info."""
        import logging

        import torch

        logger = logging.getLogger(__name__)

        dev_name = None
        try:
            if device.type == "cuda":  # type: ignore[attr-defined]
                idx = device.index if device.index is not None else torch.cuda.current_device()  # type: ignore[attr-defined]
                dev_name = torch.cuda.get_device_name(idx)
        except Exception:
            pass

        logger.info("PPO device selected: %s%s", device, f" ({dev_name})" if dev_name else "")
        print(f"PPO device selected: {device}{f' ({dev_name})' if dev_name else ''}")

        try:
            if device.type == "cuda":  # type: ignore[attr-defined]
                torch.cuda.set_device(device)  # type: ignore[arg-type]
                torch.backends.cudnn.benchmark = True  # type: ignore[attr-defined]
                mem = torch.cuda.memory_allocated(device)  # type: ignore[arg-type]
                print(f"CUDA memory allocated (bytes): {int(mem)}")
        except Exception:
            pass

    def _build_policy_network(
        self,
        feature_dim: int,
        map_shape: tuple[int, int, int],
        action_dim: int,
    ) -> object:
        """Build policy network."""
        from townlet.policy.models import (
            ConflictAwarePolicyConfig,
            ConflictAwarePolicyNetwork,
        )

        cfg = ConflictAwarePolicyConfig(
            feature_dim=feature_dim,
            map_shape=map_shape,
            action_dim=action_dim,
            hidden_dim=256,
        )
        return ConflictAwarePolicyNetwork(cfg)

    def _get_dataset_label(
        self,
        dataset: object,
        dataset_config: object | None,
    ) -> str:
        """Get dataset label for logging."""
        dataset_label = getattr(dataset, "label", None)
        if dataset_label:
            return str(dataset_label)
        if dataset_config is not None:
            config_label = getattr(dataset_config, "label", None)
            if config_label:
                return str(config_label)
        return "training_dataset"

    def _get_cycle_id(self, context: TrainingContext) -> int:
        """Get cycle ID from anneal context or metadata-backed counter.

        Returns:
            Cycle ID (anneal context takes precedence over metadata).
        """
        if context.anneal_context is not None:
            return int(context.anneal_context.cycle)

        # For plain PPO runs, use metadata-backed counter (like old _ppo_state)
        return int(context.metadata.get("cycle_id", -1))

    def _get_data_mode(
        self,
        dataset: object,
        in_memory_dataset: object | None,
        dataset_config: object | None,
    ) -> tuple[str, int]:
        """Determine data mode and rollout ticks."""
        from townlet.policy.replay_buffer import InMemoryReplayDataset

        if in_memory_dataset is not None and dataset_config is not None:
            rollout_ticks = int(getattr(in_memory_dataset, "rollout_ticks", 0))
            return ("mixed", rollout_ticks)
        elif isinstance(dataset, InMemoryReplayDataset):
            rollout_ticks = int(getattr(dataset, "rollout_ticks", 0))
            return ("rollout", rollout_ticks)
        else:
            return ("replay", 0)

    def _select_social_reward_stage(self, context: TrainingContext, cycle_id: int) -> str | None:
        """Select social reward stage from schedule based on cycle_id.

        Args:
            context: Training context with config.
            cycle_id: Current training cycle ID.

        Returns:
            Selected stage name, or None if no schedule configured.
        """
        training_cfg = getattr(context.config, "training", None)
        if training_cfg is None:
            return None

        # Check for override first
        stage = getattr(training_cfg, "social_reward_stage_override", None)

        # Process schedule
        schedule = getattr(training_cfg, "social_reward_schedule", []) or []
        try:
            iterable = sorted(
                schedule,
                key=lambda entry: int(getattr(entry, "cycle", 0)),
            )
        except TypeError:
            iterable = []

        # Find the stage for the highest cycle <= cycle_id
        for entry in iterable:
            entry_cycle = int(getattr(entry, "cycle", 0))
            if cycle_id >= entry_cycle:
                stage = getattr(entry, "stage", stage)

        return stage

    def _apply_social_reward_stage(self, context: TrainingContext, cycle_id: int) -> None:
        """Apply social reward stage from schedule to config.

        Args:
            context: Training context with config.
            cycle_id: Current training cycle ID.
        """
        stage = self._select_social_reward_stage(context, cycle_id)
        if stage is None:
            return

        # Get current stage
        current = getattr(context.config.features.stages, "social_rewards", None)

        # Only mutate if changed (use setattr to avoid literal type constraint)
        if stage != current:
            setattr(context.config.features.stages, "social_rewards", stage)  # noqa: B010

    def _open_log(self, log_path: Path) -> object:
        """Open log file for writing."""
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return log_path.open("a", encoding="utf-8", buffering=1)

    def _train_epoch(
        self,
        *,
        epoch: int,
        batches: list[ReplayBatch],
        policy: object,
        optimizer: object,
        generator: object,
        device: object,
        ppo_cfg: object,
        dataset_label_str: str,
        cycle_id: int,
        data_mode: str,
        rollout_ticks: int,
        baseline_metrics: dict[str, float],
        context: TrainingContext,
        log_stream_offset: int,
        dataset: object,
        cumulative_steps: int,
    ) -> dict[str, float]:
        """Train single epoch and return metrics."""
        import torch
        from torch.distributions import Categorical
        from torch.nn.utils import clip_grad_norm_

        # Import PPO ops
        from townlet.policy.backends.pytorch import ppo_utils as ops

        conflict_acc: dict[str, float] = {}
        metrics = {
            "policy_loss": 0.0,
            "value_loss": 0.0,
            "entropy": 0.0,
            "total_loss": 0.0,
            "clip_frac": 0.0,
            "adv_mean": 0.0,
            "adv_std": 0.0,
            "grad_norm": 0.0,
            "kl_divergence": 0.0,
        }
        mini_batch_updates = 0
        transitions_processed = 0

        entropy_values: list[float] = []
        grad_norm_max = 0.0
        kl_max = 0.0
        reward_buffer: list[float] = []
        advantage_buffer: list[float] = []
        health_tracking = {
            "adv_zero_std_batches": 0.0,
            "clip_triggered_minibatches": 0.0,
            "max_clip_fraction": 0.0,
            "min_adv_std": math.inf,
        }

        for batch_index, batch in enumerate(batches, start=1):
            # Summarize batch
            batch_summary = self._summarize_batch(batch, batch_index)
            for key, value in batch_summary.items():
                if key.startswith("conflict."):
                    conflict_acc[key] = conflict_acc.get(key, 0.0) + value

            # Convert to tensors
            maps = torch.from_numpy(batch.maps).float().to(device, non_blocking=True)
            features = torch.from_numpy(batch.features).float().to(device, non_blocking=True)
            actions = torch.from_numpy(batch.actions).long().to(device, non_blocking=True)
            old_log_probs = torch.from_numpy(batch.old_log_probs).float().to(device, non_blocking=True)
            rewards = torch.from_numpy(batch.rewards).float().to(device, non_blocking=True)
            dones = torch.from_numpy(batch.dones.astype(np.float32)).float().to(device, non_blocking=True)
            value_preds_old = torch.from_numpy(batch.value_preds).float().to(device, non_blocking=True)

            # Compute GAE
            gae = ops.compute_gae(
                rewards=rewards,
                value_preds=value_preds_old,
                dones=dones,
                gamma=ppo_cfg.gamma,
                gae_lambda=ppo_cfg.gae_lambda,
            )
            advantages = gae.advantages
            returns = gae.returns

            if ppo_cfg.advantage_normalization:
                advantages = ops.normalize_advantages(advantages.view(-1)).view_as(advantages)

            flat_advantages = advantages.reshape(-1)
            flat_returns = returns.reshape(-1)

            # Validate finite values
            self._ensure_finite("advantages", flat_advantages, batch_index, dataset_label_str)
            self._ensure_finite("returns", flat_returns, batch_index, dataset_label_str)
            self._update_advantage_health(flat_advantages, batch_index, health_tracking)

            reward_buffer.extend(batch.rewards.astype(float).reshape(-1).tolist())
            advantage_buffer.extend(advantages.cpu().numpy().astype(float).reshape(-1).tolist())

            # Flatten batch for mini-batching
            batch_size, timestep_length = rewards.shape
            baseline = ops.value_baseline_from_old_preds(value_preds_old, timestep_length)
            flat_maps = maps.reshape(batch_size * timestep_length, *maps.shape[2:])
            flat_features = features.reshape(batch_size * timestep_length, features.shape[2])
            flat_actions = actions.reshape(-1)
            flat_old_log_probs = old_log_probs.reshape(-1)
            flat_old_values = baseline.reshape(-1)

            total_transitions = flat_actions.shape[0]
            desired_batches = min(ppo_cfg.num_mini_batches, total_transitions)
            mini_batch_size = min(
                ppo_cfg.mini_batch_size,
                max(1, total_transitions // desired_batches),
            )
            if mini_batch_size <= 0:
                mini_batch_size = 1

            perm = torch.randperm(
                total_transitions,
                device=flat_actions.device,
                generator=generator,
            )

            # Mini-batch updates
            for start in range(0, total_transitions, mini_batch_size):
                idx = perm[start : start + mini_batch_size]
                mb_maps = flat_maps[idx]
                mb_features = flat_features[idx]
                mb_actions = flat_actions[idx]
                mb_old_log_probs = flat_old_log_probs[idx]
                mb_advantages = flat_advantages[idx]
                mb_returns = flat_returns[idx]
                mb_old_values = flat_old_values[idx]

                logits, values = policy(mb_maps, mb_features)
                dist = Categorical(logits=logits)
                new_log_probs = dist.log_prob(mb_actions)
                entropy = dist.entropy().mean()

                policy_loss, clip_frac = ops.policy_surrogate(
                    new_log_probs=new_log_probs,
                    old_log_probs=mb_old_log_probs,
                    advantages=mb_advantages,
                    clip_param=ppo_cfg.clip_param,
                )
                value_loss = ops.clipped_value_loss(
                    new_values=values,
                    returns=mb_returns,
                    old_values=mb_old_values,
                    value_clip=ppo_cfg.value_clip,
                )

                total_loss = policy_loss + ppo_cfg.value_loss_coef * value_loss - ppo_cfg.entropy_coef * entropy

                optimizer.zero_grad()
                total_loss.backward()

                if ppo_cfg.max_grad_norm > 0.0:
                    grad_norm = clip_grad_norm_(
                        policy.parameters(),
                        ppo_cfg.max_grad_norm,
                    ).item()
                else:
                    sq_sum = 0.0
                    for param in policy.parameters():
                        if param.grad is not None:
                            sq_sum += float(torch.sum(param.grad.detach() ** 2).item())
                    grad_norm = float(sq_sum**0.5)

                optimizer.step()

                # Accumulate metrics
                metrics["policy_loss"] += float(policy_loss.item())
                metrics["value_loss"] += float(value_loss.item())
                entropy_value = float(entropy.item())
                metrics["entropy"] += entropy_value
                entropy_values.append(entropy_value)
                metrics["total_loss"] += float(total_loss.item())
                clip_value = float(clip_frac.item())
                metrics["clip_frac"] += clip_value
                metrics["adv_mean"] += float(mb_advantages.mean().item())
                batch_adv_std = float(mb_advantages.std(unbiased=False).item())
                if math.isnan(batch_adv_std) or math.isinf(batch_adv_std):
                    raise ValueError(
                        f"PPO mini-batch advantages produced invalid std "
                        f"(dataset={dataset_label_str}, batch={batch_index})"
                    )
                metrics["adv_std"] += batch_adv_std
                metrics["grad_norm"] += float(grad_norm)
                kl_value = float(torch.mean(mb_old_log_probs - new_log_probs).item())
                metrics["kl_divergence"] += kl_value
                grad_norm_max = max(grad_norm_max, float(grad_norm))
                kl_max = max(kl_max, abs(kl_value))
                if clip_value > 0.0:
                    health_tracking["clip_triggered_minibatches"] += 1.0
                health_tracking["max_clip_fraction"] = max(health_tracking["max_clip_fraction"], clip_value)
                mini_batch_updates += 1
                transitions_processed += int(idx.shape[0])

        if mini_batch_updates == 0:
            raise ValueError("No PPO mini-batch updates were performed")

        # Average metrics
        averaged_metrics = {key: value / mini_batch_updates for key, value in metrics.items()}

        # Compute additional stats
        if entropy_values:
            epoch_entropy_mean = statistics.fmean(entropy_values)
            epoch_entropy_std = statistics.pstdev(entropy_values) if len(entropy_values) > 1 else 0.0
        else:
            epoch_entropy_mean = 0.0
            epoch_entropy_std = 0.0

        reward_adv_corr = 0.0
        if reward_buffer and advantage_buffer:
            reward_arr = np.asarray(reward_buffer, dtype=np.float64)
            adv_arr = np.asarray(advantage_buffer, dtype=np.float64)
            reward_std = reward_arr.std(ddof=0)
            adv_std = adv_arr.std(ddof=0)
            if reward_std > 0 and adv_std > 0:
                reward_adv_corr = float(np.corrcoef(reward_arr, adv_arr)[0, 1])

        lr = float(optimizer.param_groups[0]["lr"])

        # Build epoch summary
        min_adv_std = health_tracking["min_adv_std"]
        if math.isinf(min_adv_std):
            min_adv_std = 0.0

        # Cumulative steps after this epoch completes
        steps_after_epoch = cumulative_steps + transitions_processed

        epoch_summary = {
            "epoch": float(epoch + 1),
            "updates": float(mini_batch_updates),
            "transitions": float(transitions_processed),
            "loss_policy": averaged_metrics["policy_loss"],
            "loss_value": averaged_metrics["value_loss"],
            "loss_entropy": averaged_metrics["entropy"],
            "loss_total": averaged_metrics["total_loss"],
            "clip_fraction": averaged_metrics["clip_frac"],
            "adv_mean": averaged_metrics["adv_mean"],
            "adv_std": averaged_metrics["adv_std"],
            "grad_norm": averaged_metrics["grad_norm"],
            "kl_divergence": averaged_metrics["kl_divergence"],
            "telemetry_version": float(PPO_TELEMETRY_VERSION),
            "lr": lr,
            "steps": float(steps_after_epoch),  # Cumulative step count across all runs
            "adv_zero_std_batches": float(health_tracking["adv_zero_std_batches"]),
            "adv_min_std": float(min_adv_std),
            "clip_triggered_minibatches": float(health_tracking["clip_triggered_minibatches"]),
            "clip_fraction_max": float(health_tracking["max_clip_fraction"]),
            "data_mode": data_mode,
            "cycle_id": float(cycle_id),
            "batch_entropy_mean": float(epoch_entropy_mean),
            "batch_entropy_std": float(epoch_entropy_std),
            "grad_norm_max": float(grad_norm_max),
            "kl_divergence_max": float(kl_max),
            "reward_advantage_corr": float(reward_adv_corr),
            "rollout_ticks": float(rollout_ticks),
            "log_stream_offset": float(log_stream_offset),
        }

        # Add conflict stats (batch-level averages)
        if conflict_acc:
            for key, value in conflict_acc.items():
                epoch_summary[f"{key}_avg"] = value / len(batches)

        # Add dataset-level social/conflict metrics for anneal guardrails
        # These are read from dataset attributes (captured during rollout or replay)
        epoch_summary["queue_conflict_events"] = float(getattr(dataset, "queue_conflict_count", 0))
        epoch_summary["queue_conflict_intensity_sum"] = float(getattr(dataset, "queue_conflict_intensity_sum", 0.0))
        epoch_summary["shared_meal_events"] = float(getattr(dataset, "shared_meal_count", 0))
        epoch_summary["late_help_events"] = float(getattr(dataset, "late_help_count", 0))
        epoch_summary["shift_takeover_events"] = float(getattr(dataset, "shift_takeover_count", 0))
        epoch_summary["chat_success_events"] = float(getattr(dataset, "chat_success_count", 0))
        epoch_summary["chat_failure_events"] = float(getattr(dataset, "chat_failure_count", 0))
        epoch_summary["chat_quality_mean"] = float(getattr(dataset, "chat_quality_mean", 0.0))

        # Add baseline metrics
        if baseline_metrics:
            epoch_summary["baseline_sample_count"] = float(baseline_metrics.get("sample_count", 0.0))
            epoch_summary["baseline_reward_mean"] = float(baseline_metrics.get("reward_mean", 0.0))
            epoch_summary["baseline_reward_sum"] = float(baseline_metrics.get("reward_sum", 0.0))
            # Add reward_sum_mean (required) and log_prob_mean (optional)
            if "reward_sum_mean" in baseline_metrics:
                epoch_summary["baseline_reward_sum_mean"] = float(baseline_metrics["reward_sum_mean"])
            if "log_prob_mean" in baseline_metrics:
                epoch_summary["baseline_log_prob_mean"] = float(baseline_metrics["log_prob_mean"])

        # Add anneal context if present
        if context.anneal_context is not None:
            anneal_fields = self._build_anneal_fields(
                context.anneal_context,
                averaged_metrics["total_loss"],
                epoch_summary,
            )
            epoch_summary.update(anneal_fields)

        # Warn about advantage issues
        if health_tracking["adv_zero_std_batches"]:
            batch_count = int(health_tracking["adv_zero_std_batches"])
            print(f"[WARN] Advantage std near zero in {batch_count} batch(es) (dataset={dataset_label_str}, epoch={epoch + 1})")

        return epoch_summary

    def _summarize_batch(self, batch: ReplayBatch, batch_index: int) -> dict[str, float]:
        """Summarize replay batch with conflict stats."""
        summary = {
            "batch": float(batch_index),
            "batch_size": float(batch.features.shape[0]),
            "feature_dim": float(batch.features.shape[1]),
        }
        for key, value in batch.conflict_stats().items():
            summary[f"conflict.{key}"] = value
        return summary

    def _ensure_finite(
        self,
        name: str,
        tensor: object,
        batch_index: int,
        dataset_label: str,
    ) -> None:
        """Ensure tensor contains no NaN/Inf values."""
        import torch

        if torch.isnan(tensor).any() or torch.isinf(tensor).any():  # type: ignore[attr-defined]
            raise ValueError(
                f"PPO {name} contained NaN/inf "
                f"(dataset={dataset_label}, batch={batch_index})"
            )

    def _update_advantage_health(
        self,
        flat_advantages: object,
        batch_index: int,
        stats: dict[str, float],
    ) -> None:
        """Update advantage health tracking stats."""
        batch_std = float(flat_advantages.std(unbiased=False).item())  # type: ignore[attr-defined]
        if math.isnan(batch_std) or math.isinf(batch_std):
            raise ValueError(f"PPO advantages produced invalid std (batch={batch_index})")
        stats["min_adv_std"] = min(stats["min_adv_std"], batch_std)
        if batch_std < 1e-8:
            stats["adv_zero_std_batches"] += 1

    def _build_anneal_fields(
        self,
        anneal_ctx: object,
        loss_total: float,
        epoch_summary: dict[str, float],
    ) -> dict[str, float | str | bool | None]:
        """Build anneal context fields for telemetry."""
        from townlet.policy.training.contexts import AnnealContext

        if not isinstance(anneal_ctx, AnnealContext):
            return {}

        # Evaluate flags
        loss_flag, queue_flag, intensity_flag = anneal_ctx.evaluate_ppo_flags(
            loss_total=loss_total,
            queue_events=epoch_summary.get("queue_conflict_events", 0.0),
            queue_intensity=epoch_summary.get("queue_conflict_intensity_sum", 0.0),
        )

        return {
            "anneal_cycle": float(anneal_ctx.cycle),
            "anneal_stage": anneal_ctx.stage,
            "anneal_dataset": anneal_ctx.dataset_label,
            "anneal_bc_accuracy": anneal_ctx.bc_accuracy,
            "anneal_bc_threshold": anneal_ctx.bc_threshold,
            "anneal_bc_passed": anneal_ctx.bc_passed,
            "anneal_loss_baseline": anneal_ctx.loss_baseline,
            "anneal_queue_baseline": anneal_ctx.queue_events_baseline,
            "anneal_intensity_baseline": anneal_ctx.queue_intensity_baseline,
            "anneal_loss_flag": loss_flag,
            "anneal_queue_flag": queue_flag,
            "anneal_intensity_flag": intensity_flag,
        }

    def _build_result_dto(
        self,
        summary: dict[str, float],
        duration_sec: float,
    ) -> PPOTrainingResultDTO:
        """Build PPOTrainingResultDTO from epoch summary."""
        from townlet.dto.policy import PPOTrainingResultDTO

        # Extract conflict fields (dynamic extras)
        conflict_fields = {
            k: v for k, v in summary.items() if k.startswith("conflict.")
        }

        # Build DTO with all fields
        result = PPOTrainingResultDTO(
            # Core metrics
            epoch=summary["epoch"],
            updates=summary["updates"],
            transitions=summary["transitions"],
            loss_policy=summary["loss_policy"],
            loss_value=summary["loss_value"],
            loss_entropy=summary["loss_entropy"],
            loss_total=summary["loss_total"],
            clip_fraction=summary["clip_fraction"],
            adv_mean=summary["adv_mean"],
            adv_std=summary["adv_std"],
            grad_norm=summary["grad_norm"],
            kl_divergence=summary["kl_divergence"],
            lr=summary["lr"],
            steps=summary["steps"],
            telemetry_version=summary.get("telemetry_version", 1.2),
            # Health tracking
            adv_zero_std_batches=summary.get("adv_zero_std_batches", 0.0),
            adv_min_std=summary.get("adv_min_std", 0.0),
            clip_triggered_minibatches=summary.get("clip_triggered_minibatches", 0.0),
            clip_fraction_max=summary.get("clip_fraction_max", 0.0),
            # Extended metrics
            epoch_duration_sec=summary.get("epoch_duration_sec"),
            data_mode=summary.get("data_mode"),
            cycle_id=summary.get("cycle_id"),
            batch_entropy_mean=summary.get("batch_entropy_mean"),
            batch_entropy_std=summary.get("batch_entropy_std"),
            grad_norm_max=summary.get("grad_norm_max"),
            kl_divergence_max=summary.get("kl_divergence_max"),
            reward_advantage_corr=summary.get("reward_advantage_corr"),
            rollout_ticks=summary.get("rollout_ticks"),
            # Anneal context
            anneal_cycle=summary.get("anneal_cycle"),
            anneal_stage=summary.get("anneal_stage"),  # type: ignore[arg-type]
            anneal_dataset=summary.get("anneal_dataset"),  # type: ignore[arg-type]
            anneal_bc_accuracy=summary.get("anneal_bc_accuracy"),
            anneal_bc_threshold=summary.get("anneal_bc_threshold"),
            anneal_bc_passed=summary.get("anneal_bc_passed"),  # type: ignore[arg-type]
            anneal_loss_baseline=summary.get("anneal_loss_baseline"),
            anneal_queue_baseline=summary.get("anneal_queue_baseline"),
            anneal_intensity_baseline=summary.get("anneal_intensity_baseline"),
            anneal_loss_flag=summary.get("anneal_loss_flag"),  # type: ignore[arg-type]
            anneal_queue_flag=summary.get("anneal_queue_flag"),  # type: ignore[arg-type]
            anneal_intensity_flag=summary.get("anneal_intensity_flag"),  # type: ignore[arg-type]
            # Baseline metrics
            baseline_sample_count=summary.get("baseline_sample_count"),
            baseline_reward_mean=summary.get("baseline_reward_mean"),
            baseline_reward_sum=summary.get("baseline_reward_sum"),
            baseline_reward_sum_mean=summary.get("baseline_reward_sum_mean"),
            baseline_log_prob_mean=summary.get("baseline_log_prob_mean"),
            # Log stream
            log_stream_offset=summary.get("log_stream_offset"),
            # Duration
            duration_sec=duration_sec,
            # Conflict fields (dynamic)
            **conflict_fields,
        )

        return result


__all__ = ["PPOStrategy"]

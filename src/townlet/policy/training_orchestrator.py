"""Policy training orchestrator module."""

from __future__ import annotations

import json
import logging
import math
import statistics
import time
from collections.abc import Iterable
from pathlib import Path

import numpy as np

from townlet.config import PPOConfig, SimulationConfig
from townlet.core.utils import is_stub_policy, policy_provider_name
from townlet.policy.bc import BCTrainer, BCTrajectoryDataset, load_bc_samples
from townlet.policy.bc import BCTrainingConfig as BCTrainingParams
from townlet.policy.models import (
    ConflictAwarePolicyConfig,
    ConflictAwarePolicyNetwork,
    TorchNotAvailableError,
    torch_available,
)
from townlet.policy.replay import (
    ReplayBatch,
    ReplayDataset,
    ReplayDatasetConfig,
    ReplaySample,
    build_batch,
    load_replay_sample,
)
from townlet.policy.replay_buffer import InMemoryReplayDataset
from townlet.policy.rollout import RolloutBuffer
from townlet.policy.trajectory_service import TrajectoryService
from townlet.stability.promotion import PromotionManager

logger = logging.getLogger(__name__)

DEFAULT_REPLAY_MANIFEST = Path("docs/samples/replay_manifest.json")

PPO_TELEMETRY_VERSION = 1.2
ANNEAL_BC_MIN_DEFAULT = 0.9
ANNEAL_LOSS_TOLERANCE_DEFAULT = 0.10
ANNEAL_QUEUE_TOLERANCE_DEFAULT = 0.15


class PolicyTrainingOrchestrator:
    """High-level PPO/BC/anneal orchestrator used by training CLIs.

    The orchestrator owns the trajectory service and exposes convenience helpers for
    replay datasets, rollout capture, behaviour-cloning, PPO, and anneal guardrails.
    SimulationLoop continues to consume PolicyRuntime; CLI tooling and notebooks
    should depend on this orchestrator (or the thin TrainingHarness alias).
    """

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self._trajectory_service = TrajectoryService()
        self._ppo_state = {"step": 0, "learning_rate": 1e-3}
        self._capture_loop = None
        self._apply_social_reward_stage(-1)
        self._anneal_context: dict[str, object] | None = None
        self._anneal_baselines: dict[str, dict[str, float]] = {}
        self._anneal_ratio: float | None = None
        self.promotion = PromotionManager(config=config, log_path=None)
        self._promotion_eval_counter = 0
        self._promotion_pass_streak = 0
        self._last_anneal_status: str | None = None

    @staticmethod
    def _ppo_ops():
        """Import PPO ops lazily to avoid Torch dependency at import time.

        Returns a module-like object with the expected functions when PyTorch
        is available; otherwise raises TorchNotAvailableError when called.
        """
        if not torch_available():  # pragma: no cover - exercised in ML-enabled envs
            raise TorchNotAvailableError(
                "PyTorch is required for PPO operations. Install the 'ml' extra."
            )
        from townlet.policy.backends.pytorch import ppo_utils as _ops  # type: ignore

        return _ops

    @property
    def transitions(self) -> dict[str, dict[str, object]]:
        """Return the mutable transition buffer keyed by agent id."""

        return self._trajectory_service.transitions

    @property
    def trajectory(self) -> list[dict[str, object]]:
        """Return the accumulated trajectory frames recorded by the orchestrator."""

        return self._trajectory_service.trajectory

    def run(self) -> None:
        """Entry point for CLI training runs based on config.training.source."""
        mode = self.config.training.source
        if mode == "bc":
            self.run_bc_training()
            return
        if mode == "anneal":
            self.run_anneal()
            return
        raise NotImplementedError(f"Training mode '{mode}' is not supported via run(); use scripts/run_training.py with --mode.")

    def current_anneal_ratio(self) -> float | None:
        return self._anneal_ratio

    def set_anneal_ratio(self, ratio: float | None) -> None:
        if ratio is None:
            self._anneal_ratio = None
        else:
            clamped = max(0.0, min(1.0, float(ratio)))
            self._anneal_ratio = clamped

    def run_replay(self, sample_path: Path, meta_path: Path | None = None) -> dict[str, float]:
        """Load a replay observation sample and surface conflict-aware stats."""
        sample: ReplaySample = load_replay_sample(sample_path, meta_path)
        batch = build_batch([sample])
        summary = self._summarise_batch(batch, batch_index=1)
        print("Replay sample loaded:", summary)
        return summary

    def run_replay_batch(self, pairs: Iterable[tuple[Path, Path | None]]) -> dict[str, float]:
        entries = list(pairs)
        if not entries:
            raise ValueError("Replay batch requires at least one entry")
        config = ReplayDatasetConfig(entries=entries, batch_size=len(entries))
        return self.run_replay_dataset(config)

    def run_replay_dataset(self, dataset_config: ReplayDatasetConfig | ReplayDataset) -> dict[str, float]:
        if isinstance(dataset_config, ReplayDatasetConfig):
            dataset: ReplayDataset | Iterable[ReplayBatch] = ReplayDataset(dataset_config)
        else:
            dataset = dataset_config
        summary: dict[str, float] = {}
        for idx, batch in enumerate(dataset, start=1):
            summary = self._summarise_batch(batch, batch_index=idx)
            print(f"Replay batch {idx}:", summary)
        if not summary:
            raise ValueError("Replay dataset yielded no batches")
        return summary

    def capture_rollout(
        self,
        ticks: int,
        auto_seed_agents: bool = False,
        output_dir: Path | None = None,
        prefix: str = "rollout_sample",
        compress: bool = True,
    ) -> RolloutBuffer:
        """Run the simulation loop for a fixed number of ticks and collect frames."""

        if ticks <= 0:
            raise ValueError("ticks must be positive to capture a rollout")

        from townlet.core.sim_loop import (
            SimulationLoop,
        )  # delayed import to avoid cycles
        from townlet.policy.scenario_utils import (
            apply_scenario,
            has_agents,
            seed_default_agents,
        )

        loop = SimulationLoop(self.config)
        scenario_config = getattr(self.config, "scenario", None)
        if scenario_config:
            apply_scenario(loop, scenario_config)
        elif auto_seed_agents and not loop.world.agents:
            seed_default_agents(loop)
        if not has_agents(loop):
            raise ValueError("No agents available for rollout capture. Provide a scenario or use auto seeding.")

        buffer = RolloutBuffer()
        provider = policy_provider_name(loop)
        if is_stub_policy(loop.policy, provider):
            logger.warning(
                "capture_rollout_stub_policy provider=%s message='Stub policy backend active; no trajectories captured.'",
                provider,
            )
            return buffer
        for _ in range(ticks):
            loop.step()
            frames = loop.policy.collect_trajectory(clear=True)
            if frames:
                buffer.extend(frames)
            buffer.record_events(loop.telemetry.latest_events())
        leftover_frames = loop.policy.collect_trajectory(clear=True)
        if leftover_frames:
            buffer.extend(leftover_frames)
        buffer.set_tick_count(ticks)

        if output_dir is not None:
            buffer.save(output_dir, prefix=prefix, compress=compress)
        return buffer

    def run_rollout_ppo(
        self,
        ticks: int,
        batch_size: int = 1,
        auto_seed_agents: bool = False,
        output_dir: Path | None = None,
        prefix: str = "rollout_sample",
        compress: bool = True,
        epochs: int = 1,
        log_path: Path | None = None,
        log_frequency: int = 1,
        max_log_entries: int | None = None,
    ) -> dict[str, float]:
        next_cycle = int(self._ppo_state.get("cycle_id", -1)) + 1
        self._apply_social_reward_stage(next_cycle)
        buffer = self.capture_rollout(
            ticks=ticks,
            auto_seed_agents=auto_seed_agents,
            output_dir=output_dir,
            prefix=prefix,
            compress=compress,
        )
        dataset = buffer.build_dataset(batch_size=batch_size)
        return self.run_ppo(
            dataset_config=None,
            epochs=epochs,
            log_path=log_path,
            log_frequency=log_frequency,
            max_log_entries=max_log_entries,
            in_memory_dataset=dataset,
        )

    def _load_bc_dataset(self, manifest: Path) -> BCTrajectoryDataset:
        samples = load_bc_samples(manifest)
        return BCTrajectoryDataset(samples)

    def run_bc_training(
        self,
        *,
        manifest: Path | None = None,
        config: BCTrainingParams | None = None,
    ) -> dict[str, float]:
        if not torch_available():
            raise TorchNotAvailableError("PyTorch is required for behaviour cloning training")

        bc_settings = self.config.training.bc
        manifest_path = Path(manifest) if manifest is not None else bc_settings.manifest
        if manifest_path is None:
            raise ValueError("BC manifest is required for behaviour cloning")

        dataset = self._load_bc_dataset(manifest_path)
        params = config or BCTrainingParams(
            learning_rate=bc_settings.learning_rate,
            batch_size=bc_settings.batch_size,
            epochs=bc_settings.epochs,
            weight_decay=bc_settings.weight_decay,
            device=bc_settings.device,
        )

        policy_cfg = ConflictAwarePolicyConfig(
            feature_dim=dataset.feature_dim,
            map_shape=dataset.map_shape,
            action_dim=dataset.action_dim,
        )
        trainer = BCTrainer(params, policy_cfg)
        metrics = trainer.fit(dataset)
        metrics.update(
            {
                "mode": "bc",
                "manifest": str(manifest_path),
            }
        )
        return metrics

    def run_anneal(
        self,
        *,
        dataset_config: ReplayDatasetConfig | None = None,
        in_memory_dataset: InMemoryReplayDataset | None = None,
        log_dir: Path | None = None,
        bc_manifest: Path | None = None,
    ) -> list[dict[str, object]]:
        schedule = sorted(
            self.config.training.anneal_schedule,
            key=lambda stage: stage.cycle,
        )
        if not schedule:
            raise ValueError("anneal_schedule is empty; configure training.anneal_schedule in config")

        if dataset_config is None and in_memory_dataset is None:
            replay_manifest = self.config.training.replay_manifest
            if replay_manifest is None:
                raise ValueError("Replay manifest required for PPO stages in anneal")
            dataset_config = ReplayDatasetConfig.from_manifest(Path(replay_manifest))

        bc_threshold = float(self.config.training.anneal_accuracy_threshold)
        results: list[dict[str, object]] = []
        last_bc_stage: dict[str, object] | None = None
        dataset_label = None
        if dataset_config is not None:
            dataset_label = dataset_config.label
        elif in_memory_dataset is not None:
            dataset_label = getattr(in_memory_dataset, "label", None)
        dataset_key = str(dataset_label or "anneal_dataset")

        baselines = self._anneal_baselines.setdefault(dataset_key, {})

        for stage in schedule:
            if stage.mode == "bc":
                self.set_anneal_ratio(float(stage.bc_weight))
                metrics = self.run_bc_training(manifest=bc_manifest)
                accuracy = float(metrics.get("accuracy", 0.0))
                stage_result: dict[str, object] = {
                    "cycle": float(stage.cycle),
                    "mode": "bc",
                    "accuracy": accuracy,
                    "loss": float(metrics.get("loss", 0.0)),
                    "threshold": bc_threshold,
                    "passed": accuracy >= bc_threshold,
                    "bc_weight": float(stage.bc_weight),
                }
                results.append(stage_result)
                last_bc_stage = stage_result
                if not stage_result["passed"]:
                    stage_result["rolled_back"] = True
                    break
            else:
                self.set_anneal_ratio(0.0)
                context: dict[str, object] = {
                    "cycle": float(stage.cycle),
                    "stage": stage.mode,
                    "dataset_label": dataset_key,
                    "bc_accuracy": (last_bc_stage.get("accuracy") if last_bc_stage else None),
                    "bc_threshold": bc_threshold,
                    "bc_passed": (last_bc_stage.get("passed", True) if last_bc_stage else True),
                    "loss_baseline": baselines.get("loss_total"),
                    "queue_events_baseline": baselines.get("queue_conflict_events"),
                    "queue_intensity_baseline": baselines.get("queue_conflict_intensity"),
                    "loss_tolerance": ANNEAL_LOSS_TOLERANCE_DEFAULT,
                    "queue_tolerance": ANNEAL_QUEUE_TOLERANCE_DEFAULT,
                }
                self._anneal_context = context
                try:
                    summary = self.run_ppo(
                        dataset_config=dataset_config,
                        in_memory_dataset=in_memory_dataset,
                        epochs=stage.epochs,
                    )
                finally:
                    self._anneal_context = None
                baselines["loss_total"] = float(summary.get("loss_total", 0.0))
                baselines["queue_conflict_events"] = float(summary.get("queue_conflict_events", 0.0))
                baselines["queue_conflict_intensity"] = float(summary.get("queue_conflict_intensity_sum", 0.0))
                summary_result = {
                    "cycle": float(stage.cycle),
                    "mode": "ppo",
                    **summary,
                }
                results.append(summary_result)

        if log_dir is not None:
            log_dir.mkdir(parents=True, exist_ok=True)
            (log_dir / "anneal_results.json").write_text(json.dumps(results, indent=2))
        status = self.evaluate_anneal_results(results)
        self._last_anneal_status = status
        self._record_promotion_evaluation(status=status, results=results)
        return results

    def run_ppo(
        self,
        dataset_config: ReplayDatasetConfig | None = None,
        epochs: int = 1,
        log_path: Path | None = None,
        log_frequency: int = 1,
        max_log_entries: int | None = None,
        in_memory_dataset: InMemoryReplayDataset | None = None,
        device_str: str | None = None,
    ) -> dict[str, float]:
        if not torch_available():
            raise TorchNotAvailableError("PyTorch is required for PPO training. Install torch to proceed.")

        if in_memory_dataset is not None:
            dataset: InMemoryReplayDataset | ReplayDataset = in_memory_dataset
        else:
            if dataset_config is None:
                raise ValueError("dataset_config is required when in_memory_dataset is not provided")
            dataset = ReplayDataset(dataset_config)
        if len(dataset) == 0:
            raise ValueError("Replay dataset yielded no batches")

        batches: list[ReplayBatch] = list(dataset)
        if not batches:
            raise ValueError("Replay dataset yielded no batches")

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

        import torch
        from torch.distributions import Categorical
        from torch.nn.utils import clip_grad_norm_

        if self.config.ppo is None:
            self.config.ppo = PPOConfig()
        ppo_cfg = self.config.ppo

        # Prefer CUDA if available for faster training; fallback to CPU. Allow
        # explicit override via device_str (e.g., 'cuda:1', 'cpu').
        if device_str:
            device = torch.device(device_str)
        else:
            if torch.cuda.is_available():
                # Pick the CUDA device with the most free memory to avoid clashing
                # with other workloads (e.g., LLMs) on multi-GPU systems.
                try:
                    best_idx = 0
                    best_free = -1
                    for i in range(torch.cuda.device_count()):
                        free_bytes, _total = torch.cuda.mem_get_info(i)  # type: ignore[attr-defined]
                        if free_bytes > best_free:
                            best_free = int(free_bytes)
                            best_idx = i
                    device = torch.device(f"cuda:{best_idx}")
                except Exception:
                    device = torch.device("cuda")
            else:
                device = torch.device("cpu")
        dev_name = None
        try:  # best-effort device logging
            if device.type == "cuda":
                idx = device.index if device.index is not None else torch.cuda.current_device()
                dev_name = torch.cuda.get_device_name(idx)
        except Exception:  # pragma: no cover - logging only
            pass
        logger.info("PPO device selected: %s%s", device, f" ({dev_name})" if dev_name else "")
        print(f"PPO device selected: {device}{f' ({dev_name})' if dev_name else ''}")
        try:
            if device.type == "cuda":
                torch.cuda.set_device(device)
                torch.backends.cudnn.benchmark = True  # speed up fixed-shape convs
                # Emit a quick memory snapshot to prove CUDA context is live
                mem = torch.cuda.memory_allocated(device)
                print(f"CUDA memory allocated (bytes): {int(mem)}")
        except Exception:  # pragma: no cover - best-effort
            pass
        policy = self.build_policy_network(feature_dim, map_shape, action_dim)
        policy.train()
        policy.to(device)

        optimizer = torch.optim.Adam(policy.parameters(), lr=ppo_cfg.learning_rate)
        self._ppo_state["learning_rate"] = float(ppo_cfg.learning_rate)
        generator = torch.Generator(device=device)

        dataset_label = getattr(dataset, "label", None)
        dataset_label_str = str(
            dataset_label or (getattr(dataset_config, "label", None) if dataset_config is not None else None) or "training_dataset"
        )

        def _ensure_finite(name: str, tensor: torch.Tensor, batch_index: int) -> None:
            if torch.isnan(tensor).any() or torch.isinf(tensor).any():
                raise ValueError(f"PPO {name} contained NaN/inf (dataset={dataset_label_str}, batch={batch_index})")

        def _update_advantage_health(
            flat_advantages: torch.Tensor,
            *,
            batch_index: int,
            stats: dict[str, float],
        ) -> None:
            batch_std = float(flat_advantages.std(unbiased=False).item())
            if math.isnan(batch_std) or math.isinf(batch_std):
                raise ValueError(f"PPO advantages produced invalid std (dataset={dataset_label_str}, batch={batch_index})")
            stats["min_adv_std"] = min(stats["min_adv_std"], batch_std)
            if batch_std < 1e-8:
                stats["adv_zero_std_batches"] += 1

        log_frequency = max(1, int(log_frequency or 1))
        max_log_entries = max_log_entries if max_log_entries and max_log_entries > 0 else None

        log_handle = None
        log_entries_written = 0
        rotation_index = 0

        cycle_id = int(self._ppo_state.get("cycle_id", -1))
        if isinstance(dataset, InMemoryReplayDataset):
            cycle_id += 1
            self._ppo_state["cycle_id"] = cycle_id
        else:
            cycle_id = max(cycle_id, 0)
        self._apply_social_reward_stage(cycle_id)

        data_mode = "replay"
        rollout_ticks = 0
        if in_memory_dataset is not None and dataset_config is not None:
            data_mode = "mixed"
            rollout_ticks = int(getattr(in_memory_dataset, "rollout_ticks", 0))
        elif isinstance(dataset, InMemoryReplayDataset):
            data_mode = "rollout"
            rollout_ticks = int(getattr(dataset, "rollout_ticks", 0))

        log_stream_offset = int(self._ppo_state.get("log_stream_offset", 0))

        def _open_log(target_path: Path) -> None:
            nonlocal log_handle
            target_path.parent.mkdir(parents=True, exist_ok=True)
            log_handle = target_path.open("a", encoding="utf-8", buffering=1)

        if log_path is not None:
            _open_log(log_path)
        last_summary: dict[str, float] = {}
        for epoch in range(epochs):
            epoch_start = time.perf_counter()
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
                batch_summary = self._summarise_batch(batch, batch_index=batch_index)
                for key, value in batch_summary.items():
                    if key.startswith("conflict."):
                        conflict_acc[key] = conflict_acc.get(key, 0.0) + value

                maps = torch.from_numpy(batch.maps).float().to(device, non_blocking=True)
                features = torch.from_numpy(batch.features).float().to(device, non_blocking=True)
                actions = torch.from_numpy(batch.actions).long().to(device, non_blocking=True)
                old_log_probs = torch.from_numpy(batch.old_log_probs).float().to(device, non_blocking=True)
                rewards = torch.from_numpy(batch.rewards).float().to(device, non_blocking=True)
                dones = torch.from_numpy(batch.dones.astype(np.float32)).float().to(device, non_blocking=True)
                value_preds_old = torch.from_numpy(batch.value_preds).float().to(device, non_blocking=True)

                ops = self._ppo_ops()
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
                # Derive baseline per-batch using that batch's timestep length.
                # In rollout/mixed modes, batches may differ in timesteps when
                # batch_size == 1, so using a fixed value from the first batch
                # can be incorrect and cause shape errors.
                flat_advantages = advantages.reshape(-1)
                flat_returns = returns.reshape(-1)
                _ensure_finite("advantages", flat_advantages, batch_index)
                _ensure_finite("returns", flat_returns, batch_index)
                _update_advantage_health(flat_advantages, batch_index=batch_index, stats=health_tracking)

                reward_buffer.extend(batch.rewards.astype(float).reshape(-1).tolist())
                advantage_buffer.extend(advantages.cpu().numpy().astype(float).reshape(-1).tolist())

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
                # Ensure the permutation tensor and RNG live on the same device
                perm = torch.randperm(
                    total_transitions,
                    device=flat_actions.device,
                    generator=generator,
                )

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
                            f"PPO mini-batch advantages produced invalid std (dataset={dataset_label_str}, batch={batch_index})"
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

            averaged_metrics = {key: value / mini_batch_updates for key, value in metrics.items()}

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
            self._ppo_state["learning_rate"] = lr
            self._ppo_state["step"] = int(self._ppo_state.get("step", 0)) + transitions_processed

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
                "steps": float(self._ppo_state["step"]),
            }

            min_adv_std = health_tracking["min_adv_std"]
            if math.isinf(min_adv_std):
                min_adv_std = 0.0
            epoch_summary.update(
                {
                    "adv_zero_std_batches": float(health_tracking["adv_zero_std_batches"]),
                    "adv_min_std": float(min_adv_std),
                    "clip_triggered_minibatches": float(health_tracking["clip_triggered_minibatches"]),
                    "clip_fraction_max": float(health_tracking["max_clip_fraction"]),
                }
            )

            if health_tracking["adv_zero_std_batches"]:
                batch_count = int(health_tracking["adv_zero_std_batches"])
                print(f"[WARN] Advantage std near zero in {batch_count} batch(es) (dataset={dataset_label_str}, epoch={epoch + 1})")

            if PPO_TELEMETRY_VERSION >= 1.1:
                epoch_summary.update(
                    {
                        "epoch_duration_sec": float(time.perf_counter() - epoch_start),
                        "data_mode": data_mode,
                        "cycle_id": float(cycle_id),
                        "batch_entropy_mean": float(epoch_entropy_mean),
                        "batch_entropy_std": float(epoch_entropy_std),
                        "grad_norm_max": float(grad_norm_max),
                        "kl_divergence_max": float(kl_max),
                        "reward_advantage_corr": float(reward_adv_corr),
                        "rollout_ticks": float(rollout_ticks),
                        "log_stream_offset": float(log_stream_offset + 1),
                        "queue_conflict_events": float(getattr(dataset, "queue_conflict_count", 0)),
                        "queue_conflict_intensity_sum": float(getattr(dataset, "queue_conflict_intensity_sum", 0.0)),
                        "shared_meal_events": float(getattr(dataset, "shared_meal_count", 0)),
                        "late_help_events": float(getattr(dataset, "late_help_count", 0)),
                        "shift_takeover_events": float(getattr(dataset, "shift_takeover_count", 0)),
                        "chat_success_events": float(getattr(dataset, "chat_success_count", 0)),
                        "chat_failure_events": float(getattr(dataset, "chat_failure_count", 0)),
                        "chat_quality_mean": float(getattr(dataset, "chat_quality_mean", 0.0)),
                    }
                )
                log_stream_offset += 1

            anneal_context = getattr(self, "_anneal_context", None)
            if PPO_TELEMETRY_VERSION >= 1.2 and anneal_context:
                bc_accuracy_value = anneal_context.get("bc_accuracy")
                bc_threshold_value = anneal_context.get("bc_threshold")
                loss_baseline = anneal_context.get("loss_baseline")
                queue_baseline = anneal_context.get("queue_events_baseline")
                intensity_baseline = anneal_context.get("queue_intensity_baseline")
                loss_tolerance = float(anneal_context.get("loss_tolerance", ANNEAL_LOSS_TOLERANCE_DEFAULT))
                queue_tolerance = float(anneal_context.get("queue_tolerance", ANNEAL_QUEUE_TOLERANCE_DEFAULT))
                loss_total_value = averaged_metrics["total_loss"]
                queue_events_value = float(epoch_summary.get("queue_conflict_events", 0.0))
                queue_intensity_value = float(epoch_summary.get("queue_conflict_intensity_sum", 0.0))

                loss_flag = False
                if isinstance(loss_baseline, (int, float)) and loss_baseline:
                    loss_flag = (abs(loss_total_value - float(loss_baseline)) / abs(float(loss_baseline))) > loss_tolerance

                queue_flag = False
                if isinstance(queue_baseline, (int, float)) and queue_baseline:
                    queue_flag = queue_events_value < (1.0 - queue_tolerance) * float(queue_baseline)

                intensity_flag = False
                if isinstance(intensity_baseline, (int, float)) and intensity_baseline:
                    intensity_flag = queue_intensity_value < ((1.0 - queue_tolerance) * float(intensity_baseline))

                epoch_summary.update(
                    {
                        "anneal_cycle": float(anneal_context.get("cycle", -1.0)),
                        "anneal_stage": str(anneal_context.get("stage", "")),
                        "anneal_dataset": str(anneal_context.get("dataset_label", "")),
                        "anneal_bc_accuracy": (float(bc_accuracy_value) if isinstance(bc_accuracy_value, (int, float)) else None),
                        "anneal_bc_threshold": (
                            float(bc_threshold_value)
                            if isinstance(bc_threshold_value, (int, float))
                            else float(self.config.training.anneal_accuracy_threshold)
                        ),
                        "anneal_bc_passed": bool(anneal_context.get("bc_passed", True)),
                        "anneal_loss_baseline": (float(loss_baseline) if isinstance(loss_baseline, (int, float)) else None),
                        "anneal_queue_baseline": (float(queue_baseline) if isinstance(queue_baseline, (int, float)) else None),
                        "anneal_intensity_baseline": (float(intensity_baseline) if isinstance(intensity_baseline, (int, float)) else None),
                        "anneal_loss_flag": bool(loss_flag),
                        "anneal_queue_flag": bool(queue_flag),
                        "anneal_intensity_flag": bool(intensity_flag),
                    }
                )
            if baseline_metrics:
                epoch_summary["baseline_sample_count"] = float(baseline_metrics.get("sample_count", 0.0))
                epoch_summary["baseline_reward_mean"] = float(baseline_metrics.get("reward_mean", 0.0))
                epoch_summary["baseline_reward_sum"] = float(baseline_metrics.get("reward_sum", 0.0))
                if "reward_sum_mean" in baseline_metrics:
                    epoch_summary["baseline_reward_sum_mean"] = float(baseline_metrics.get("reward_sum_mean", 0.0))
                if "log_prob_mean" in baseline_metrics:
                    epoch_summary["baseline_log_prob_mean"] = float(baseline_metrics.get("log_prob_mean", 0.0))
            if conflict_acc:
                for key, value in conflict_acc.items():
                    epoch_summary[f"{key}_avg"] = value / len(batches)

            print(f"PPO epoch {epoch + 1}:", epoch_summary)
            should_log_epoch = log_handle is not None and ((epoch + 1) % log_frequency == 0)
            if should_log_epoch and log_path is not None:
                if max_log_entries is not None and log_entries_written >= max_log_entries:
                    assert log_handle is not None
                    log_handle.close()
                    rotation_index += 1
                    rotated_path = log_path.with_name(f"{log_path.name}.{rotation_index}")
                    _open_log(rotated_path)
                    log_entries_written = 0
                assert log_handle is not None
                log_handle.write(json.dumps(epoch_summary) + "\n")
                log_handle.flush()
                log_entries_written += 1
            last_summary = epoch_summary
        if log_handle is not None:
            log_handle.close()
        if PPO_TELEMETRY_VERSION >= 1.1:
            self._ppo_state["log_stream_offset"] = log_stream_offset
        return last_summary

    def evaluate_anneal_results(self, results: list[dict[str, object]]) -> str:
        status = "PASS"
        for stage in results:
            mode = stage.get("mode")
            if mode == "bc" and not stage.get("passed", True):
                return "FAIL"
            if mode == "ppo" and (
                bool(stage.get("anneal_loss_flag")) or bool(stage.get("anneal_queue_flag")) or bool(stage.get("anneal_intensity_flag"))
            ):
                status = "HOLD"
        return status

    @property
    def last_anneal_status(self) -> str | None:
        return self._last_anneal_status

    def _record_promotion_evaluation(
        self,
        *,
        status: str,
        results: list[dict[str, object]],
    ) -> None:
        self._promotion_eval_counter += 1
        evaluation_tick = self._promotion_eval_counter
        required = self.config.stability.promotion.required_passes
        if status == "PASS":
            self._promotion_pass_streak += 1
            last_result = "pass"
        else:
            self._promotion_pass_streak = 0
            last_result = "fail"
        candidate_ready = self._promotion_pass_streak >= required
        promotion_metrics = {
            "promotion": {
                "pass_streak": self._promotion_pass_streak,
                "required_passes": required,
                "candidate_ready": candidate_ready,
                "last_result": last_result,
                "last_evaluated_tick": evaluation_tick,
            }
        }
        self.promotion.update_from_metrics(
            promotion_metrics,
            tick=evaluation_tick,
        )
        if status == "PASS":
            metadata = {
                "status": status,
                "cycle": results[-1].get("cycle") if results else None,
                "mode": results[-1].get("mode") if results else None,
            }
            self.promotion.set_candidate_metadata(metadata)
        else:
            self.promotion.set_candidate_metadata(None)

    def _select_social_reward_stage(self, cycle_id: int) -> str | None:
        training_cfg = getattr(self.config, "training", None)
        if training_cfg is None:
            return None
        stage = getattr(training_cfg, "social_reward_stage_override", None)
        schedule = getattr(training_cfg, "social_reward_schedule", []) or []
        try:
            iterable = sorted(
                schedule,
                key=lambda entry: int(getattr(entry, "cycle", 0)),
            )
        except TypeError:
            iterable = []
        for entry in iterable:
            entry_cycle = int(getattr(entry, "cycle", 0))
            if cycle_id >= entry_cycle:
                stage = getattr(entry, "stage", stage)
        return stage

    def _apply_social_reward_stage(self, cycle_id: int) -> None:
        stage = self._select_social_reward_stage(cycle_id)
        if stage is None:
            return
        current = getattr(self.config.features.stages, "social_rewards", None)
        if stage != current:
            self.config.features.stages.social_rewards = stage

    def _summarise_batch(self, batch: ReplayBatch, batch_index: int) -> dict[str, float]:
        summary = {
            "batch": float(batch_index),
            "batch_size": float(batch.features.shape[0]),
            "feature_dim": float(batch.features.shape[1]),
        }
        for key, value in batch.conflict_stats().items():
            summary[f"conflict.{key}"] = value
        return summary

    def _resolve_replay_manifest(self, manifest: Path | str | None) -> Path:
        candidates: list[Path] = []
        for value in (manifest, getattr(self.config.training, "replay_manifest", None)):
            if value:
                path = Path(value)
                candidates.append(path)
                candidates.append(Path.cwd() / path)
        repo_root = Path(__file__).resolve().parents[3]
        candidates.append(repo_root / DEFAULT_REPLAY_MANIFEST)
        candidates.append(Path.cwd() / DEFAULT_REPLAY_MANIFEST)
        checked: set[str] = set()
        for candidate in candidates:
            expanded = candidate.expanduser()
            resolved = expanded.resolve(strict=False)
            key = str(resolved)
            if key in checked:
                continue
            checked.add(key)
            if resolved.exists():
                return resolved
        raise FileNotFoundError(
            "Replay manifest not provided and default manifest could not be located",
        )

    def build_replay_dataset(self, config: ReplayDatasetConfig | Path | str | None = None) -> ReplayDataset:
        if isinstance(config, ReplayDatasetConfig):
            dataset_config = config
        else:
            manifest_path = self._resolve_replay_manifest(config)
            dataset_config = ReplayDatasetConfig.from_manifest(manifest_path)
        return ReplayDataset(dataset_config)

    def build_policy_network(
        self,
        feature_dim: int,
        map_shape: tuple[int, int, int],
        action_dim: int,
        hidden_dim: int | None = None,
    ) -> ConflictAwarePolicyNetwork:
        if not torch_available():
            raise TorchNotAvailableError("PyTorch is required to build the policy network. Install torch or disable PPO.")
        cfg = ConflictAwarePolicyConfig(
            feature_dim=feature_dim,
            map_shape=map_shape,
            action_dim=action_dim,
            hidden_dim=hidden_dim or 256,
        )
        return ConflictAwarePolicyNetwork(cfg)


__all__ = ["PolicyTrainingOrchestrator"]

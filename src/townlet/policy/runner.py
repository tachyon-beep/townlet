"""Policy orchestration scaffolding."""
from __future__ import annotations

import json
import statistics
import time
from collections.abc import Iterable
from pathlib import Path

import numpy as np

from townlet.config import PPOConfig, SimulationConfig
from townlet.policy.behavior import AgentIntent, BehaviorController, build_behavior
from townlet.policy.models import (
    ConflictAwarePolicyConfig,
    ConflictAwarePolicyNetwork,
    TorchNotAvailableError,
    torch_available,
)
from townlet.policy.bc import (
    BCTrainer,
    BCTrainingConfig as BCTrainingParams,
    BCTrajectoryDataset,
    evaluate_bc_policy,
    load_bc_samples,
)
from townlet.policy.ppo.utils import (
    AdvantageReturns,
    clipped_value_loss,
    compute_gae,
    normalize_advantages,
    policy_surrogate,
    value_baseline_from_old_preds,
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
from townlet.world.grid import WorldState

PPO_TELEMETRY_VERSION = 1.1


class PolicyRuntime:
    """Bridges the simulation with PPO/backends via PettingZoo."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.behavior: BehaviorController = build_behavior(config)
        self._transitions: dict[str, dict[str, object]] = {}
        self._trajectory: list[dict[str, object]] = []
        self._tick: int = 0
        self._action_lookup: dict[str, int] = {}
        self._action_inverse: dict[int, str] = {}
        self._policy_net: ConflictAwarePolicyNetwork | None = None
        self._policy_map_shape: tuple[int, int, int] | None = None
        self._policy_feature_dim: int | None = None
        self._policy_action_dim: int = 0

    def decide(self, world: WorldState, tick: int) -> dict[str, object]:
        """Return a primitive action per agent."""
        self._tick = tick
        actions: dict[str, object] = {}
        for agent_id in world.agents:
            intent: AgentIntent = self.behavior.decide(world, agent_id)
            if intent.kind == "wait":
                actions[agent_id] = {"kind": "wait"}
            else:
                actions[agent_id] = {
                    "kind": intent.kind,
                    "object": intent.object_id,
                    "affordance": intent.affordance_id,
                    "blocked": intent.blocked,
                }
            action_payload = actions[agent_id]
            try:
                action_key = json.dumps(action_payload, sort_keys=True)
            except TypeError:
                action_key = str(action_payload)
            if action_key not in self._action_lookup:
                action_id = len(self._action_lookup)
                self._action_lookup[action_key] = action_id
                self._action_inverse[action_id] = action_key
            action_id = self._action_lookup[action_key]
            entry = self._transitions.setdefault(agent_id, {})
            entry["action"] = action_payload
            entry["action_id"] = action_id
        return actions

    def post_step(self, rewards: dict[str, float], terminated: dict[str, bool]) -> None:
        """Record rewards and termination signals into buffers."""
        for agent_id, reward in rewards.items():
            entry = self._transitions.setdefault(agent_id, {})
            entry.setdefault("rewards", []).append(reward)
            entry.setdefault("dones", []).append(bool(terminated.get(agent_id, False)))

    def flush_transitions(
        self, observations: dict[str, dict[str, object]]
    ) -> list[dict[str, object]]:
        """Combine stored transition data with observations and return trajectory frames."""
        frames: list[dict[str, object]] = []
        for agent_id, payload in observations.items():
            entry = self._transitions.get(agent_id, {})
            frame = {
                "tick": self._tick,
                "agent_id": agent_id,
                "map": payload.get("map"),
                "features": payload.get("features"),
                "metadata": payload.get("metadata"),
                "action": entry.get("action"),
                "action_id": entry.get("action_id"),
                "rewards": entry.get("rewards", []),
                "dones": entry.get("dones", []),
                "action_lookup": dict(self._action_inverse),
            }
            self._annotate_with_policy_outputs(frame)
            frames.append(frame)
        self._trajectory.extend(frames)
        self._transitions.clear()
        return frames

    def collect_trajectory(self, clear: bool = True) -> list[dict[str, object]]:
        """Return accumulated trajectory frames and reset internal buffer."""
        result = list(self._trajectory)
        if clear:
            self._trajectory.clear()
        return result

    def reset_state(self) -> None:
        """Reset transient buffers so snapshot loads don’t duplicate data."""

        self._transitions.clear()
        self._trajectory.clear()

    def _annotate_with_policy_outputs(self, frame: dict[str, object]) -> None:
        if not torch_available():  # pragma: no cover - torch optional
            frame.setdefault("log_prob", 0.0)
            frame.setdefault("value_pred", 0.0)
            return

        map_tensor = frame.get("map")
        features = frame.get("features")
        action_id = frame.get("action_id")
        if map_tensor is None or features is None or action_id is None:
            frame.setdefault("log_prob", 0.0)
            frame.setdefault("value_pred", 0.0)
            return

        map_array = np.asarray(map_tensor, dtype=np.float32)
        feature_array = np.asarray(features, dtype=np.float32)
        if map_array.ndim != 3 or feature_array.ndim != 1:
            frame.setdefault("log_prob", 0.0)
            frame.setdefault("value_pred", 0.0)
            return

        action_dim = max(len(self._action_lookup), 1)
        if not self._ensure_policy_network(map_array.shape, feature_array.shape[0], action_dim):
            frame.setdefault("log_prob", 0.0)
            frame.setdefault("value_pred", 0.0)
            return

        import torch

        map_batch = torch.from_numpy(map_array).unsqueeze(0)
        feature_batch = torch.from_numpy(feature_array).unsqueeze(0)

        assert self._policy_net is not None
        self._policy_net.eval()
        with torch.no_grad():
            logits, value = self._policy_net(map_batch, feature_batch)
            valid_dim = min(logits.shape[-1], action_dim)
            logits = logits[..., :valid_dim]
            log_probs = torch.log_softmax(logits, dim=-1)
            clipped_action = int(min(action_id, valid_dim - 1))
            log_prob = log_probs[0, clipped_action].item()
            value_pred = value[0].item()
        frame["log_prob"] = log_prob
        frame["value_pred"] = value_pred
        frame["logits"] = logits.squeeze(0).cpu().numpy()

    def _ensure_policy_network(
        self,
        map_shape: tuple[int, int, int],
        feature_dim: int,
        action_dim: int,
    ) -> bool:
        if not torch_available():  # pragma: no cover - torch optional
            return False

        rebuild = False
        if self._policy_net is None:
            rebuild = True
        elif (
            self._policy_map_shape != map_shape
            or self._policy_feature_dim != feature_dim
            or self._policy_action_dim != action_dim
        ):
            rebuild = True

        if rebuild:
            try:
                import torch

                torch.manual_seed(0)
                policy = self._build_policy_network(
                    feature_dim=feature_dim,
                    map_shape=map_shape,
                    action_dim=action_dim,
                )
            except TorchNotAvailableError:  # pragma: no cover - guard
                return False
            self._policy_net = policy
            self._policy_map_shape = map_shape
            self._policy_feature_dim = feature_dim
            self._policy_action_dim = action_dim
        return self._policy_net is not None

    def _build_policy_network(
        self,
        feature_dim: int,
        map_shape: tuple[int, int, int],
        action_dim: int,
    ) -> ConflictAwarePolicyNetwork:
        config = ConflictAwarePolicyConfig(
            feature_dim=feature_dim,
            map_shape=map_shape,
            action_dim=action_dim,
        )
        return ConflictAwarePolicyNetwork(config)


class TrainingHarness:
    """Coordinates RL training sessions."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self._ppo_state = {"step": 0, "learning_rate": 1e-3}
        # TODO(@townlet): Wire up PPO trainer, evaluators, and promotion hooks.
        self._capture_loop = None
        self._apply_social_reward_stage(-1)

    def run(self) -> None:
        """Entry point for CLI training runs."""
        raise NotImplementedError("Training harness not yet implemented")

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

    def run_replay_dataset(self, dataset_config: ReplayDatasetConfig) -> dict[str, float]:
        dataset = ReplayDataset(dataset_config)
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

        from townlet.core.sim_loop import SimulationLoop  # delayed import to avoid cycles
        from townlet.policy.scenario_utils import (
            apply_scenario,
            has_agents,
            seed_default_agents,
        )

        if self._capture_loop is None:
            self._capture_loop = SimulationLoop(self.config)
        else:
            self._capture_loop.reset()
        loop = self._capture_loop
        scenario_config = getattr(self.config, "scenario", None)
        if scenario_config:
            apply_scenario(loop, scenario_config)
        elif auto_seed_agents and not loop.world.agents:
            seed_default_agents(loop)
        if not has_agents(loop):
            raise ValueError(
                "No agents available for rollout capture. Provide a scenario or use auto seeding."
            )

        buffer = RolloutBuffer()
        for _ in range(ticks):
            loop.step()
            frames = loop.policy.collect_trajectory(clear=True)
            buffer.extend(frames)
            buffer.record_events(loop.telemetry.latest_events())
        buffer.extend(loop.policy.collect_trajectory(clear=True))
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

        for stage in schedule:
            if stage.mode == "bc":
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
                if not stage_result["passed"]:
                    stage_result["rolled_back"] = True
                    break
            else:
                summary = self.run_ppo(
                    dataset_config=dataset_config,
                    in_memory_dataset=in_memory_dataset,
                    epochs=stage.epochs,
                )
                summary_result = {
                    "cycle": float(stage.cycle),
                    "mode": "ppo",
                    **summary,
                }
                results.append(summary_result)

        if log_dir is not None:
            log_dir.mkdir(parents=True, exist_ok=True)
            (log_dir / "anneal_results.json").write_text(json.dumps(results, indent=2))
        return results

    def run_ppo(
        self,
        dataset_config: ReplayDatasetConfig | None = None,
        epochs: int = 1,
        log_path: Path | None = None,
        log_frequency: int = 1,
        max_log_entries: int | None = None,
        in_memory_dataset: InMemoryReplayDataset | None = None,
    ) -> dict[str, float]:
        if not torch_available():
            raise TorchNotAvailableError(
                "PyTorch is required for PPO training. Install torch to proceed."
            )

        if in_memory_dataset is not None:
            dataset = in_memory_dataset
        else:
            if dataset_config is None:
                raise ValueError(
                    "dataset_config is required when in_memory_dataset is not provided"
                )
            dataset = ReplayDataset(dataset_config)
        if len(dataset) == 0:
            raise ValueError("Replay dataset yielded no batches")

        batches: list[ReplayBatch] = list(dataset)
        if not batches:
            raise ValueError("Replay dataset yielded no batches")

        example = batches[0]
        timesteps = int(example.metadata.get("timesteps", 1) or 1)
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

        device = torch.device("cpu")
        policy = self.build_policy_network(feature_dim, map_shape, action_dim)
        policy.train()
        policy.to(device)

        optimizer = torch.optim.Adam(policy.parameters(), lr=ppo_cfg.learning_rate)
        self._ppo_state["learning_rate"] = float(ppo_cfg.learning_rate)
        generator = torch.Generator(device=device)

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

            for batch_index, batch in enumerate(batches, start=1):
                batch_summary = self._summarise_batch(batch, batch_index=batch_index)
                for key, value in batch_summary.items():
                    if key.startswith("conflict."):
                        conflict_acc[key] = conflict_acc.get(key, 0.0) + value

                maps = torch.from_numpy(batch.maps).float().to(device)
                features = torch.from_numpy(batch.features).float().to(device)
                actions = torch.from_numpy(batch.actions).long().to(device)
                old_log_probs = torch.from_numpy(batch.old_log_probs).float().to(device)
                rewards = torch.from_numpy(batch.rewards).float().to(device)
                dones = torch.from_numpy(batch.dones.astype(np.float32)).float().to(device)
                value_preds_old = torch.from_numpy(batch.value_preds).float().to(device)

                gae: AdvantageReturns = compute_gae(
                    rewards=rewards,
                    value_preds=value_preds_old,
                    dones=dones,
                    gamma=ppo_cfg.gamma,
                    gae_lambda=ppo_cfg.gae_lambda,
                )
                advantages = gae.advantages
                returns = gae.returns
                if ppo_cfg.advantage_normalization:
                    advantages = normalize_advantages(advantages.view(-1)).view_as(advantages)

                baseline = value_baseline_from_old_preds(value_preds_old, timesteps)

                reward_buffer.extend(
                    batch.rewards.astype(float).reshape(-1).tolist()
                )
                advantage_buffer.extend(
                    advantages.cpu().numpy().astype(float).reshape(-1).tolist()
                )

                batch_size, timestep_length = rewards.shape
                flat_maps = maps.reshape(batch_size * timestep_length, *maps.shape[2:])
                flat_features = features.reshape(batch_size * timestep_length, features.shape[2])
                flat_actions = actions.reshape(-1)
                flat_old_log_probs = old_log_probs.reshape(-1)
                flat_advantages = advantages.reshape(-1)
                flat_returns = returns.reshape(-1)
                flat_old_values = baseline.reshape(-1)

                total_transitions = flat_actions.shape[0]
                desired_batches = min(ppo_cfg.num_mini_batches, total_transitions)
                mini_batch_size = min(
                    ppo_cfg.mini_batch_size,
                    max(1, total_transitions // desired_batches),
                )
                if mini_batch_size <= 0:
                    mini_batch_size = 1
                perm = torch.randperm(total_transitions, generator=generator)

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

                    policy_loss, clip_frac = policy_surrogate(
                        new_log_probs=new_log_probs,
                        old_log_probs=mb_old_log_probs,
                        advantages=mb_advantages,
                        clip_param=ppo_cfg.clip_param,
                    )
                    value_loss = clipped_value_loss(
                        new_values=values,
                        returns=mb_returns,
                        old_values=mb_old_values,
                        value_clip=ppo_cfg.value_clip,
                    )

                    total_loss = (
                        policy_loss
                        + ppo_cfg.value_loss_coef * value_loss
                        - ppo_cfg.entropy_coef * entropy
                    )

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
                        grad_norm = float(sq_sum ** 0.5)
                    optimizer.step()

                    metrics["policy_loss"] += float(policy_loss.item())
                    metrics["value_loss"] += float(value_loss.item())
                    entropy_value = float(entropy.item())
                    metrics["entropy"] += entropy_value
                    entropy_values.append(entropy_value)
                    metrics["total_loss"] += float(total_loss.item())
                    metrics["clip_frac"] += float(clip_frac.item())
                    metrics["adv_mean"] += float(mb_advantages.mean().item())
                    metrics["adv_std"] += float(mb_advantages.std(unbiased=False).item())
                    metrics["grad_norm"] += float(grad_norm)
                    kl_value = float(torch.mean(mb_old_log_probs - new_log_probs).item())
                    metrics["kl_divergence"] += kl_value
                    grad_norm_max = max(grad_norm_max, float(grad_norm))
                    kl_max = max(kl_max, abs(kl_value))
                    mini_batch_updates += 1
                    transitions_processed += int(idx.shape[0])

            if mini_batch_updates == 0:
                raise ValueError("No PPO mini-batch updates were performed")

            averaged_metrics = {
                key: value / mini_batch_updates for key, value in metrics.items()
            }

            if entropy_values:
                epoch_entropy_mean = statistics.fmean(entropy_values)
                epoch_entropy_std = (
                    statistics.pstdev(entropy_values) if len(entropy_values) > 1 else 0.0
                )
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
                        "queue_conflict_intensity_sum": float(
                            getattr(dataset, "queue_conflict_intensity_sum", 0.0)
                        ),
                        "shared_meal_events": float(getattr(dataset, "shared_meal_count", 0)),
                        "late_help_events": float(getattr(dataset, "late_help_count", 0)),
                        "shift_takeover_events": float(
                            getattr(dataset, "shift_takeover_count", 0)
                        ),
                        "chat_success_events": float(getattr(dataset, "chat_success_count", 0)),
                        "chat_failure_events": float(getattr(dataset, "chat_failure_count", 0)),
                        "chat_quality_mean": float(getattr(dataset, "chat_quality_mean", 0.0)),
                    }
                )
                log_stream_offset += 1
            if baseline_metrics:
                epoch_summary["baseline_sample_count"] = float(
                    baseline_metrics.get("sample_count", 0.0)
                )
                epoch_summary["baseline_reward_mean"] = float(
                    baseline_metrics.get("reward_mean", 0.0)
                )
                epoch_summary["baseline_reward_sum"] = float(
                    baseline_metrics.get("reward_sum", 0.0)
                )
                if "reward_sum_mean" in baseline_metrics:
                    epoch_summary["baseline_reward_sum_mean"] = float(
                        baseline_metrics.get("reward_sum_mean", 0.0)
                    )
                if "log_prob_mean" in baseline_metrics:
                    epoch_summary["baseline_log_prob_mean"] = float(
                        baseline_metrics.get("log_prob_mean", 0.0)
                    )
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

    def build_replay_dataset(self, config: ReplayDatasetConfig) -> ReplayDataset:
        return ReplayDataset(config)

    def build_policy_network(
        self,
        feature_dim: int,
        map_shape: tuple[int, int, int],
        action_dim: int,
        hidden_dim: int | None = None,
    ) -> ConflictAwarePolicyNetwork:
        if not torch_available():
            raise TorchNotAvailableError(
                "PyTorch is required to build the policy network. Install torch or disable PPO."
            )
        cfg = ConflictAwarePolicyConfig(
            feature_dim=feature_dim,
            map_shape=map_shape,
            action_dim=action_dim,
            hidden_dim=hidden_dim or 256,
        )
        return ConflictAwarePolicyNetwork(cfg)

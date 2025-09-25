"""Policy orchestration scaffolding."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional

import json
import numpy as np

from townlet.config import PPOConfig, SimulationConfig
from townlet.world.grid import WorldState
from townlet.policy.behavior import AgentIntent, BehaviorController, build_behavior
from townlet.policy.replay import (
    ReplayBatch,
    ReplayDataset,
    ReplayDatasetConfig,
    ReplaySample,
    build_batch,
    load_replay_sample,
)
from townlet.policy.models import (
    ConflictAwarePolicyConfig,
    ConflictAwarePolicyNetwork,
    TorchNotAvailableError,
    torch_available,
)
from townlet.policy.ppo.utils import (
    AdvantageReturns,
    clipped_value_loss,
    compute_gae,
    normalize_advantages,
    policy_surrogate,
    value_baseline_from_old_preds,
)


class PolicyRuntime:
    """Bridges the simulation with PPO/backends via PettingZoo."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.behavior: BehaviorController = build_behavior(config)
        self._transitions: Dict[str, Dict[str, object]] = {}
        self._trajectory: List[Dict[str, object]] = []
        self._tick: int = 0
        self._action_lookup: Dict[str, int] = {}
        self._action_inverse: Dict[int, str] = {}
        self._policy_net: ConflictAwarePolicyNetwork | None = None
        self._policy_map_shape: tuple[int, int, int] | None = None
        self._policy_feature_dim: int | None = None
        self._policy_action_dim: int = 0

    def decide(self, world: WorldState, tick: int) -> Dict[str, object]:
        """Return a primitive action per agent."""
        self._tick = tick
        actions: Dict[str, object] = {}
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

    def post_step(self, rewards: Dict[str, float], terminated: Dict[str, bool]) -> None:
        """Record rewards and termination signals into buffers."""
        for agent_id, reward in rewards.items():
            entry = self._transitions.setdefault(agent_id, {})
            entry.setdefault("rewards", []).append(reward)
            entry.setdefault("dones", []).append(bool(terminated.get(agent_id, False)))

    def flush_transitions(self, observations: Dict[str, Dict[str, object]]) -> List[Dict[str, object]]:
        """Combine stored transition data with observations and return trajectory frames."""
        frames: List[Dict[str, object]] = []
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

    def collect_trajectory(self, clear: bool = True) -> List[Dict[str, object]]:
        """Return accumulated trajectory frames and reset internal buffer."""
        result = list(self._trajectory)
        if clear:
            self._trajectory.clear()
        return result

    def _annotate_with_policy_outputs(self, frame: Dict[str, object]) -> None:
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

    def run(self) -> None:
        """Entry point for CLI training runs."""
        raise NotImplementedError("Training harness not yet implemented")

    def run_replay(self, sample_path: Path, meta_path: Optional[Path] = None) -> Dict[str, float]:
        """Load a replay observation sample and surface conflict-aware stats."""
        sample: ReplaySample = load_replay_sample(sample_path, meta_path)
        batch = build_batch([sample])
        summary = self._summarise_batch(batch, batch_index=1)
        print("Replay sample loaded:", summary)
        return summary

    def run_replay_batch(self, pairs: Iterable[tuple[Path, Optional[Path]]]) -> Dict[str, float]:
        entries = list(pairs)
        if not entries:
            raise ValueError("Replay batch requires at least one entry")
        config = ReplayDatasetConfig(entries=entries, batch_size=len(entries))
        return self.run_replay_dataset(config)

    def run_replay_dataset(self, dataset_config: ReplayDatasetConfig) -> Dict[str, float]:
        dataset = ReplayDataset(dataset_config)
        summary: Dict[str, float] = {}
        for idx, batch in enumerate(dataset, start=1):
            summary = self._summarise_batch(batch, batch_index=idx)
            print(f"Replay batch {idx}:", summary)
        if not summary:
            raise ValueError("Replay dataset yielded no batches")
        return summary

    def run_ppo(
        self, dataset_config: ReplayDatasetConfig, epochs: int = 1, log_path: Optional[Path] = None
    ) -> Dict[str, float]:
        if not torch_available():
            raise TorchNotAvailableError("PyTorch is required for PPO training. Install torch to proceed.")

        dataset = ReplayDataset(dataset_config)
        if len(dataset) == 0:
            raise ValueError("Replay dataset yielded no batches")

        batches: List[ReplayBatch] = list(dataset)
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

        log_handle = None
        if log_path is not None:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_handle = log_path.open("a", encoding="utf-8")
        last_summary: Dict[str, float] = {}
        for epoch in range(epochs):
            conflict_acc: Dict[str, float] = {}
            metrics = {
                "policy_loss": 0.0,
                "value_loss": 0.0,
                "entropy": 0.0,
                "total_loss": 0.0,
                "clip_frac": 0.0,
                "adv_mean": 0.0,
                "adv_std": 0.0,
                "grad_norm": 0.0,
            }
            mini_batch_updates = 0
            transitions_processed = 0

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
                        grad_norm = clip_grad_norm_(policy.parameters(), ppo_cfg.max_grad_norm).item()
                    else:
                        sq_sum = 0.0
                        for param in policy.parameters():
                            if param.grad is not None:
                                sq_sum += float(torch.sum(param.grad.detach() ** 2).item())
                        grad_norm = float(sq_sum ** 0.5)
                    optimizer.step()

                    metrics["policy_loss"] += float(policy_loss.item())
                    metrics["value_loss"] += float(value_loss.item())
                    metrics["entropy"] += float(entropy.item())
                    metrics["total_loss"] += float(total_loss.item())
                    metrics["clip_frac"] += float(clip_frac.item())
                    metrics["adv_mean"] += float(mb_advantages.mean().item())
                    metrics["adv_std"] += float(mb_advantages.std(unbiased=False).item())
                    metrics["grad_norm"] += float(grad_norm)
                    mini_batch_updates += 1
                    transitions_processed += int(idx.shape[0])

            if mini_batch_updates == 0:
                raise ValueError("No PPO mini-batch updates were performed")

            averaged_metrics = {
                key: value / mini_batch_updates for key, value in metrics.items()
            }

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
                "lr": lr,
                "steps": float(self._ppo_state["step"]),
            }
            if conflict_acc:
                for key, value in conflict_acc.items():
                    epoch_summary[f"{key}_avg"] = value / len(batches)

            print(f"PPO epoch {epoch + 1}:", epoch_summary)
            if log_handle is not None:
                log_handle.write(json.dumps(epoch_summary) + "\n")
                log_handle.flush()
            last_summary = epoch_summary
        if log_handle is not None:
            log_handle.close()
        return last_summary

    def _summarise_batch(self, batch: ReplayBatch, batch_index: int) -> Dict[str, float]:
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
        self, feature_dim: int, map_shape: tuple[int, int, int], action_dim: int, hidden_dim: int | None = None
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

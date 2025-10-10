"""Orchestration layer between the simulation loop and policy backends."""

from __future__ import annotations

import json
import warnings
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any

import numpy as np

from townlet.config import SimulationConfig
from townlet.policy.behavior import AgentIntent, BehaviorController, build_behavior
from townlet.policy.behavior_bridge import BehaviorBridge
from townlet.policy.models import (
    ConflictAwarePolicyConfig,
    ConflictAwarePolicyNetwork,
    TorchNotAvailableError,
    torch_available,
)
from townlet.policy.trajectory_service import TrajectoryService
from townlet.world.grid import WorldState

from .dto_view import DTOWorldView

if TYPE_CHECKING:  # pragma: no cover
    from townlet.world.dto.observation import ObservationEnvelope

# NOTE: Training orchestrator is imported lazily by TrainingHarness to avoid
# importing Torch-dependent modules during test collection in non-ML envs.


def _softmax(logits: np.ndarray) -> np.ndarray:
    if logits.size == 0:
        return logits
    max_logit = float(np.max(logits))
    shifted = logits - max_logit
    exps = np.exp(shifted, dtype=np.float64)
    denom = float(np.sum(exps))
    if denom <= 0.0:
        return np.full_like(logits, 1.0 / logits.size)
    return (exps / denom).astype(np.float32)


def _pretty_action(action_repr: str) -> str:
    try:
        data = json.loads(action_repr)
    except json.JSONDecodeError:
        return action_repr
    if isinstance(data, dict):
        kind = data.get("kind")
        obj = data.get("object") or data.get("object_id")
        aff = data.get("affordance") or data.get("affordance_id")
        if kind and obj:
            label = f"{kind}@{obj}"
        elif kind:
            label = str(kind)
        else:
            label = action_repr
        if aff:
            label = f"{label}:{aff}"
        return label
    return action_repr


class PolicyRuntime:
    """Bridge between the simulation loop, scripted behaviour, and policy backends.

    The runtime owns the behaviour controller, optional neural policy, and the
    trajectory buffers consumed by training jobs. It presents a PettingZoo-like
    façade (`decide`, `post_step`, `flush_transitions`) while hiding optional
    dependencies such as PyTorch.
    """

    def __init__(self, config: SimulationConfig) -> None:
        """Initialise behaviour bridges, trajectory buffers, and policy metadata."""

        self.config = config
        behavior_controller: BehaviorController = build_behavior(config)
        self._tick: int = 0
        self._action_lookup: dict[str, int] = {}
        self._action_inverse: dict[int, str] = {}
        self._policy_net: ConflictAwarePolicyNetwork | None = None
        self._policy_map_shape: tuple[int, int, int] | None = None
        self._policy_feature_dim: int | None = None
        self._policy_action_dim: int = 0
        self._latest_policy_snapshot: dict[str, dict[str, object]] = {}
        policy_cfg = getattr(config, "policy_runtime", None)
        commit_ticks = 15
        if policy_cfg is not None:
            commit_ticks = int(getattr(policy_cfg, "option_commit_ticks", commit_ticks))
        option_commit_ticks = max(commit_ticks, 0)
        self._behavior_bridge = BehaviorBridge(
            behavior=behavior_controller,
            option_commit_ticks=option_commit_ticks,
        )
        self._trajectory_service = TrajectoryService()
        self._policy_hash: str | None = None
        config_policy_hash = getattr(self.config, "policy_hash", None)
        if isinstance(config_policy_hash, str) and config_policy_hash:
            self._policy_hash = config_policy_hash
        self._latest_envelope: "ObservationEnvelope | None" = None

    @property
    def behavior(self) -> BehaviorController:
        return self._behavior_bridge.behavior

    @property
    def transitions(self) -> dict[str, dict[str, object]]:
        """Expose the per-agent transition buffer maintained by the trajectory service."""

        return self._trajectory_service.transitions

    @property
    def trajectory(self) -> list[dict[str, object]]:
        """Expose accumulated trajectory frames for inspection or testing."""

        return self._trajectory_service.trajectory

    def anneal_context(self) -> dict[str, object]:
        """Return anneal and option commit context for diagnostics."""

        return self._behavior_bridge.snapshot()


    @behavior.setter
    def behavior(self, controller: BehaviorController) -> None:
        self._behavior_bridge.behavior = controller

    @property
    def _option_commit_until(self) -> dict[str, int]:
        return self._behavior_bridge._option_commit_until

    @property
    def _option_committed_intent(self) -> dict[str, AgentIntent]:
        return self._behavior_bridge._option_committed_intent

    def seed_anneal_rng(self, seed: int) -> None:
        """Seed the RNG used by anneal blend scheduling."""

        self._behavior_bridge.seed_anneal_rng(seed)

    def enable_anneal_blend(self, enabled: bool) -> None:
        """Toggle anneal blending behaviour on the underlying controller."""

        self._behavior_bridge.enable_anneal_blend(enabled)

    def register_ctx_reset_callback(self, callback: Callable[[str], None] | None) -> None:
        """Install a callback invoked whenever an agent context reset is requested."""

        self._behavior_bridge.register_ctx_reset_callback(callback)

    def set_policy_action_provider(
        self, provider: Callable[[WorldState, str, AgentIntent], AgentIntent | None]
    ) -> None:
        """Override scripted action selection for possessed agents."""

        self._behavior_bridge.set_policy_action_provider(provider)

    def decide(
        self,
        world: WorldState,
        tick: int,
        *,
        envelope: "ObservationEnvelope | None" = None,
        observations: Mapping[str, Any] | None = None,
    ) -> dict[str, object]:
        """Return an action dictionary per agent for the current tick."""

        dto_world: DTOWorldView | None = None
        if envelope is not None:
            self._latest_envelope = envelope
            guardrail_emitter = getattr(world, "emit_event", None)
            dto_world = DTOWorldView(
                envelope=envelope,
                world=world,
                guardrail_emitter=guardrail_emitter,
            )
        self._tick = tick
        self._trajectory_service.begin_tick(tick)
        actions: dict[str, object] = {}
        for agent_id in world.agents:
            if self._behavior_bridge.is_possessed(agent_id):
                actions[agent_id] = {"kind": "wait"}
                continue
            def _guard(world_ref: WorldState, agent: str, intent: AgentIntent) -> AgentIntent:
                return self._apply_relationship_guardrails(
                    world_ref,
                    agent,
                    intent,
                    dto_world=dto_world,
                )

            selected_intent, commit_enforced = self._behavior_bridge.decide_agent(
                world=world,
                agent_id=agent_id,
                tick=tick,
                guardrail_fn=_guard,
                dto_world=dto_world,
            )
            if selected_intent.kind == "wait":
                wait_payload: dict[str, object] = {"kind": "wait"}
                if selected_intent.blocked:
                    wait_payload["blocked"] = True
                actions[agent_id] = wait_payload
            else:
                action_dict: dict[str, object | None] = {
                    "kind": selected_intent.kind,
                    "object": selected_intent.object_id,
                    "affordance": selected_intent.affordance_id,
                    "blocked": selected_intent.blocked,
                }
                if selected_intent.position is not None:
                    action_dict["position"] = selected_intent.position
                if selected_intent.target_agent is not None:
                    action_dict["target"] = selected_intent.target_agent
                if selected_intent.quality is not None:
                    action_dict["quality"] = float(selected_intent.quality)
                actions[agent_id] = action_dict
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

            entry = self._trajectory_service.transition_entry(agent_id)
            self._behavior_bridge.update_transition_entry(
                agent_id, tick, entry, commit_enforced
            )
            self._trajectory_service.record_action(agent_id, action_payload, action_id)
        return actions

    def _apply_relationship_guardrails(
        self,
        world: WorldState,
        agent_id: str,
        intent: AgentIntent,
        *,
        dto_world: DTOWorldView | None = None,
    ) -> AgentIntent:
        avoidance = getattr(self.behavior, "should_avoid", None)
        rivalry_source = dto_world if dto_world is not None else world

        def _should_avoid(target_agent: str) -> bool:
            if not target_agent:
                return False
            if callable(avoidance):
                try:
                    return bool(avoidance(world, agent_id, target_agent))
                except Exception:  # pragma: no cover - defensive hook
                    return rivalry_source.rivalry_should_avoid(agent_id, target_agent)
            return rivalry_source.rivalry_should_avoid(agent_id, target_agent)

        if intent.kind == "chat" and intent.target_agent:
            if _should_avoid(intent.target_agent):
                if dto_world is not None:
                    dto_world.record_chat_failure(agent_id, intent.target_agent)
                    dto_world.record_relationship_guard_block(
                        agent_id=agent_id,
                        reason="chat_rival",
                        target_agent=intent.target_agent,
                    )
                else:
                    self._emit_guardrail_request(
                        world,
                        "chat_failure",
                        speaker=agent_id,
                        listener=intent.target_agent,
                    )
                    self._emit_guardrail_request(
                        world,
                        "relationship_block",
                        agent_id=agent_id,
                        reason="chat_rival",
                        target_agent=intent.target_agent,
                    )
                cancel = getattr(self.behavior, "cancel_pending", None)
                if callable(cancel):
                    cancel(agent_id)
                return AgentIntent(kind="wait", blocked=True)
        if intent.kind in {"request", "start"} and intent.object_id:
            guard = getattr(self.behavior, "_rivals_in_queue", None)
            queue_view = None
            relationship_view = None
            if dto_world is not None:
                queue_view = dto_world.queue_manager
                relationship_view = dto_world
            else:
                queue_view = world.queue_manager
                relationship_view = world
            if callable(guard) and guard(
                world,
                agent_id,
                intent.object_id,
                queue_view=queue_view,
                relationship_view=relationship_view,
            ):
                if dto_world is not None:
                    dto_world.record_relationship_guard_block(
                        agent_id=agent_id,
                        reason="queue_rival",
                        object_id=intent.object_id,
                    )
                else:
                    self._emit_guardrail_request(
                        world,
                        "relationship_block",
                        agent_id=agent_id,
                        reason="queue_rival",
                        object_id=intent.object_id,
                    )
                cancel = getattr(self.behavior, "cancel_pending", None)
                if callable(cancel):
                    cancel(agent_id)
                return AgentIntent(kind="wait", blocked=True)
        return intent

    def _emit_guardrail_request(
        self,
        world: WorldState,
        variant: str,
        **payload: Any,
    ) -> None:
        emitter = getattr(world, "emit_event", None)
        request: dict[str, Any] = {"variant": variant}
        for key, value in payload.items():
            if value is not None:
                request[key] = value
        if callable(emitter):
            emitter("policy.guardrail.request", request)
            return
        raise RuntimeError("WorldState.emit_event unavailable for guardrail event request")

    def post_step(self, rewards: dict[str, float], terminated: dict[str, bool]) -> None:
        """Record rewards and termination signals into internal buffers."""
        for agent_id, reward in rewards.items():
            done = bool(terminated.get(agent_id, False))
            self._trajectory_service.append_reward(agent_id, reward, done)
            if done:
                self._behavior_bridge.mark_termination(agent_id)

        for agent_id, is_done in terminated.items():
            if is_done and agent_id not in rewards:
                self._behavior_bridge.clear_commit_state(agent_id)

    def flush_transitions(
        self, observations: dict[str, dict[str, object]]
    ) -> list[dict[str, object]]:
        """Combine stored transition data with observations and return frames."""
        frames = self._trajectory_service.flush_transitions(observations)
        for frame in frames:
            self._annotate_with_policy_outputs(frame)
        self._trajectory_service.extend_trajectory(frames)
        self._update_policy_snapshot(frames)
        return frames

    def collect_trajectory(self, clear: bool = True) -> list[dict[str, object]]:
        """Return accumulated trajectory frames and optionally clear the buffer."""
        return self._trajectory_service.collect_trajectory(clear=clear)

    def consume_option_switch_counts(self) -> dict[str, int]:
        """Return per-agent option switch counts accumulated since the last call."""

        return self._behavior_bridge.consume_option_switch_counts()

    def acquire_possession(self, agent_id: str) -> bool:
        """Mark an agent as possessed so scripted logic controls actions."""

        return self._behavior_bridge.acquire_possession(agent_id)

    def release_possession(self, agent_id: str) -> bool:
        """Release possession acquired via :meth:`acquire_possession`."""

        return self._behavior_bridge.release_possession(agent_id)

    def is_possessed(self, agent_id: str) -> bool:
        """Return whether ``agent_id`` is currently possessed."""

        return self._behavior_bridge.is_possessed(agent_id)

    def possessed_agents(self) -> list[str]:
        """Return a list of possessed agent identifiers."""

        return self._behavior_bridge.possessed_agents()

    def reset_state(self) -> None:
        """Reset transient buffers so snapshot loads don't duplicate data."""

        self._trajectory_service.reset_state()
        self._behavior_bridge.reset_state()

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

    def _update_policy_snapshot(self, frames: list[dict[str, object]]) -> None:
        snapshot: dict[str, dict[str, object]] = {}
        for frame in frames:
            agent_id = str(frame.get("agent_id", "unknown"))
            logits = frame.get("logits")
            if logits is None:
                continue
            logits_array = np.asarray(logits, dtype=np.float32)
            if logits_array.ndim != 1 or logits_array.size == 0:
                continue
            probabilities = _softmax(logits_array)
            action_lookup_raw = frame.get("action_lookup", {})
            action_lookup: dict[int, str] = {}
            if isinstance(action_lookup_raw, Mapping):
                for action_repr, action_index in action_lookup_raw.items():
                    if isinstance(action_index, int):
                        action_lookup[action_index] = _pretty_action(str(action_repr))
            top_indices = np.argsort(probabilities)[::-1][:5]
            top_actions: list[dict[str, object]] = []
            for idx in top_indices:
                if idx < 0 or idx >= probabilities.size:
                    continue
                top_actions.append(
                    {
                        "action": action_lookup.get(idx, str(idx)),
                        "probability": float(round(float(probabilities[idx]), 6)),
                    }
                )
            selected_idx = frame.get("action_id")
            selected_label = action_lookup.get(selected_idx, str(selected_idx))
            snapshot[agent_id] = {
                "tick": int(frame.get("tick", self._tick)),
                "selected_action": selected_label,
                "log_prob": float(round(float(frame.get("log_prob", 0.0)), 6)),
                "value_pred": float(round(float(frame.get("value_pred", 0.0)), 6)),
                "top_actions": top_actions,
            }
        self._latest_policy_snapshot = snapshot

    def latest_policy_snapshot(self) -> dict[str, dict[str, object]]:
        return {agent: dict(data) for agent, data in self._latest_policy_snapshot.items()}

    # ------------------------------------------------------------------
    # Policy metadata helpers
    # ------------------------------------------------------------------

    def active_policy_hash(self) -> str | None:
        """Return the configured policy hash, if any."""

        return self._policy_hash

    def set_policy_hash(self, value: str | None) -> None:
        """Set the policy hash after loading a checkpoint."""

        self._policy_hash = value if value else None

    def current_anneal_ratio(self) -> float | None:
        """Return the latest anneal ratio (0..1) if tracking available."""

        return self._behavior_bridge.current_anneal_ratio()

    def set_anneal_ratio(self, ratio: float | None) -> None:
        self._behavior_bridge.set_anneal_ratio(ratio)

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
    """Backward-compatible, lazy wrapper around PolicyTrainingOrchestrator.

    This indirection prevents importing Torch-dependent modules at import time
    when the training harness is not used.
    """

    def __init__(self, config: SimulationConfig) -> None:
        warnings.warn(
            "TrainingHarness is deprecated; import PolicyTrainingOrchestrator instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from .training_orchestrator import PolicyTrainingOrchestrator

        self._impl = PolicyTrainingOrchestrator(config=config)

    def __getattr__(self, name: str):  # pragma: no cover - simple delegation
        return getattr(self._impl, name)

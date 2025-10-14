"""Rollout capture service (torch-free).

This service handles simulation rollout capture and dataset building from
rollout buffers. All operations are torch-free and importable without PyTorch.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from townlet.config import SimulationConfig
    from townlet.policy.replay_buffer import InMemoryReplayDataset
    from townlet.policy.rollout import RolloutBuffer

logger = logging.getLogger(__name__)


class RolloutCaptureService:
    """Torch-free rollout capture service.

    Provides utilities for capturing simulation rollouts and building replay
    datasets from captured trajectory buffers. Does not require PyTorch.

    Example:
        service = RolloutCaptureService(config)
        buffer = service.capture(ticks=100, auto_seed_agents=True)
        dataset = service.build_dataset_from_buffer(buffer, batch_size=1)
    """

    def __init__(self, config: SimulationConfig) -> None:
        """Initialize rollout capture service.

        Args:
            config: Simulation configuration.
        """
        self.config = config

    def capture(
        self,
        ticks: int,
        auto_seed_agents: bool = False,
        output_dir: Path | None = None,
        prefix: str = "rollout_sample",
        compress: bool = True,
    ) -> RolloutBuffer:
        """Capture a rollout from simulation loop.

        Runs the simulation for a fixed number of ticks and collects trajectory
        frames from the policy backend. Optionally saves the buffer to disk.

        Args:
            ticks: Number of simulation ticks to run.
            auto_seed_agents: Whether to seed default agents if none exist.
            output_dir: Optional directory to save rollout buffer.
            prefix: Filename prefix for saved rollout.
            compress: Whether to compress saved rollout.

        Returns:
            RolloutBuffer containing captured trajectory frames.

        Raises:
            ValueError: If ticks <= 0 or no agents available.
        """
        from townlet.core.sim_loop import SimulationLoop
        from townlet.core.utils import is_stub_policy, policy_provider_name
        from townlet.policy.rollout import RolloutBuffer
        from townlet.policy.scenario_utils import (
            apply_scenario,
            has_agents,
            seed_default_agents,
        )

        if ticks <= 0:
            raise ValueError("ticks must be positive to capture a rollout")

        # Create simulation loop
        loop = SimulationLoop(self.config)

        # Apply scenario or seed agents
        scenario_config = getattr(self.config, "scenario", None)
        if scenario_config:
            apply_scenario(loop, scenario_config)
        elif auto_seed_agents and not loop.world.agents:
            seed_default_agents(loop)

        if not has_agents(loop):
            raise ValueError(
                "No agents available for rollout capture. "
                "Provide a scenario or use auto seeding."
            )

        # Create rollout buffer
        buffer = RolloutBuffer()

        # Check if policy is a stub (won't capture trajectories)
        provider = policy_provider_name(loop)
        if is_stub_policy(loop.policy, provider):
            logger.warning(
                "capture_rollout_stub_policy provider=%s "
                "message='Stub policy backend active; no trajectories captured.'",
                provider,
            )
            return buffer

        # Run simulation and capture frames
        for _ in range(ticks):
            loop.step()
            frames = loop.policy.collect_trajectory(clear=True)
            if frames:
                buffer.extend(frames)
            buffer.record_events(loop.telemetry.latest_events())

        # Collect any leftover frames
        leftover_frames = loop.policy.collect_trajectory(clear=True)
        if leftover_frames:
            buffer.extend(leftover_frames)

        buffer.set_tick_count(ticks)

        # Optionally save to disk
        if output_dir is not None:
            buffer.save(output_dir, prefix=prefix, compress=compress)

        return buffer

    def build_dataset_from_buffer(
        self,
        buffer: RolloutBuffer,
        batch_size: int = 1,
    ) -> InMemoryReplayDataset:
        """Build an in-memory replay dataset from a rollout buffer.

        Args:
            buffer: Rollout buffer containing trajectory frames.
            batch_size: Batch size for dataset.

        Returns:
            In-memory replay dataset ready for training.
        """
        return buffer.build_dataset(batch_size=batch_size)


__all__ = ["RolloutCaptureService"]

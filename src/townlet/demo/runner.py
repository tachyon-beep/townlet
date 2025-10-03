from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable

from townlet.core.sim_loop import SimulationLoop
from townlet.demo.timeline import DemoTimeline, ScheduledCommand, load_timeline
from townlet_ui.commands import CommandQueueFull, ConsoleCommandExecutor
from townlet_ui.dashboard import PaletteState, run_dashboard
from townlet.world.grid import AgentSnapshot, WorldState

__all__ = [
    "DemoScheduler",
    "default_timeline",
    "load_timeline",
    "run_demo_dashboard",
    "seed_demo_state",
]

logger = logging.getLogger(__name__)


@dataclass
class DemoScheduler:
    """Executes scheduled commands or scripted actions during the demo."""

    timeline: DemoTimeline
    palette_state: PaletteState | None = None

    def on_tick(
        self,
        loop: SimulationLoop,
        executor: ConsoleCommandExecutor,
        tick: int,
    ) -> None:
        due = self.timeline.pop_due(tick)
        if not due:
            if self.palette_state is not None:
                self.palette_state.pending = executor.pending_count()
            return

        for item in due:
            if item.kind == "console":
                payload = item.payload()
                try:
                    executor.submit_payload(payload)
                    message = f"Dispatched {item.name} at tick {tick}"
                    logger.info(message)
                    if self.palette_state is not None:
                        self.palette_state.status_message = message
                        self.palette_state.status_style = "green"
                except CommandQueueFull as exc:
                    warning = (
                        f"Console queue saturated ({exc.pending}/{exc.max_pending or exc.pending})"
                    )
                    logger.warning(warning)
                    if self.palette_state is not None:
                        self.palette_state.status_message = warning
                        self.palette_state.status_style = "yellow"
            else:
                message = self._execute_action(loop.world, item)
                if self.palette_state is not None:
                    self.palette_state.status_message = message
                    self.palette_state.status_style = "cyan"
            if self.palette_state is not None:
                self.palette_state.pending = executor.pending_count()

    def _execute_action(self, world: WorldState, command: ScheduledCommand) -> str:
        name = command.name
        kwargs = command.kwargs or {}
        if name == "spawn_agent":
            agent_id = kwargs.get("agent_id") or (command.args[0] if command.args else None)
            if not agent_id:
                agent_id = f"demo_{world.tick}"
            needs = kwargs.get("needs") or {
                "hunger": 0.4,
                "hygiene": 0.6,
                "energy": 0.5,
            }
            wallet = float(kwargs.get("wallet", 5.0))
            position = kwargs.get("position", (0, 0))
            if not isinstance(position, (tuple, list)) or len(position) != 2:
                position = (0, 0)
            snapshot = AgentSnapshot(
                agent_id=agent_id,
                position=(int(position[0]), int(position[1])),
                needs=dict(needs),
                wallet=wallet,
            )
            world.agents[agent_id] = snapshot
            assign_jobs = getattr(world, "_assign_jobs_to_agents", None)
            if callable(assign_jobs):
                assign_jobs()
            message = f"Spawned agent {agent_id}"
        elif name == "force_chat":
            speaker = kwargs.get("speaker") or (command.args[0] if command.args else None)
            listener = kwargs.get("listener") or (command.args[1] if len(command.args) > 1 else None)
            quality = float(kwargs.get("quality", 0.85))
            if speaker and listener:
                world.record_chat_success(speaker, listener, quality)
                message = f"Forced chat {speaker}->{listener}"
            else:
                message = "force_chat missing speaker/listener"
        elif name == "set_need":
            agent_id = kwargs.get("agent_id") or (command.args[0] if command.args else None)
            need = kwargs.get("need") or (command.args[1] if len(command.args) > 1 else None)
            value = float(kwargs.get("value", command.args[2] if len(command.args) > 2 else 0.5))
            if agent_id and need and agent_id in world.agents:
                world.agents[agent_id].needs[need] = max(0.0, min(1.0, value))
                message = f"Set {agent_id}.{need} -> {value:.2f}"
            else:
                message = "set_need missing agent/need"
        else:
            message = f"Unknown action {name}"
            logger.warning(message)
        return message


def seed_demo_state(
    world: WorldState,
    *,
    agents_required: int = 3,
    history_window: int | None = 30,
) -> None:
    """Populate world with starter agents, relationships, and history for demos."""

    seeded = False
    if not world.agents:
        for index in range(agents_required):
            agent_id = f"demo_{index+1}"
            world.agents[agent_id] = AgentSnapshot(
                agent_id=agent_id,
                position=(index, 0),
                needs={
                    "hunger": 0.45 + 0.05 * index,
                    "hygiene": 0.55 - 0.05 * index,
                    "energy": 0.5,
                },
                wallet=5.0 + index,
            )
        seeded = True

    assign_jobs = getattr(world, "_assign_jobs_to_agents", None)
    if callable(assign_jobs):
        assign_jobs()

    agent_ids = list(world.agents.keys())
    if len(agent_ids) >= 2:
        for idx in range(min(len(agent_ids), 4)):
            current = agent_ids[idx]
            other = agent_ids[(idx + 1) % len(agent_ids)]
            world.update_relationship(current, other, trust=0.25, familiarity=0.2)
            world.record_chat_success(current, other, 0.9)

    telemetry = getattr(world, "telemetry", None)
    if telemetry is not None and history_window and history_window > 0:
        for agent_id in agent_ids:
            agent = world.agents[agent_id]
            telemetry.record_wallet(agent_id, agent.wallet)
            for need, value in agent.needs.items():
                telemetry.record_need(agent_id, need, value)

        if seeded:
            telemetry.publish_tick(
                tick=world.tick,
                world=world,
                observations={},
                rewards={},
                events=[],
                policy_snapshot={},
                kpi_history=False,
                reward_breakdown={},
                stability_inputs={},
                perturbations={},
                policy_identity={},
                possessed_agents=[],
            )


def default_timeline() -> DemoTimeline:
    commands: list[ScheduledCommand] = [
        ScheduledCommand(tick=5, name="spawn_agent", kind="action", kwargs={"agent_id": "guest_1", "position": (2, 1), "wallet": 8.0}),
        ScheduledCommand(tick=10, name="force_chat", kind="action", kwargs={"speaker": "guest_1", "listener": "demo_1", "quality": 0.95}),
        ScheduledCommand(tick=20, name="perturbation_trigger", args=("price_spike",), kwargs={"magnitude": 1.4, "starts_in": 0}),
    ]
    return DemoTimeline(commands)


def run_demo_dashboard(
    loop: SimulationLoop,
    *,
    refresh_interval: float,
    max_ticks: int,
    timeline: DemoTimeline,
    palette_state: PaletteState | None,
) -> None:
    scheduler = DemoScheduler(timeline=timeline, palette_state=palette_state)
    run_dashboard(
        loop,
        refresh_interval=refresh_interval,
        max_ticks=max_ticks,
        palette_state=palette_state,
        on_tick=scheduler.on_tick,
    )

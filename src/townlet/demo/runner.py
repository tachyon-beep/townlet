"""Utilities for running scripted Townlet demos and dashboards."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from townlet.core.interfaces import TelemetrySinkProtocol
from townlet.core.sim_loop import SimulationLoop
from townlet.core.utils import is_stub_telemetry
from townlet.demo.storylines import available_storylines, build_storyline, default_timeline
from townlet.demo.timeline import DemoTimeline, ScheduledCommand, load_timeline
from townlet.world.grid import AgentSnapshot, WorldState
from townlet_ui.commands import CommandQueueFull, ConsoleCommandExecutor
from townlet_ui.dashboard import PaletteState, run_dashboard

__all__ = [
    "DemoScheduler",
    "available_storylines",
    "build_storyline",
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
    narration_category: str = "demo_story"
    _last_narration_tick: int = field(default=-10_000, init=False, repr=False)

    def on_tick(
        self,
        loop: SimulationLoop,
        executor: ConsoleCommandExecutor,
        tick: int,
    ) -> None:
        """Dispatch due timeline entries for the current tick."""
        due = self.timeline.pop_due(tick)
        if not due:
            self._set_palette(executor, None)
            return

        for item in due:
            if item.kind == "console":
                payload = item.payload()
                try:
                    executor.submit_payload(payload)
                    message = f"Dispatched {item.name} at tick {tick}"
                    logger.info(message)
                    self._set_palette(executor, message, "green")
                except CommandQueueFull as exc:
                    warning = f"Console queue saturated ({exc.pending}/{exc.max_pending or exc.pending})"
                    logger.warning(warning)
                    self._set_palette(executor, warning, "yellow")
            elif item.kind == "action":
                message = self._execute_action(loop.world, item)
                self._set_palette(executor, message, "cyan")
            elif item.kind == "narration":
                message, style = self._enqueue_narration(loop, executor, tick, item)
                self._set_palette(executor, message, style)
            else:
                warning = f"Unsupported timeline kind {item.kind}"
                logger.warning(warning)
                self._set_palette(executor, warning, "red")

    def _execute_action(self, world: WorldState, command: ScheduledCommand) -> str:
        """Execute action-style commands that mutate the world directly."""
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
            profile_field = kwargs.get("personality_profile")
            profile_name, resolved_personality = world.select_personality_profile(
                agent_id,
                profile_field if isinstance(profile_field, str) else None,
            )
            snapshot = AgentSnapshot(
                agent_id=agent_id,
                position=(int(position[0]), int(position[1])),
                needs=dict(needs),
                wallet=wallet,
                personality=resolved_personality,
                personality_profile=profile_name,
            )
            world.agents[agent_id] = snapshot
            world.assign_jobs_to_agents()
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

    def _enqueue_narration(
        self,
        loop: SimulationLoop,
        executor: ConsoleCommandExecutor,
        tick: int,
        command: ScheduledCommand,
    ) -> tuple[str, str]:
        """Submit a narration command while respecting throttling rules."""
        kwargs = command.kwargs or {}
        raw_message = kwargs.get("message")
        if raw_message is None and command.args:
            raw_message = command.args[0]
        if not isinstance(raw_message, str) or not raw_message.strip():
            return ("Narration missing message", "red")
        message_text = raw_message.strip()

        spacing = int(getattr(loop.config.telemetry.narration, "global_cooldown_ticks", 30))
        spacing_override = kwargs.get("spacing")
        if spacing_override is not None:
            try:
                spacing = max(1, int(spacing_override))
            except (TypeError, ValueError):
                return ("Narration spacing must be an integer", "red")
        spacing = max(1, spacing)
        if tick - self._last_narration_tick < spacing:
            remaining = spacing - (tick - self._last_narration_tick)
            return (f"Narration throttled ({remaining} ticks remaining)", "yellow")

        tick_override = kwargs.get("tick")
        try:
            tick_value = int(tick_override) if tick_override is not None else tick
        except (TypeError, ValueError):
            return ("Narration tick must be an integer", "red")

        payload_kwargs: dict[str, object] = {
            "message": message_text,
            "category": str(kwargs.get("category", self.narration_category) or self.narration_category),
            "tick": tick_value,
        }
        if "priority" in kwargs:
            payload_kwargs["priority"] = bool(kwargs["priority"])
        if "data" in kwargs:
            payload_kwargs["data"] = kwargs["data"]
        if "dedupe_key" in kwargs:
            payload_kwargs["dedupe_key"] = kwargs["dedupe_key"]

        payload = {"name": "announce_story", "kwargs": payload_kwargs}
        try:
            executor.submit_payload(payload)
        except CommandQueueFull as exc:
            warning = f"Console queue saturated ({exc.pending}/{exc.max_pending or exc.pending})"
            logger.warning(warning)
            return (warning, "yellow")

        self._last_narration_tick = tick
        summary = message_text if len(message_text) <= 60 else f"{message_text[:57]}..."
        return (f"Narration queued: {summary}", "magenta")

    def _set_palette(
        self,
        executor: ConsoleCommandExecutor,
        message: str | None,
        style: str = "dim",
    ) -> None:
        """Update dashboard palette state with the most recent status message."""
        if self.palette_state is None:
            return
        if message is not None:
            self.palette_state.status_message = message
            self.palette_state.status_style = style
        self.palette_state.pending = executor.pending_count()


def seed_demo_state(
    world: WorldState,
    *,
    agents_required: int = 3,
    history_window: int | None = 30,
    telemetry: TelemetrySinkProtocol | None = None,
    narration_level: str | None = None,
) -> None:
    """Populate world with starter agents, relationships, and history for demos."""

    seeded = False
    if not world.agents:
        for index in range(agents_required):
            agent_id = f"demo_{index + 1}"
            profile_name, resolved_personality = world.select_personality_profile(agent_id)
            world.agents[agent_id] = AgentSnapshot(
                agent_id=agent_id,
                position=(index, 0),
                needs={
                    "hunger": 0.45 + 0.05 * index,
                    "hygiene": 0.55 - 0.05 * index,
                    "energy": 0.5,
                },
                wallet=5.0 + index,
                personality=resolved_personality,
                personality_profile=profile_name,
            )
        seeded = True

    world.assign_jobs_to_agents()

    agent_ids = list(world.agents.keys())
    if len(agent_ids) >= 2:
        for idx in range(min(len(agent_ids), 4)):
            current = agent_ids[idx]
            other = agent_ids[(idx + 1) % len(agent_ids)]
            world.update_relationship(current, other, trust=0.25, familiarity=0.2)
            world.record_chat_success(current, other, 0.9)

    telemetry_source = telemetry or getattr(world, "telemetry", None)
    if telemetry_source is not None:
        if is_stub_telemetry(telemetry_source):
            logger.warning("demo_seed_stub_telemetry message='Telemetry stub active; demo narration/history not populated.'")
        else:
            mode = (narration_level or "summary").strip().lower()
            if mode not in {"off", "none"} and hasattr(telemetry_source, "emit_manual_narration"):
                summary = "Avery and Kai prep the town for Blair's arrival."
                payload_data = {
                    "stage": "warmup",
                    "agents_seeded": len(agent_ids),
                }
                priority = mode in {"summary", "highlight", "verbose", "priority"}
                emitted = telemetry_source.emit_manual_narration(
                    message=summary,
                    category="demo_story",
                    tick=world.tick,
                    priority=priority,
                    data=payload_data,
                    dedupe_key="demo_seed_warmup",
                )
                if emitted is None:
                    logger.debug(
                        "Opening demo narration throttled",
                        extra={"tick": world.tick, "mode": mode},
                    )

            if history_window and history_window > 0 and seeded and hasattr(telemetry_source, "publish_tick"):
                telemetry_source.publish_tick(
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


def run_demo_dashboard(
    loop: SimulationLoop,
    *,
    refresh_interval: float,
    max_ticks: int,
    timeline: DemoTimeline,
    palette_state: PaletteState | None,
    personality_filter: str | None = None,
    show_personality_narration: bool = True,
    telemetry_provider: str | None = None,
    policy_provider: str | None = None,
) -> None:
    """Run the interactive Rich dashboard with the supplied timeline."""

    scheduler = DemoScheduler(timeline=timeline, palette_state=palette_state)
    run_dashboard(
        loop,
        refresh_interval=refresh_interval,
        max_ticks=max_ticks,
        palette_state=palette_state,
        on_tick=scheduler.on_tick,
        personality_filter=personality_filter,
        show_personality_narration=show_personality_narration,
        telemetry_provider=telemetry_provider,
        policy_provider=policy_provider,
    )

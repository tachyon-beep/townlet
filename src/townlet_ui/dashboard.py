"""Rich-based console dashboard for Townlet observer UI."""
from __future__ import annotations

import time
from typing import Iterable, Mapping

import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from townlet.console.handlers import ConsoleCommand
from townlet_ui.commands import ConsoleCommandExecutor
from townlet_ui.telemetry import TelemetryClient, TelemetrySnapshot

MAP_AGENT_CHAR = "A"
MAP_CENTER_CHAR = "S"


def render_snapshot(snapshot: TelemetrySnapshot, tick: int, refreshed: str) -> Iterable[Panel]:
    """Yield rich Panels representing the current telemetry snapshot."""
    panels: list[Panel] = []

    header_table = Table.grid(expand=True)
    header_table.add_column(justify="left")
    header_table.add_column(justify="right")
    warning_text = snapshot.schema_warning or "OK"
    warning_style = "yellow" if snapshot.schema_warning else "green"
    header_table.add_row(
        f"[bold]Schema:[/bold] {snapshot.schema_version}",
        f"[bold]Warning:[/bold] [bold {warning_style}] {warning_text}[/] ",
    )
    header_table.add_row(
        f"[bold]Tick:[/bold] {tick}",
        f"[bold]Refreshed:[/bold] {refreshed}",
    )
    panels.append(Panel(header_table, title="Telemetry"))

    employment = snapshot.employment
    emp_table = Table(title="Employment Queue", expand=True)
    emp_table.add_column("Pending", justify="left")
    emp_table.add_column("Count", justify="right")
    emp_table.add_column("Exits Today", justify="right")
    emp_table.add_column("Daily Cap", justify="right")
    emp_table.add_column("Queue Limit", justify="right")
    emp_table.add_column("Review Window", justify="right")
    pending_str = ", ".join(employment.pending) if employment.pending else "(none)"
    emp_table.add_row(
        pending_str,
        str(employment.pending_count),
        str(employment.exits_today),
        str(employment.daily_exit_cap),
        str(employment.queue_limit),
        str(employment.review_window),
    )
    border_style = "red" if employment.pending_count else "green"
    badge = "[bold red]BACKLOG[/bold red]" if employment.pending_count else "[green]CLEAR[/green]"
    panels.append(Panel(emp_table, title=f"Employment — {badge}", border_style=border_style))

    conflict = snapshot.conflict
    conflict_table = Table(title="Conflict Snapshot", expand=True)
    conflict_table.add_column("Queue Cooldowns", justify="right")
    conflict_table.add_column("Ghost Steps", justify="right")
    conflict_table.add_column("Rivalry Agents", justify="right")
    conflict_table.add_row(
        str(conflict.queue_cooldown_events),
        str(conflict.queue_ghost_step_events),
        str(conflict.rivalry_agents),
    )
    conflict_border = "magenta" if conflict.queue_ghost_step_events or conflict.queue_cooldown_events else "blue"
    panels.append(Panel(conflict_table, title="Conflict", border_style=conflict_border))

    relationships = snapshot.relationships
    if relationships is not None:
        rel_table = Table(title="Relationship Churn", expand=True)
        rel_table.add_column("Window", justify="left")
        rel_table.add_column("Evictions", justify="right")
        rel_table.add_column("Top Owners", justify="left")
        rel_table.add_column("Reasons", justify="left")
        window_label = f"{relationships.window_start}–{relationships.window_end}"
        owners_summary = _format_top_entries(relationships.per_owner)
        reasons_summary = _format_top_entries(relationships.per_reason)
        rel_table.add_row(
            window_label,
            str(relationships.total_evictions),
            owners_summary,
            reasons_summary,
        )
        rel_border = "red" if relationships.total_evictions else "green"
        panels.append(Panel(rel_table, title="Relationships", border_style=rel_border))

    agent_table = Table(title="Agents", expand=True)
    agent_table.add_column("Agent")
    agent_table.add_column("Wallet", justify="right")
    agent_table.add_column("Shift State")
    agent_table.add_column("Attendance", justify="right")
    agent_table.add_column("Wages Withheld", justify="right")
    agent_table.add_column("Lateness", justify="right")

    sorted_agents = sorted(
        snapshot.agents,
        key=lambda a: (not a.on_shift, a.attendance_ratio * -1, a.agent_id),
    )
    for agent in sorted_agents:
        row_style = "cyan" if agent.on_shift else None
        shift_state = agent.shift_state + (" *" if agent.on_shift else "")
        agent_table.add_row(
            agent.agent_id,
            f"{agent.wallet:.2f}",
            shift_state,
            f"{agent.attendance_ratio:.2f}",
            f"{agent.wages_withheld:.2f}",
            str(agent.lateness_counter),
            style=row_style,
        )
    panels.append(Panel(agent_table, title="Agents"))

    legend_lines = [
        "Legend: S=self (center), A=other agents.",
        "Employment panel turns red when pending queue > 0.",
        "Conflict panel highlights queue cooldowns/ghost steps; rivalry count shows active edges.",
        "Relationships panel displays eviction churn window, top owners, and reasons.",
    ]
    legend = Text("\n".join(legend_lines), style="dim")
    panels.append(Panel(legend, title="Legend"))

    return panels


def _format_top_entries(entries: Mapping[str, int]) -> str:
    if not entries:
        return "(none)"
    sorted_entries = sorted(entries.items(), key=lambda item: item[1], reverse=True)
    return ", ".join(f"{owner}:{count}" for owner, count in sorted_entries[:3])


def run_dashboard(
    loop,
    *,
    refresh_interval: float = 1.0,
    max_ticks: int = 0,
    approve: str | None = None,
    defer: str | None = None,
    focus_agent: str | None = None,
    show_coords: bool = False,
) -> None:
    """Continuously render dashboard against a SimulationLoop instance."""
    from townlet.console.handlers import create_console_router
    from townlet.world.grid import AgentSnapshot

    if not loop.world.agents:
        loop.world.agents["observer_demo"] = AgentSnapshot(
            agent_id="observer_demo",
            position=(0, 0),
            needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
            wallet=1.0,
        )
        loop.world._assign_jobs_to_agents()  # type: ignore[attr-defined]

    router = create_console_router(loop.telemetry, loop.world)
    client = TelemetryClient()
    console = Console()
    executor = ConsoleCommandExecutor(router)

    if approve:
        executor.submit(ConsoleCommand(name="employment_exit", args=("approve", approve), kwargs={}))
    if defer:
        executor.submit(ConsoleCommand(name="employment_exit", args=("defer", defer), kwargs={}))

    tick = 0
    try:
        while max_ticks <= 0 or tick < max_ticks:
            tick += 1
            loop.step()
            snapshot = client.from_console(router)
            console.clear()
            refreshed = time.strftime("%H:%M:%S")
            for panel in render_snapshot(snapshot, tick=loop.tick, refreshed=refreshed):
                console.print(panel)
            obs_batch = loop.observations.build_batch(loop.world, terminated={})
            map_panel = _build_map_panel(loop, snapshot, obs_batch, focus_agent, show_coords=show_coords)
            if map_panel is not None:
                console.print(map_panel)
            console.print(f"Tick: {loop.tick}")
            time.sleep(refresh_interval)
    except KeyboardInterrupt:
        console.print("[yellow]Dashboard interrupted by user.[/yellow]")
    finally:
        executor.shutdown()


def _build_map_panel(
    loop,
    snapshot: TelemetrySnapshot,
    obs_batch: dict[str, dict[str, np.ndarray]],
    focus_agent: str | None,
    show_coords: bool = False,
) -> Panel | None:
    agents = snapshot.agents
    if not agents:
        return None
    agent_id = focus_agent if focus_agent and any(a.agent_id == focus_agent for a in agents) else agents[0].agent_id
    obs = obs_batch.get(agent_id)
    if not obs:
        return None
    map_tensor = obs.get("map")
    if not isinstance(map_tensor, np.ndarray):
        return None
    agents_channel = map_tensor[1]
    window = agents_channel.shape[0]
    center = window // 2

    panel_text = Text()
    if show_coords:
        header_chars = "   " + "".join(str(x % 10) for x in range(window))
        panel_text.append(header_chars, style="dim")
        panel_text.append("\n")
    for y in range(window):
        if show_coords:
            panel_text.append(str(y % 10) + " ", style="dim")
        for x in range(window):
            if x == center and y == center:
                panel_text.append(MAP_CENTER_CHAR, style="bold yellow")
            elif agents_channel[y, x] > 0.5:
                panel_text.append(MAP_AGENT_CHAR, style="green")
            else:
                panel_text.append(".", style="dim")
        if y != window - 1:
            panel_text.append("\n")
    subtitle = f"Focus: {agent_id}"
    return Panel(panel_text, title=f"Local Map — {agent_id} ({window}×{window})", subtitle=subtitle)

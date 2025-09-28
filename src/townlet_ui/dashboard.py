"""Rich-based console dashboard for Townlet observer UI."""

from __future__ import annotations

import math
import time
from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any

import numpy as np
from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from townlet.console.handlers import ConsoleCommand
from townlet_ui.commands import ConsoleCommandExecutor
from townlet_ui.telemetry import TelemetryClient, TelemetrySnapshot

if TYPE_CHECKING:
    from townlet.core.sim_loop import SimulationLoop
else:
    SimulationLoop = Any  # type: ignore[assignment]

MAP_AGENT_CHAR = "A"
MAP_CENTER_CHAR = "S"


def render_snapshot(
    snapshot: TelemetrySnapshot, tick: int, refreshed: str
) -> Iterable[Panel]:
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
    transport = snapshot.transport
    status_text = (
        "[green]CONNECTED[/green]"
        if transport.connected
        else "[bold red]DISCONNECTED[/bold red]"
    )
    header_table.add_row(
        f"[bold]Transport:[/bold] {status_text}",
        f"[bold]Dropped:[/bold] {transport.dropped_messages}",
    )
    last_success = transport.last_success_tick if transport.last_success_tick is not None else "—"
    last_failure = transport.last_failure_tick if transport.last_failure_tick is not None else "—"
    header_table.add_row(
        f"[bold]Last success tick:[/bold] {last_success}",
        f"[bold]Last failure tick:[/bold] {last_failure}",
    )
    if transport.last_error:
        header_table.add_row(
            "[bold]Last error:[/bold]",
            str(transport.last_error),
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
    badge = (
        "[bold red]BACKLOG[/bold red]"
        if employment.pending_count
        else "[green]CLEAR[/green]"
    )
    panels.append(
        Panel(emp_table, title=f"Employment — {badge}", border_style=border_style)
    )

    conflict = snapshot.conflict
    conflict_table = Table(title="Conflict Snapshot", expand=True)
    conflict_table.add_column("Cooldowns", justify="right")
    conflict_table.add_column("Ghost Steps", justify="right")
    conflict_table.add_column("Rotations", justify="right")
    conflict_table.add_column("Rivalry Agents", justify="right")
    conflict_table.add_row(
        str(conflict.queue_cooldown_events),
        str(conflict.queue_ghost_step_events),
        str(conflict.queue_rotation_events),
        str(conflict.rivalry_agents),
    )
    conflict_border = (
        "magenta"
        if (
            conflict.queue_ghost_step_events
            or conflict.queue_cooldown_events
            or conflict.queue_rotation_events
        )
        else "blue"
    )
    conflict_renderables: list[RenderableType] = [conflict_table]

    history_entries = list(conflict.queue_history[-5:])
    if history_entries:
        history_table = Table(title="Queue Fairness Δ (recent)", expand=True)
        history_table.add_column("Tick", justify="right")
        history_table.add_column("Cooldown Δ", justify="right")
        history_table.add_column("Ghost Δ", justify="right")
        history_table.add_column("Rotation Δ", justify="right")
        for entry in reversed(history_entries):
            history_table.add_row(
                str(entry.tick),
                str(entry.cooldown_delta),
                str(entry.ghost_step_delta),
                str(entry.rotation_delta),
            )
        conflict_renderables.append(history_table)

    rivalry_events = list(conflict.rivalry_events[-5:])
    if rivalry_events:
        rivalry_table = Table(title="Recent Rivalry Events", expand=True)
        rivalry_table.add_column("Tick", justify="right")
        rivalry_table.add_column("Agent A")
        rivalry_table.add_column("Agent B")
        rivalry_table.add_column("Intensity", justify="right")
        rivalry_table.add_column("Reason")
        for event in reversed(rivalry_events):
            rivalry_table.add_row(
                str(event.tick),
                event.agent_a or "—",
                event.agent_b or "—",
                f"{event.intensity:.2f}",
                event.reason or "unknown",
            )
        conflict_renderables.append(rivalry_table)

    if snapshot.stability.alerts:
        alert_text = Text(
            "Active alerts: " + ", ".join(snapshot.stability.alerts),
            style="bold red",
        )
        conflict_renderables.append(alert_text)

    panels.append(
        Panel(
            Group(*conflict_renderables),
            title="Conflict",
            border_style=conflict_border,
        )
    )

    panels.append(_build_anneal_panel(snapshot))
    panels.append(_build_policy_inspector_panel(snapshot))
    panels.append(_build_relationship_overlay_panel(snapshot))
    panels.append(_build_kpi_panel(snapshot))

    narration_panel = _build_narration_panel(snapshot)
    panels.append(narration_panel)

    relationships = snapshot.relationships
    if relationships is not None:
        rel_table = Table(title="Relationship Churn", expand=True)
        rel_table.add_column("Window", justify="left")
        rel_table.add_column("Evictions", justify="right")
        rel_table.add_column("Top Owners", justify="left")
        rel_table.add_column("Reasons", justify="left")
        window_label = f"{relationships.window_start}-{relationships.window_end}"
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

    if snapshot.relationship_updates:
        update_table = Table(title="Relationship Updates", expand=True)
        update_table.add_column("Owner")
        update_table.add_column("Other")
        update_table.add_column("Status")
        update_table.add_column("Trust", justify="right")
        update_table.add_column("Fam", justify="right")
        update_table.add_column("Rivalry", justify="right")
        for update in snapshot.relationship_updates[:8]:
            update_table.add_row(
                update.owner,
                update.other,
                update.status,
                f"{update.trust:.2f}",
                f"{update.familiarity:.2f}",
                f"{update.rivalry:.2f}",
            )
        panels.append(
            Panel(update_table, title="Relationship Updates", border_style="cyan")
        )

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
        "Anneal panel uses green/yellow/red to reflect BC pass/fail and drift flags.",
        "Policy Inspector lists per-agent top actions and probabilities.",
        "Relationship Overlay shows top ties with trust/familiarity/rivalry deltas.",
        "KPI Panel tracks queue intensity, lateness, and late help with colour-coded trends.",
        "Relationships panel displays eviction churn; updates table lists recent tie changes.",
        "Narrations panel lists throttled conflict narrations (! marks priority entries).",
    ]
    legend = Text("\n".join(legend_lines), style="dim")
    panels.append(Panel(legend, title="Legend"))

    return panels


def _format_top_entries(entries: Mapping[str, int]) -> str:
    if not entries:
        return "(none)"
    sorted_entries = sorted(entries.items(), key=lambda item: item[1], reverse=True)
    return ", ".join(f"{owner}:{count}" for owner, count in sorted_entries[:3])


def _build_narration_panel(snapshot: TelemetrySnapshot) -> Panel:
    narrations = snapshot.narrations
    if narrations:
        table = Table(expand=True)
        table.add_column("Tick", justify="right")
        table.add_column("Category")
        table.add_column("Message")
        table.add_column("!", justify="center")
        for entry in narrations[:5]:
            priority_flag = "[bold red]![/bold red]" if entry.priority else ""
            table.add_row(
                str(entry.tick),
                entry.category,
                entry.message,
                priority_flag,
            )
        border_style = (
            "yellow" if any(entry.priority for entry in narrations) else "blue"
        )
        return Panel(table, title="Narrations", border_style=border_style)

    body = Text("No recent narrations", style="dim")
    return Panel(body, title="Narrations", border_style="green")


def _build_anneal_panel(snapshot: TelemetrySnapshot) -> Panel:
    status = snapshot.anneal
    if status is None:
        body = Text("No anneal telemetry yet", style="dim")
        return Panel(body, title="Anneal Status", border_style="green")

    meta_table = Table(title="Cycle", expand=True)
    meta_table.add_column("Cycle", justify="right")
    meta_table.add_column("Stage")
    meta_table.add_column("Dataset")
    meta_table.add_row(
        _safe_format(status.cycle),
        status.stage or "-",
        status.dataset or "-",
    )

    bc_table = Table(title="BC Gate", expand=True)
    bc_table.add_column("Accuracy", justify="right")
    bc_table.add_column("Threshold", justify="right")
    bc_table.add_column("Passed", justify="center")
    bc_table.add_row(
        _format_optional_float(status.bc_accuracy),
        _format_optional_float(status.bc_threshold),
        "✅" if status.bc_passed else "❌",
    )
    drift_table = Table.grid(expand=True)
    drift_table.add_column(justify="left")
    drift_table.add_row(
        "Loss drift: {} (baseline {})".format(
            "⚠️" if status.loss_flag else "OK",
            _format_optional_float(status.loss_baseline),
        )
    )
    drift_table.add_row(
        "Queue drift: {} (baseline {})".format(
            "⚠️" if status.queue_flag else "OK",
            _format_optional_float(status.queue_baseline),
        )
    )
    drift_table.add_row(
        "Intensity drift: {} (baseline {})".format(
            "⚠️" if status.intensity_flag else "OK",
            _format_optional_float(status.intensity_baseline),
        )
    )
    composite = Panel.fit(
        drift_table,
        title="Drift",
        border_style=(
            "yellow"
            if (status.loss_flag or status.queue_flag or status.intensity_flag)
            else "green"
        ),
    )
    container = Table.grid(expand=True)
    container.add_row(meta_table)
    container.add_row(bc_table)
    container.add_row(composite)

    border_style = (
        "red"
        if not status.bc_passed
        else (
            "yellow"
            if (status.loss_flag or status.queue_flag or status.intensity_flag)
            else "green"
        )
    )
    return Panel(container, title="Anneal Status", border_style=border_style)


def _safe_format(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.1f}"


def _format_optional_float(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.3f}"


def _build_policy_inspector_panel(snapshot: TelemetrySnapshot) -> Panel:
    entries = snapshot.policy_inspector
    if not entries:
        body = Text("No policy inspector data yet", style="dim")
        return Panel(body, title="Policy Inspector", border_style="green")

    table = Table(expand=True)
    table.add_column("Agent")
    table.add_column("Selected")
    table.add_column("p(selected)", justify="right")
    table.add_column("Value", justify="right")
    table.add_column("Top Actions")

    for entry in entries[:8]:
        try:
            selected_prob = math.exp(entry.log_prob)
        except OverflowError:
            selected_prob = float("inf")
        tops = (
            ", ".join(
                f"{action.action}:{action.probability:.2f}"
                for action in entry.top_actions[:3]
            )
            or "-"
        )
        table.add_row(
            entry.agent_id,
            entry.selected_action or "-",
            f"{selected_prob:.2f}",
            f"{entry.value_pred:.2f}",
            tops,
        )

    border_style = "green"
    if any(action.probability < 0.2 for e in entries for action in e.top_actions[:1]):
        border_style = "yellow"
    return Panel(table, title="Policy Inspector", border_style=border_style)


def _build_relationship_overlay_panel(snapshot: TelemetrySnapshot) -> Panel:
    overlay = snapshot.relationship_overlay
    if not overlay:
        body = Text("No relationship overlays yet", style="dim")
        return Panel(body, title="Relationship Overlay", border_style="green")

    table = Table(expand=True)
    table.add_column("Owner")
    table.add_column("Other")
    table.add_column("Trust", justify="right")
    table.add_column("ΔT", justify="right")
    table.add_column("Fam", justify="right")
    table.add_column("ΔF", justify="right")
    table.add_column("Riv", justify="right")
    table.add_column("ΔR", justify="right")

    for owner, ties in overlay.items():
        for entry in ties:
            table.add_row(
                owner,
                entry.other,
                f"{entry.trust:.2f}",
                _format_delta(entry.delta_trust),
                f"{entry.familiarity:.2f}",
                _format_delta(entry.delta_familiarity),
                f"{entry.rivalry:.2f}",
                _format_delta(entry.delta_rivalry, inverse=True),
            )

    border_style = "green"
    if any(abs(entry.delta_trust) > 0.1 for ties in overlay.values() for entry in ties):
        border_style = "yellow"
    return Panel(table, title="Relationship Overlay", border_style=border_style)


def _format_delta(value: float, inverse: bool = False) -> str:
    if value == 0:
        return "±0.00"
    arrow = "↑" if (value > 0) ^ inverse else "↓"
    colour = "green" if (value > 0) ^ inverse else "red"
    return f"[{colour}]{value:+.2f} {arrow}[/]"


def _build_kpi_panel(snapshot: TelemetrySnapshot) -> Panel:
    history = snapshot.kpis
    if not history:
        body = Text("No KPI history yet", style="dim")
        return Panel(body, title="KPIs", border_style="green")

    table = Table(expand=True)
    table.add_column("Metric")
    table.add_column("Latest", justify="right")
    table.add_column("Trend", justify="left")

    for key in ("queue_conflict_intensity", "employment_lateness", "late_help_events"):
        series = history.get(key, [])
        if not series:
            continue
        latest = series[-1]
        trend_symbol, colour = _trend_from_series(series)
        label = _humanize_kpi(key)
        table.add_row(
            label,
            f"{latest:.2f}",
            f"[{colour}]{trend_symbol}[/]",
        )

    if not table.rows:
        body = Text("No KPI history yet", style="dim")
        return Panel(body, title="KPIs", border_style="green")
    return Panel(table, title="KPIs", border_style="blue")


def _trend_from_series(series: list[float]) -> tuple[str, str]:
    if len(series) < 2:
        return "→", "green"
    delta = series[-1] - series[-2]
    if series[-2] == 0:
        pct = delta
    else:
        pct = delta / abs(series[-2])
    if pct > 0.1:
        return "↑", "red"
    if pct < -0.1:
        return "↓", "green"
    return "→", "yellow"


def _humanize_kpi(key: str) -> str:
    mapping = {
        "queue_conflict_intensity": "Queue Intensity",
        "employment_lateness": "Lateness",
        "late_help_events": "Late Help",
    }
    return mapping.get(key, key)


def run_dashboard(
    loop: SimulationLoop,
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
        assign_jobs = getattr(loop.world, "_assign_jobs_to_agents", None)
        if callable(assign_jobs):
            assign_jobs()

    router = create_console_router(loop.telemetry, loop.world, config=loop.config)
    client = TelemetryClient()
    console = Console()
    executor = ConsoleCommandExecutor(router)

    if approve:
        executor.submit(
            ConsoleCommand(name="employment_exit", args=("approve", approve), kwargs={})
        )
    if defer:
        executor.submit(
            ConsoleCommand(name="employment_exit", args=("defer", defer), kwargs={})
        )

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
            map_panel = _build_map_panel(
                snapshot, obs_batch, focus_agent, show_coords=show_coords
            )
            if map_panel is not None:
                console.print(map_panel)
            console.print(f"Tick: {loop.tick}")
            time.sleep(refresh_interval)
    except KeyboardInterrupt:
        console.print("[yellow]Dashboard interrupted by user.[/yellow]")
    finally:
        executor.shutdown()


def _build_map_panel(
    snapshot: TelemetrySnapshot,
    obs_batch: Mapping[str, dict[str, np.ndarray]],
    focus_agent: str | None,
    show_coords: bool = False,
) -> Panel | None:
    agents = snapshot.agents
    if not agents:
        return None
    agent_id = (
        focus_agent
        if focus_agent and any(a.agent_id == focus_agent for a in agents)
        else agents[0].agent_id
    )
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
    return Panel(
        panel_text,
        title=f"Local Map - {agent_id} ({window}x{window})",
        subtitle=subtitle,
    )

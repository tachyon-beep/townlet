"""Rich-based console dashboard for Townlet observer UI."""

from __future__ import annotations

import difflib
import itertools
import math
import re
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from rich.columns import Columns
from rich.console import Console, Group, RenderableType
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

try:  # pragma: no cover - fallback for older Rich versions
    from rich.tooltip import Tooltip
except ImportError:  # pragma: no cover - fallback shim

    class Tooltip:  # type: ignore[too-many-ancestors]
        """Minimal shim when rich.tooltip.Tooltip is unavailable."""

        def __init__(self, renderable: RenderableType, text: str) -> None:
            self.renderable = renderable
            self.text = text

        def __rich_console__(self, console: Console, options) -> Iterable[RenderableType]:
            yield from console.render(self.renderable, options)


from townlet.console.handlers import ConsoleCommand, create_console_router
from townlet.core.utils import policy_provider_name, telemetry_provider_name
from townlet.dto.observations import ObservationEnvelope
from townlet_ui.commands import CommandQueueFullError, ConsoleCommandExecutor
from townlet_ui.telemetry import (
    AgentSummary,
    AnnealStatus,
    FriendSummary,
    NarrationEntry,
    PersonalitySnapshotEntry,
    PromotionSnapshot,
    RelationshipChurn,
    RelationshipSummarySnapshot,
    RivalSummary,
    SocialEventEntry,
    TelemetryClient,
    TelemetrySnapshot,
)

if TYPE_CHECKING:
    from townlet.core.sim_loop import SimulationLoop
else:
    SimulationLoop = Any  # type: ignore[assignment]

MAP_AGENT_CHAR = "A"
MAP_CENTER_CHAR = "S"

NARRATION_CATEGORY_STYLES: dict[str, tuple[str, str]] = {
    "utility_outage": ("Utility Outage", "bold red"),
    "shower_complete": ("Shower Complete", "cyan"),
    "sleep_complete": ("Sleep Complete", "green"),
    "queue_conflict": ("Queue Conflict", "magenta"),
    "personality_event": ("Personality", "magenta"),
}

NEED_SPARK_STYLES: Mapping[str, str] = {
    "hunger": "magenta",
    "hygiene": "cyan",
    "energy": "yellow",
}

PROFILE_STYLE_MAP: Mapping[str, str] = {
    "socialite": "magenta",
    "industrious": "yellow",
    "stoic": "cyan",
    "balanced": "white",
}

PERSONALITY_TRAIT_ALIASES: Mapping[str, str] = {
    "ext": "extroversion",
    "extroversion": "extroversion",
    "forg": "forgiveness",
    "forgiveness": "forgiveness",
    "amb": "ambition",
    "ambition": "ambition",
}

PERSONALITY_TRAIT_LABELS: Mapping[str, str] = {
    "extroversion": "Extroversion",
    "forgiveness": "Forgiveness",
    "ambition": "Ambition",
}

FILTER_COMMAND_PREFIX = "filter"


@dataclass(frozen=True)
class PersonalityFilterSpec:
    """Structured representation of a personality filter request."""

    profile_prefix: str | None = None
    trait_key: str | None = None
    trait_operator: str | None = None
    trait_threshold: float | None = None

    def describe(self) -> str:
        parts: list[str] = []
        if self.profile_prefix:
            parts.append(f"profile={self.profile_prefix}")
        if self.trait_key and self.trait_operator and self.trait_threshold is not None:
            trait_label = PERSONALITY_TRAIT_LABELS.get(self.trait_key, self.trait_key)
            parts.append(f"{trait_label} {self.trait_operator} {self.trait_threshold:+.2f}")
        return " & ".join(parts)


_FILTER_DIRECTIVE_RE = re.compile(r"^(?P<kind>profile|trait)\s*:\s*(?P<body>.+)$")
_FILTER_TRAIT_RE = re.compile(
    r"^(?P<key>[a-z_]+)\s*(?P<op>>=|<=|==|=|>|<)\s*(?P<value>[-+]?\d*\.?\d+)",
)


def _parse_personality_filter(raw: str | None) -> PersonalityFilterSpec | None:
    if raw is None:
        return None
    text = raw.strip()
    if not text:
        return None

    directive_match = _FILTER_DIRECTIVE_RE.match(text.lower())
    if directive_match:
        kind = directive_match.group("kind")
        body = directive_match.group("body").strip()
        if kind == "profile":
            return PersonalityFilterSpec(profile_prefix=body.lower())
        if kind == "trait":
            trait_match = _FILTER_TRAIT_RE.match(body.lower())
            if not trait_match:
                return None
            raw_key = trait_match.group("key")
            trait_key = PERSONALITY_TRAIT_ALIASES.get(raw_key)
            if trait_key is None:
                return None
            operator = trait_match.group("op")
            threshold = float(trait_match.group("value"))
            if operator == "=":
                operator = "=="
            return PersonalityFilterSpec(
                trait_key=trait_key,
                trait_operator=operator,
                trait_threshold=threshold,
            )
        return None

    # Default to treating the text as a profile prefix
    return PersonalityFilterSpec(profile_prefix=text.lower())


def _compare_trait_value(value: float, operator: str, threshold: float) -> bool:
    if operator == ">=":
        return value >= threshold
    if operator == ">":
        return value > threshold
    if operator == "<=":
        return value <= threshold
    if operator == "<":
        return value < threshold
    if operator == "==":
        return math.isclose(value, threshold, abs_tol=1e-6)
    return False


def _matches_personality_filter(
    entry: PersonalitySnapshotEntry,
    spec: PersonalityFilterSpec,
) -> bool:
    if spec.profile_prefix and not entry.profile.lower().startswith(spec.profile_prefix):
        return False
    if spec.trait_key and spec.trait_operator and spec.trait_threshold is not None:
        trait_value = entry.traits.get(spec.trait_key, 0.0)
        if not _compare_trait_value(trait_value, spec.trait_operator, spec.trait_threshold):
            return False
    return True


@dataclass(frozen=True)
class PaletteCommandMeta:
    """Metadata describing a console command for palette display."""

    name: str
    mode: str
    usage: str
    description: str


@dataclass
class PaletteState:
    """Represents the rendered state of the palette overlay."""

    visible: bool = False
    query: str = ""
    mode_filter: str = "all"  # "viewer", "admin", or "all"
    max_results: int = 7
    highlight_index: int = 0
    history_limit: int = 5
    pending: int = 0
    status_message: str | None = None
    status_style: str = "dim"
    personality_filter: str | None = None

    def clamp_history(self, window: int | None) -> None:
        if window is None:
            return
        self.history_limit = max(1, window // 2 or 1)


def _build_personality_filter_commands(
    personalities: Mapping[str, PersonalitySnapshotEntry] | None,
) -> list[PaletteCommandMeta]:
    if not personalities:
        return []

    commands: list[PaletteCommandMeta] = []
    commands.append(
        PaletteCommandMeta(
            name=f"{FILTER_COMMAND_PREFIX}:clear",
            mode="ui",
            usage="clear personality filter",
            description="Show all agents (remove personality filters)",
        )
    )

    profiles = sorted({entry.profile.lower() for entry in personalities.values()})
    for profile in profiles:
        commands.append(
            PaletteCommandMeta(
                name=f"{FILTER_COMMAND_PREFIX}:profile:{profile}",
                mode="ui",
                usage=f"profile:{profile}",
                description=f"Filter agent cards to the {profile.title()} archetype",
            )
        )

    trait_thresholds: tuple[tuple[str, str, float, str], ...] = (
        (">=", ">=", 0.5, "High"),
        ("<=", "<=", -0.5, "Low"),
    )
    for trait_key, trait_label in PERSONALITY_TRAIT_LABELS.items():
        for command_suffix, operator, threshold, adjective in trait_thresholds:
            commands.append(
                PaletteCommandMeta(
                    name=(f"{FILTER_COMMAND_PREFIX}:trait:{trait_key}{command_suffix}{threshold}"),
                    mode="ui",
                    usage=f"trait:{trait_key}{operator}{threshold}",
                    description=(f"Filter agents with {adjective.lower()} {trait_label}"),
                )
            )

    # Deduplicate command names while preserving order
    seen: set[str] = set()
    unique_commands: list[PaletteCommandMeta] = []
    for command in commands:
        if command.name in seen:
            continue
        seen.add(command.name)
        unique_commands.append(command)
    return unique_commands


@dataclass
class AgentCardState:
    """Mutable state for paginating and rotating agent card panels."""

    page_size: int = 6
    rotate: bool = True
    rotate_interval: int = 12
    page: int = 0
    _last_rotate_tick: int | None = field(default=None, repr=False)

    def update(
        self,
        tick: int,
        agent_ids: Sequence[str],
        *,
        focus_agent: str | None = None,
    ) -> int:
        """Update pagination state and return total number of pages."""

        total_agents = len(agent_ids)
        page_size = max(1, self.page_size if self.page_size > 0 else total_agents or 1)
        total_pages = max(1, math.ceil(total_agents / page_size)) if total_agents else 1

        if focus_agent and focus_agent in agent_ids:
            target_page = agent_ids.index(focus_agent) // page_size
            if target_page != self.page:
                self.page = target_page
                self._last_rotate_tick = tick
        elif self.rotate and total_pages > 1 and self.rotate_interval > 0:
            if self._last_rotate_tick is None:
                self._last_rotate_tick = tick
            elif tick - self._last_rotate_tick >= self.rotate_interval:
                self.page = (self.page + 1) % total_pages
                self._last_rotate_tick = tick

        if self.page >= total_pages:
            self.page = total_pages - 1
        if self.page < 0:
            self.page = 0
        return total_pages


@dataclass
class DashboardState:
    """Top-level dashboard rendering state shared across ticks."""

    agent_cards: AgentCardState = field(default_factory=AgentCardState)


def _extract_palette_commands(
    snapshot: TelemetrySnapshot,
    *,
    include_filters: bool = False,
) -> list[PaletteCommandMeta]:
    commands: list[PaletteCommandMeta] = []
    metadata = getattr(snapshot, "console_commands", {})
    if isinstance(metadata, Mapping):
        for name, entry in metadata.items():
            if not isinstance(entry, Mapping):
                continue
            mode = str(entry.get("mode", "viewer"))
            usage = str(entry.get("usage", name))
            description = str(entry.get("description", "")).strip()
            commands.append(
                PaletteCommandMeta(
                    name=str(name),
                    mode=mode.lower() or "viewer",
                    usage=usage,
                    description=description,
                )
            )
    if include_filters:
        personality_map = getattr(snapshot, "personalities", {})
        commands.extend(_build_personality_filter_commands(personality_map))
    commands.sort(key=lambda item: item.name)
    return commands


def _score_palette_match(command: PaletteCommandMeta, query: str) -> float:
    if not query:
        return 1.0
    query_norm = query.lower().strip()
    if not query_norm:
        return 1.0
    name_ratio = difflib.SequenceMatcher(None, query_norm, command.name.lower()).ratio()
    usage_ratio = difflib.SequenceMatcher(None, query_norm, command.usage.lower()).ratio()
    description_ratio = difflib.SequenceMatcher(None, query_norm, command.description.lower()).ratio() if command.description else 0.0
    return max(name_ratio, usage_ratio, description_ratio * 0.85)


def _search_palette_commands(
    commands: list[PaletteCommandMeta],
    palette: PaletteState,
) -> list[PaletteCommandMeta]:
    filtered: list[tuple[float, PaletteCommandMeta]] = []
    mode_filter = palette.mode_filter.lower()
    for command in commands:
        if mode_filter in {"viewer", "admin"} and command.mode != mode_filter:
            continue
        score = _score_palette_match(command, palette.query)
        filtered.append((score, command))
    if not filtered:
        return []
    filtered.sort(key=lambda item: (-item[0], item[1].name))
    results = [entry[1] for entry in filtered[: max(1, palette.max_results)]]
    return results


def _format_palette_filter_label(mode_filter: str) -> str:
    lowered = mode_filter.lower()
    if lowered == "viewer":
        return "viewer"
    if lowered == "admin":
        return "admin"
    return "all"


def _build_palette_overlay(
    snapshot: TelemetrySnapshot,
    palette: PaletteState,
    *,
    personality_enabled: bool = False,
) -> Panel | None:
    if not palette.visible:
        return None

    commands = _extract_palette_commands(snapshot, include_filters=personality_enabled)
    results = _search_palette_commands(commands, palette)
    highlight_index = palette.highlight_index if results else -1
    if highlight_index >= len(results):
        highlight_index = len(results) - 1
    if highlight_index < 0:
        highlight_index = 0

    header = Table.grid(expand=True)
    header.add_column(justify="left")
    header.add_column(justify="center")
    header.add_column(justify="right")
    header.add_column(justify="right")
    query_text = palette.query.strip() or "[dim](all commands)[/]"
    header.add_row(
        f"[bold]Search:[/bold] {query_text}",
        f"[bold]Pending:[/bold] {palette.pending}",
        f"[bold]Filter:[/bold] {_format_palette_filter_label(palette.mode_filter)}",
        (f"[bold]Personality:[/bold] {palette.personality_filter or '—'}" if personality_enabled else "[bold]Personality:[/bold] disabled"),
    )

    suggestion_table = Table.grid(padding=(0, 1), expand=True)
    suggestion_table.add_column(width=2)
    suggestion_table.add_column(ratio=2)
    suggestion_table.add_column(ratio=3)

    if results:
        for idx, command in enumerate(results):
            marker = ">" if idx == highlight_index else " "
            marker_style = "bold cyan" if idx == highlight_index else "dim"
            label = f"{command.name} [{command.mode}]"
            description = command.description or command.usage
            if idx == highlight_index:
                label = f"[bold]{label}[/]"
                description = f"[dim]{description}[/]"
            suggestion_table.add_row(
                f"[{marker_style}]{marker}[/]",
                label,
                description,
            )
    else:
        suggestion_table.add_row("", "[dim]No commands match current search.[/]", "")

    instruction_parts = [
        "Ctrl+P toggle",
        "Tab cycles fields",
        "Enter dispatch",
        "Esc close",
    ]
    if personality_enabled:
        instruction_parts.append("Type or select filter: profile:<name> / trait:ext>=0.5")
    instructions = Text(" • ".join(instruction_parts), style="dim")

    status_text: Text | None = None
    if palette.status_message:
        status_text = Text(palette.status_message, style=palette.status_style)

    history_limit = max(1, palette.history_limit)
    history_entries = list(getattr(snapshot, "console_results", ()))
    history_rows: list[Mapping[str, Any]] = []
    if history_entries:
        history_rows = history_entries[-history_limit:][::-1]

    history_table = Table.grid(padding=(0, 1), expand=True)
    history_table.add_column(width=2)
    history_table.add_column(ratio=2)
    history_table.add_column(ratio=3)
    if history_rows:
        for entry in history_rows:
            status = str(entry.get("status", ""))
            icon = "✓" if status == "ok" else "⚠"
            style = "green" if status == "ok" else "yellow"
            name = str(entry.get("name", ""))
            if status == "ok":
                result_payload = entry.get("result", {})
                summary = str(result_payload) if isinstance(result_payload, Mapping) else "ok"
            else:
                error_payload = entry.get("error", {})
                if isinstance(error_payload, Mapping):
                    summary = str(error_payload.get("message")) or str(error_payload.get("code", "error"))
                else:
                    summary = str(error_payload)
            history_table.add_row(
                f"[{style}]{icon}[/]",
                f"{name}",
                summary,
            )
    else:
        history_table.add_row("", "[dim]No recent command activity.[/]", "")

    body_renderables = [header]
    if status_text is not None:
        body_renderables.append(status_text)
    body_renderables.extend([suggestion_table, instructions, history_table])
    body = Group(*body_renderables)
    return Panel(body, title="Command Palette", border_style="cyan", expand=True)


def dispatch_palette_selection(
    snapshot: TelemetrySnapshot,
    palette: PaletteState,
    executor: ConsoleCommandExecutor,
    *,
    personality_enabled: bool = False,
    payload_override: Mapping[str, Any] | None = None,
    enqueue: bool = True,
) -> ConsoleCommand | None:
    """Dispatch the highlighted palette command via the executor.

    Returns the normalised `ConsoleCommand` produced by the executor so callers
    can preview or log the outgoing payload. When the executor queue is
    saturated, updates palette state with a warning banner and re-raises the
    `CommandQueueFullError` so the caller can react (e.g. show dialog).
    """

    commands = _search_palette_commands(
        _extract_palette_commands(snapshot, include_filters=personality_enabled),
        palette,
    )
    if not commands:
        raise ValueError("No palette commands available for current selection")

    index = min(max(palette.highlight_index, 0), len(commands) - 1)
    selected = commands[index]
    payload: Mapping[str, Any]
    if payload_override is not None:
        payload = payload_override
    else:
        payload = {"name": selected.name, "args": (), "kwargs": {}}

    if personality_enabled and selected.name.startswith(f"{FILTER_COMMAND_PREFIX}:"):
        action = selected.name.split(":", 2)
        if len(action) >= 2:
            directive = action[1]
            if directive == "clear":
                palette.personality_filter = None
                palette.status_message = "Cleared personality filter"
                palette.status_style = "green"
                return None
            if directive == "profile" and len(action) == 3:
                palette.personality_filter = f"profile:{action[2]}"
                palette.status_message = f"Personality filter set to profile:{action[2]}"
                palette.status_style = "cyan"
                return None
            if directive == "trait" and len(action) == 3:
                # usage already normalised (e.g., trait:extroversion>=0.5)
                palette.personality_filter = selected.usage
                palette.status_message = f"Personality filter set to {selected.usage}"
                palette.status_style = "cyan"
                return None

    try:
        command = executor.submit_payload(payload, enqueue=enqueue)
    except CommandQueueFullError as exc:
        max_pending = exc.max_pending or exc.pending
        palette.status_message = f"Queue saturated ({exc.pending}/{max_pending})"
        palette.status_style = "yellow"
        palette.pending = exc.pending
        raise

    palette.pending = executor.pending_count()
    if enqueue:
        palette.status_message = f"Dispatched {selected.name}"
        palette.status_style = "green"
    else:
        palette.status_message = f"Preview {selected.name}"
        palette.status_style = "cyan"
    return command


def render_snapshot(
    snapshot: TelemetrySnapshot,
    tick: int,
    refreshed: str,
    *,
    palette: PaletteState | None = None,
    state: DashboardState | None = None,
    focus_agent: str | None = None,
    personality_filter: str | None = None,
    personality_enabled: bool = False,
    show_personality_narration: bool = True,
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
    status_text = "[green]CONNECTED[/green]" if transport.connected else "[bold red]DISCONNECTED[/bold red]"
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
    health = snapshot.health
    if health is not None:
        tick_duration_text = f"{health.tick_duration_ms:.1f} ms"
        header_table.add_row(
            f"[bold]Queue backlog:[/bold] {health.telemetry_queue}",
            f"[bold]Tick duration:[/bold] {tick_duration_text}",
        )
        perturbation_status = f"pending {health.perturbations_pending} / active {health.perturbations_active}"
        header_table.add_row(
            f"[bold]Perturbations:[/bold] {perturbation_status}",
            f"[bold]Exit queue:[/bold] {health.employment_exit_queue}",
        )
    else:
        header_table.add_row(
            f"[bold]Queue backlog:[/bold] {transport.queue_length}",
            "[bold]Last flush:[/bold] "
            + (f"{transport.last_flush_duration_ms:.1f} ms" if transport.last_flush_duration_ms is not None else "—"),
        )
    if transport.last_error:
        header_table.add_row(
            "[bold]Last error:[/bold]",
            str(transport.last_error),
        )
    panels.append(Panel(header_table, title="Telemetry"))

    if palette is not None:
        if palette.personality_filter is None and personality_filter:
            palette.personality_filter = personality_filter
        overlay = _build_palette_overlay(
            snapshot,
            palette,
            personality_enabled=personality_enabled,
        )
        if overlay is not None:
            panels.append(overlay)

    banner = _build_perturbation_banner(snapshot)
    if banner is not None:
        panels.append(banner)

    perturbation_panel = _build_perturbation_panel(snapshot)
    if perturbation_panel is not None:
        panels.append(perturbation_panel)

    active_personality_filter = personality_filter
    if palette is not None and palette.personality_filter:
        active_personality_filter = palette.personality_filter

    agent_cards_panel = _build_agent_cards_panel(
        snapshot,
        tick,
        focus_agent=focus_agent,
        state=state.agent_cards if state else None,
        personality_filter=active_personality_filter,
        personality_enabled=personality_enabled,
    )
    if agent_cards_panel is not None:
        panels.append(agent_cards_panel)

    economy_table = Table(title="Economy Settings", expand=True)
    economy_table.add_column("Key")
    economy_table.add_column("Value", justify="right")
    for key in sorted(snapshot.economy_settings):
        value = snapshot.economy_settings[key]
        economy_table.add_row(key, f"{value:.2f}")

    utilities_table = Table(title="Utilities", expand=True)
    utilities_table.add_column("Utility")
    utilities_table.add_column("Status")
    any_outage = False
    for name, online in sorted(snapshot.utilities.items()):
        if online:
            status_render = "[green]ONLINE[/green]"
        else:
            status_render = "[bold red]OFFLINE[/bold red]"
            any_outage = True
        utilities_table.add_row(name.title(), status_render)

    spikes_renderables: list[RenderableType] = []
    if snapshot.price_spikes:
        spikes_table = Table(title="Active Price Spikes", expand=True)
        spikes_table.add_column("Event")
        spikes_table.add_column("Magnitude", justify="right")
        spikes_table.add_column("Targets")
        for entry in snapshot.price_spikes:
            targets = ", ".join(entry.targets) if entry.targets else "global"
            spikes_table.add_row(entry.event_id, f"{entry.magnitude:.2f}", targets)
        spikes_renderables.append(spikes_table)

    economy_renderables: list[RenderableType] = [economy_table, utilities_table]
    if spikes_renderables:
        economy_renderables.extend(spikes_renderables)

    economy_border = "green"
    if any_outage:
        economy_border = "bold red"
    elif snapshot.price_spikes:
        economy_border = "yellow"

    panels.append(
        Panel(
            Group(*economy_renderables),
            title="Economy & Utilities",
            border_style=economy_border,
        )
    )

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
        "magenta" if (conflict.queue_ghost_step_events or conflict.queue_cooldown_events or conflict.queue_rotation_events) else "blue"
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

    visible_narrations = list(snapshot.narrations)
    if not show_personality_narration:
        visible_narrations = [entry for entry in visible_narrations if entry.category != "personality_event"]
    narration_panel = _build_narration_panel(visible_narrations)
    panels.append(narration_panel)

    summary = snapshot.relationship_summary
    relationships = snapshot.relationships
    if relationships is None and summary is not None:
        churn_metrics = summary.churn_metrics
        if churn_metrics:
            owners_field = churn_metrics.get("owners")
            reasons_field = churn_metrics.get("reasons")
            relationships = RelationshipChurn(
                window_start=int(churn_metrics.get("window_start", 0) or 0),
                window_end=int(churn_metrics.get("window_end", 0) or 0),
                total_evictions=int(churn_metrics.get("total", 0) or 0),
                per_owner={
                    str(owner): int(count)
                    for owner, count in (owners_field or {}).items()
                    if isinstance(owner, str) and isinstance(count, (int, float))
                }
                if isinstance(owners_field, Mapping)
                else {},
                per_reason={
                    str(reason): int(count)
                    for reason, count in (reasons_field or {}).items()
                    if isinstance(reason, str) and isinstance(count, (int, float))
                }
                if isinstance(reasons_field, Mapping)
                else {},
            )

    social_panel = _build_social_panel(summary, relationships, snapshot.social_events)
    if social_panel is not None:
        panels.append(social_panel)
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
        panels.append(Panel(update_table, title="Relationship Updates", border_style="cyan"))

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
        "Social panel highlights top friends/rivals, churn aggregates, and recent chats/avoidance.",
        "Narrations panel lists throttled conflict narrations (! marks priority entries).",
    ]
    legend = Text("\n".join(legend_lines), style="dim")
    panels.append(Panel(legend, title="Legend"))

    return panels


def _build_social_panel(
    summary: RelationshipSummarySnapshot | None,
    relationships: RelationshipChurn | None,
    events: tuple[SocialEventEntry, ...],
) -> Panel | None:
    status_panel = _build_social_status_panel(summary)
    cards_panel = _build_social_cards_panel(summary)
    churn_panel = _build_social_churn_panel(summary, relationships)
    events_panel = _build_social_events_panel(events)

    renderables: list[RenderableType] = []
    if status_panel is not None:
        renderables.append(status_panel)
    if cards_panel is not None:
        renderables.append(cards_panel)
    if churn_panel is not None:
        renderables.append(churn_panel)
    if events_panel is not None:
        renderables.append(events_panel)

    if not renderables:
        body = Text("No social telemetry available", style="dim")
        return Panel(body, title="Social", border_style="green")

    border = "magenta"
    if churn_panel is not None and isinstance(churn_panel, Panel):
        total_evictions = _extract_churn_total(summary, relationships)
        if total_evictions:
            border = "red"

    return Panel(Group(*renderables), title="Social", border_style=border)


def _build_agent_cards_panel(
    snapshot: TelemetrySnapshot,
    tick: int,
    *,
    focus_agent: str | None = None,
    state: AgentCardState | None = None,
    personality_filter: str | None = None,
    personality_enabled: bool = False,
) -> Panel | None:
    agents = snapshot.agents
    if not agents:
        return None

    summary_map = snapshot.relationship_summary.per_agent if snapshot.relationship_summary else {}
    history = snapshot.history
    sorted_agents = sorted(
        agents,
        key=lambda a: (not a.on_shift, a.attendance_ratio * -1, a.agent_id),
    )

    personality_map: Mapping[str, PersonalitySnapshotEntry] = getattr(snapshot, "personalities", {})
    filter_spec = _parse_personality_filter(personality_filter) if personality_filter else None
    filter_label: str | None = None
    filter_active = False
    filter_notice: Text | None = None
    if filter_spec:
        filter_label = filter_spec.describe() or personality_filter
        filter_active = True
        if personality_enabled and isinstance(personality_map, Mapping) and personality_map:
            filtered_agents: list[AgentSummary] = []
            for agent in sorted_agents:
                entry = personality_map.get(agent.agent_id)
                if not isinstance(entry, PersonalitySnapshotEntry):
                    continue
                if _matches_personality_filter(entry, filter_spec):
                    filtered_agents.append(agent)
            if filtered_agents:
                sorted_agents = filtered_agents
            else:
                description = filter_label or "filter"
                body = Text(
                    f"No agents match {description}",
                    style="yellow",
                )
                return Panel(body, title=f"Agents — filter: {description}", border_style="cyan")
        else:
            filter_notice = Text(
                "Personality filters require personality telemetry",
                style="yellow",
            )

    agent_ids = [agent.agent_id for agent in sorted_agents]

    card_state = state
    total_pages = 1
    page_size = len(sorted_agents)
    page_index = 0
    if card_state is not None:
        total_pages = card_state.update(tick, agent_ids, focus_agent=focus_agent)
        page_size = max(1, card_state.page_size if card_state.page_size > 0 else len(sorted_agents))
        page_index = card_state.page
    start = page_index * page_size
    end = start + page_size
    visible_agents = sorted_agents[start:end] or sorted_agents[:page_size]

    cards: list[Panel] = []
    for agent in visible_agents:
        card_table = Table.grid(expand=True)
        subtitle_parts: list[str] = []
        if agent.job_id:
            subtitle_parts.append(agent.job_id)
        subtitle_parts.append(agent.shift_state)
        subtitle = " • ".join(part for part in subtitle_parts if part)

        personality_entry = None
        if personality_enabled and isinstance(personality_map, Mapping):
            personality_entry = personality_map.get(agent.agent_id)
        if personality_enabled and isinstance(personality_entry, PersonalitySnapshotEntry):
            profile_key = personality_entry.profile.lower()
            badge_color = PROFILE_STYLE_MAP.get(profile_key, "white")
            badge_label = personality_entry.profile.title()
            badge_text = Text(f" {badge_label} ", style=f"bold {badge_color}")
            badge_text.stylize(f"reverse {badge_color}")
            traits = personality_entry.traits
            tooltip_summary = (
                f"Profile: {badge_label} • Ext {traits.get('extroversion', 0.0):+.2f}"
                f" • Forg {traits.get('forgiveness', 0.0):+.2f}"
                f" • Amb {traits.get('ambition', 0.0):+.2f}"
            )
            card_table.add_row(Tooltip(badge_text, tooltip_summary))
            traits_text = Text(
                "Traits "
                f"ext {traits.get('extroversion', 0.0):+.2f}  "
                f"forg {traits.get('forgiveness', 0.0):+.2f}  "
                f"amb {traits.get('ambition', 0.0):+.2f}",
                style="dim",
            )
            card_table.add_row(traits_text)
            multipliers = personality_entry.multipliers or {}
            behaviour_bias = multipliers.get("behaviour", {})
            if behaviour_bias:
                bias_parts = ", ".join(f"{key.replace('_', ' ')}={value:+.2f}" for key, value in behaviour_bias.items())
                card_table.add_row(Text(f"Bias {bias_parts}", style="dim"))

        needs_history = history.needs.get(agent.agent_id, {}) if history and isinstance(history.needs, Mapping) else {}
        wallet_history = history.wallet.get(agent.agent_id, ()) if history and isinstance(history.wallet, Mapping) else ()
        rivalry_history = history.rivalry.get(agent.agent_id, {}) if history and isinstance(history.rivalry, Mapping) else {}

        needs_table = Table.grid(expand=True)
        needs_table.add_column(ratio=3)
        needs_table.add_column(ratio=1, justify="right")
        for need_name in ("hunger", "hygiene", "energy"):
            value = agent.needs.get(need_name, 0.0)
            series: Sequence[float] = ()
            if isinstance(needs_history, Mapping):
                need_series = needs_history.get(need_name)
                if isinstance(need_series, Sequence):
                    series = need_series
                elif isinstance(need_series, tuple):
                    series = need_series
                else:
                    composite = needs_history.get("composite")
                    if isinstance(composite, Sequence):
                        series = composite
            spark_style = NEED_SPARK_STYLES.get(need_name, "cyan")
            needs_table.add_row(
                _format_need_bar(need_name, value),
                _sparkline_text(series, style=spark_style),
            )

        wallet_line = Text(
            f"Wallet {agent.wallet:.2f} | Wages withheld {agent.wages_withheld:.2f}",
            style="cyan" if agent.wallet > 0 else "dim",
        )

        attendance_text = Text(
            f"Attendance {agent.attendance_ratio:.0%} | Lateness {agent.lateness_counter}",
            style="green" if agent.attendance_ratio >= 0.75 else "yellow",
        )
        alerts_text = _build_agent_alerts_line(agent, snapshot)

        summary_entry = summary_map.get(agent.agent_id) if summary_map else None
        rival_line = Text("Rivalry: none", style="dim")
        if summary_entry and summary_entry.top_rivals:
            top_rival = summary_entry.top_rivals[0]
            rivalry_value = top_rival.rivalry
            if rivalry_value >= 0.7:
                rival_style = "red"
            elif rivalry_value >= 0.4:
                rival_style = "yellow"
            else:
                rival_style = "green"
            rival_line = Text(
                f"Top rival {top_rival.agent} ({rivalry_value:.2f})",
                style=f"bold {rival_style}",
            )

        friend_line = Text("Friendship: none", style="dim")
        if summary_entry and summary_entry.top_friends:
            top_friend = summary_entry.top_friends[0]
            trust_value = top_friend.trust
            friend_line = Text(
                f"Top friend {top_friend.agent} ({trust_value:.2f})",
                style="bold green" if trust_value >= 0.5 else "green",
            )

        social_line = _build_agent_social_line(agent.agent_id, snapshot.social_events)

        card_table.add_row(needs_table)
        card_table.add_row(_row_with_sparkline(wallet_line, _sparkline_text(wallet_history, style="green")))
        card_table.add_row(attendance_text)
        rivalry_series: Sequence[float] = ()
        if isinstance(rivalry_history, Mapping):
            if summary_entry and summary_entry.top_rivals:
                rival_target = summary_entry.top_rivals[0].agent
                rivalry_series = rivalry_history.get(rival_target) or rivalry_history.get("*") or ()
            elif rivalry_history:
                rivalry_series = next(iter(rivalry_history.values()))
        card_table.add_row(_row_with_sparkline(rival_line, _sparkline_text(rivalry_series, style="red")))
        card_table.add_row(friend_line)
        card_table.add_row(social_line)
        card_table.add_row(alerts_text)

        border_style = "blue"
        if personality_enabled and isinstance(personality_entry, PersonalitySnapshotEntry):
            profile_color = PROFILE_STYLE_MAP.get(personality_entry.profile.lower())
            if profile_color:
                border_style = profile_color
        if agent.exit_pending:
            border_style = "red"
        elif agent.on_shift:
            border_style = "cyan"
        if focus_agent and agent.agent_id == focus_agent:
            border_style = "bold magenta"

        title = agent.agent_id
        if subtitle:
            title += f" • {subtitle}"
        cards.append(
            Panel(
                card_table,
                title=title,
                border_style=border_style,
                padding=(0, 1),
            )
        )

    columns = Columns(cards, equal=True, expand=True)
    body: RenderableType = columns
    if filter_notice is not None:
        notice_panel = Panel(filter_notice, border_style="yellow", padding=(0, 1))
        body = Group(columns, notice_panel)

    title = "Agents"
    filter_title = filter_label or (personality_filter or "")
    if filter_active and filter_title:
        title += f" — filter: {filter_title}"
    if card_state is not None and total_pages > 1:
        title += f" (Page {card_state.page + 1}/{total_pages})"
    return Panel(body, title=title, border_style="cyan")


def _format_need_bar(name: str, value: float) -> Text:
    filled = max(0, min(10, round(value * 10)))
    empty = 10 - filled
    bar = "█" * filled + "·" * empty
    if value < 0.3:
        style = "red"
    elif value < 0.6:
        style = "yellow"
    else:
        style = "green"
    text = Text(f"{name.title():<7} {value:>5.0%} ")
    text.append(bar, style=style)
    return text


_SPARKLINE_CHARS = " .:-=+*#%@"


def _sparkline_text(
    series: Sequence[float] | tuple[float, ...],
    *,
    style: str = "cyan",
    width: int = 12,
) -> Text:
    if not series:
        return Text("n/a", style="dim")
    trimmed = tuple(series)[-width:]
    if not trimmed:
        return Text("n/a", style="dim")
    low = min(trimmed)
    high = max(trimmed)
    if math.isclose(high, low):
        normalized = [0.5] * len(trimmed)
    else:
        span = high - low
        normalized = [(value - low) / span for value in trimmed]
    glyphs = "".join(_SPARKLINE_CHARS[min(int(value * (len(_SPARKLINE_CHARS) - 1)), len(_SPARKLINE_CHARS) - 1)] for value in normalized)
    return Text(glyphs, style=style)


def _row_with_sparkline(text: Text, sparkline: Text) -> Table:
    table = Table.grid(expand=True)
    table.add_column(ratio=3)
    table.add_column(ratio=1, justify="right")
    table.add_row(text, sparkline)
    return table


def _build_perturbation_banner(snapshot: TelemetrySnapshot) -> Panel | None:
    perturbations = snapshot.perturbations
    if not perturbations.active and not perturbations.pending:
        health = snapshot.health
        if health and (health.perturbations_pending or health.perturbations_active):
            pending = health.perturbations_pending
            active = health.perturbations_active
            status_line = f"Health reports pending={pending} active={active}"
            text = Text(status_line, style="yellow")
            return Panel(text, title="Perturbation Status", border_style="yellow", padding=(0, 1))
        return None

    lines: list[str] = []
    border = "yellow"

    if perturbations.active:
        border = "red"
        active_parts = []
        for event_id, data in perturbations.active.items():
            spec = str(data.get("spec", "")) if isinstance(data, Mapping) else ""
            remaining = data.get("ticks_remaining") if isinstance(data, Mapping) else None
            remaining_text = f"T-{remaining}" if isinstance(remaining, (int, float)) else "active"
            active_parts.append(f"{event_id}:{spec or 'n/a'} ({remaining_text})")
        lines.append("Active " + ", ".join(active_parts))

    if perturbations.pending:
        pending_parts = []
        for entry in perturbations.pending[:3]:
            if not isinstance(entry, Mapping):
                continue
            spec = str(entry.get("spec", "")) or "n/a"
            starts_in = entry.get("starts_in")
            label = f"{spec} in {starts_in}" if isinstance(starts_in, (int, float)) else spec
            pending_parts.append(label)
        extra = len(perturbations.pending) - len(pending_parts)
        if extra > 0:
            pending_parts.append(f"+{extra} more")
        if pending_parts:
            lines.append("Pending " + ", ".join(pending_parts))

    if perturbations.cooldowns_agents:
        affected = sorted(perturbations.cooldowns_agents.keys())[:3]
        lines.append("Cooldowns " + ", ".join(affected))

    text = Text(" • ".join(lines) if lines else "Perturbation activity detected", style="bold")
    return Panel(text, title="Perturbation Status", border_style=border, padding=(0, 1))


def _build_agent_alerts_line(agent: AgentSummary, snapshot: TelemetrySnapshot) -> Text:
    alerts: list[str] = []
    if agent.exit_pending:
        alerts.append("[bold red]⚠ Exit Pending[/]")
    if agent.late_ticks_today > 0:
        alerts.append(f"[yellow]⏰ Late {agent.late_ticks_today}[/]")
    cooldowns = snapshot.perturbations.cooldowns_agents.get(agent.agent_id, {})
    if cooldowns:
        ordered = sorted(cooldowns.items(), key=lambda item: item[1], reverse=True)
        preview = ", ".join(f"{spec}:{ticks}" for spec, ticks in ordered[:2])
        alerts.append(f"[cyan]🕑 Cooldown {preview}[/]")
    if not alerts:
        return Text("Alerts: none", style="dim")
    return Text.from_markup("Alerts: " + " • ".join(alerts))


def _build_agent_social_line(
    agent_id: str,
    events: Sequence[SocialEventEntry],
) -> Text:
    entry = _latest_social_event(agent_id, events)
    if entry is None:
        return Text("Last social: none", style="dim")
    label = _format_event_type(entry.type)
    summary = _summarise_social_event(entry)
    return Text.from_markup(f"Last social: {label} • {summary}")


def _latest_social_event(
    agent_id: str,
    events: Sequence[SocialEventEntry],
) -> SocialEventEntry | None:
    for entry in reversed(events):
        if _event_involves_agent(entry.payload, agent_id):
            return entry
    return None


def _event_involves_agent(payload: Mapping[str, Any], agent_id: str) -> bool:
    for value in payload.values():
        if _payload_contains_agent(value, agent_id):
            return True
    return False


def _payload_contains_agent(value: Any, agent_id: str) -> bool:
    if isinstance(value, str):
        return value == agent_id
    if isinstance(value, Mapping):
        return any(_payload_contains_agent(item, agent_id) for item in value.values())
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, bytearray, Text)):
        return any(_payload_contains_agent(item, agent_id) for item in value)
    return False


def _build_perturbation_panel(snapshot: TelemetrySnapshot) -> Panel | None:
    perturbations = snapshot.perturbations
    if not perturbations.active and not perturbations.pending:
        body = Text("No active perturbations", style="dim")
        return Panel(body, title="Perturbations", border_style="green")

    renderables: list[RenderableType] = []
    if perturbations.active:
        active_table = Table(title="Active", expand=True)
        active_table.add_column("Event")
        active_table.add_column("Spec")
        active_table.add_column("Details")
        for event_id, data in perturbations.active.items():
            spec = str(data.get("spec", "")) if isinstance(data, Mapping) else ""
            details_parts: list[str] = []
            for key in ("ticks_remaining", "magnitude", "location", "targets"):
                if key in data:
                    details_parts.append(f"{key}={data[key]}")
            details = ", ".join(details_parts) if details_parts else "—"
            active_table.add_row(event_id, spec or "—", details)
        renderables.append(active_table)

    if perturbations.pending:
        pending_table = Table(title="Pending", expand=True)
        pending_table.add_column("Spec")
        pending_table.add_column("Starts In", justify="right")
        pending_table.add_column("Metadata")
        for entry in perturbations.pending:
            spec = str(entry.get("spec", "")) if isinstance(entry, Mapping) else ""
            starts_in = entry.get("starts_in") if isinstance(entry, Mapping) else None
            metadata_parts: list[str] = []
            for key, value in entry.items():
                if key in {"spec", "starts_in"}:
                    continue
                metadata_parts.append(f"{key}={value}")
            metadata = ", ".join(metadata_parts) if metadata_parts else "—"
            pending_table.add_row(spec or "—", str(starts_in or "—"), metadata)
        renderables.append(pending_table)

    if perturbations.cooldowns_spec:
        cooldown_table = Table(title="Cooldowns", expand=True)
        cooldown_table.add_column("Spec")
        cooldown_table.add_column("Ticks", justify="right")
        for spec, ticks in perturbations.cooldowns_spec.items():
            cooldown_table.add_row(spec, str(ticks))
        renderables.append(cooldown_table)

    border_style = "red" if perturbations.active else "yellow"
    return Panel(Group(*renderables), title="Perturbations", border_style=border_style)


def _build_social_status_panel(
    summary: RelationshipSummarySnapshot | None,
) -> Panel | None:
    if summary is None:
        body = Text(
            "Relationships telemetry unavailable (stage OFF or not yet emitted)",
            style="yellow",
        )
        return Panel(body, title="Status", border_style="yellow")
    if not summary.per_agent:
        body = Text(
            "No agent friendships or rivalries recorded yet",
            style="dim",
        )
        return Panel(body, title="Status", border_style="green")
    return None


def _build_social_cards_panel(
    summary: RelationshipSummarySnapshot | None,
) -> Panel | None:
    if summary is None or not summary.per_agent:
        return None

    table = Table(title="Agent Ties", expand=True)
    table.add_column("Agent")
    table.add_column("Friends (trust/fam)")
    table.add_column("Rivals (rivalry)")

    rows_added = 0

    max_agents = 6
    for agent_id, entry in itertools.islice(sorted(summary.per_agent.items()), max_agents):
        friends_text = _format_friends(entry.top_friends)
        rivals_text = _format_rivals(entry.top_rivals)
        table.add_row(agent_id, friends_text, rivals_text)
        rows_added += 1

    if rows_added == 0:
        table.add_row("—", "No tracked friendships", "No active rivals")

    return Panel(table, title="Social Ties", border_style="cyan")


def _build_social_churn_panel(
    summary: RelationshipSummarySnapshot | None,
    relationships: RelationshipChurn | None,
) -> Panel | None:
    churn_data = summary.churn_metrics if summary is not None else {}
    owners_raw = churn_data.get("owners") if isinstance(churn_data, Mapping) else {}
    reasons_raw = churn_data.get("reasons") if isinstance(churn_data, Mapping) else {}
    owners = (
        {str(owner): int(count) for owner, count in owners_raw.items() if isinstance(count, (int, float))}
        if isinstance(owners_raw, Mapping)
        else {}
    )
    reasons = (
        {str(reason): int(count) for reason, count in reasons_raw.items() if isinstance(count, (int, float))}
        if isinstance(reasons_raw, Mapping)
        else {}
    )
    total = int(churn_data.get("total", 0)) if isinstance(churn_data, Mapping) else 0
    window_start = churn_data.get("window_start") if isinstance(churn_data, Mapping) else None
    window_end = churn_data.get("window_end") if isinstance(churn_data, Mapping) else None

    if relationships is not None:
        if window_start is None:
            window_start = relationships.window_start
        if window_end is None:
            window_end = relationships.window_end
        if not owners:
            owners = dict(relationships.per_owner)
        if not reasons:
            reasons = dict(relationships.per_reason)
        if total == 0:
            total = relationships.total_evictions

    window_label = f"{int(window_start)}-{int(window_end)}" if window_start is not None and window_end is not None else "n/a"

    table = Table(title="Churn Summary", expand=True)
    table.add_column("Window")
    table.add_column("Total", justify="right")
    table.add_column("Top Owners")
    table.add_column("Reasons")

    if total == 0 and not owners and not reasons:
        table.add_row(window_label, "0", "(no evictions)", "(no evictions)")
        return Panel(table, title="Churn", border_style="green")

    table.add_row(
        window_label,
        str(total),
        _format_top_entries(owners),
        _format_top_entries(reasons),
    )

    border = "red" if total else "yellow"
    return Panel(table, title="Churn", border_style=border)


def _build_social_events_panel(
    events: tuple[SocialEventEntry, ...],
) -> Panel | None:
    max_events = 8
    displayed_events = list(events)[-max_events:]

    table = Table(title="Recent Social Events", expand=True)
    table.add_column("Type")
    table.add_column("Details")

    if not displayed_events:
        table.add_row("—", "No recent social events")
    else:
        for entry in reversed(displayed_events):
            table.add_row(_format_event_type(entry.type), _summarise_social_event(entry))

    border = "blue" if displayed_events else "green"
    return Panel(table, title="Social Events", border_style=border)


def _format_friends(friends: tuple[FriendSummary, ...]) -> str:
    if not friends:
        return "(none)"
    parts = []
    for friend in friends:
        trust = f"{friend.trust:.2f}" if isinstance(friend.trust, float) else "n/a"
        familiarity = f"{friend.familiarity:.2f}" if isinstance(friend.familiarity, float) else "n/a"
        parts.append(f"{friend.agent} ({trust}/{familiarity})")
    return ", ".join(parts)


def _format_rivals(rivals: tuple[RivalSummary, ...]) -> str:
    if not rivals:
        return "(none)"
    parts = []
    for rival in rivals:
        rivalry = f"{rival.rivalry:.2f}" if isinstance(rival.rivalry, float) else "n/a"
        parts.append(f"{rival.agent} ({rivalry})")
    return ", ".join(parts)


def _format_event_type(event_type: str) -> str:
    mapping = {
        "chat_success": "Chat Success",
        "chat_failure": "Chat Failure",
        "rivalry_avoidance": "Rivalry Avoidance",
    }
    label = mapping.get(event_type, event_type.replace("_", " ").title())
    if event_type == "chat_failure":
        return f"[red]{label}[/]"
    if event_type == "chat_success":
        return f"[green]{label}[/]"
    return label


def _summarise_social_event(entry: SocialEventEntry) -> str:
    payload = entry.payload
    if entry.type in {"chat_success", "chat_failure"}:
        speaker = str(payload.get("speaker", "?"))
        listener = str(payload.get("listener", "?"))
        quality = payload.get("quality")
        quality_text = f" q {float(quality):.2f}" if isinstance(quality, (int, float)) else ""
        return f"{speaker} → {listener}{quality_text}"
    if entry.type == "rivalry_avoidance":
        agent = str(payload.get("agent", "?"))
        target = str(payload.get("object", payload.get("object_id", "?")))
        reason = str(payload.get("reason", ""))
        reason_text = f" ({reason})" if reason else ""
        return f"{agent} avoided {target}{reason_text}"
    if not payload:
        return "(no details)"
    details = ", ".join(f"{key}={value}" for key, value in payload.items())
    return details or "(no details)"


def _extract_churn_total(
    summary: RelationshipSummarySnapshot | None,
    relationships: RelationshipChurn | None,
) -> int:
    churn_data = summary.churn_metrics if summary is not None else {}
    total = int(churn_data.get("total", 0)) if isinstance(churn_data, Mapping) else 0
    if total == 0 and relationships is not None:
        total = relationships.total_evictions
    return total


def _format_top_entries(entries: Mapping[str, int]) -> str:
    if not entries:
        return "(none)"
    sorted_entries = sorted(entries.items(), key=lambda item: item[1], reverse=True)
    return ", ".join(f"{owner}:{count}" for owner, count in sorted_entries[:3])


def _build_narration_panel(narrations: Sequence[NarrationEntry]) -> Panel:
    if narrations:
        table = Table(expand=True)
        table.add_column("Tick", justify="right")
        table.add_column("Category")
        table.add_column("Message")
        table.add_column("!", justify="center")
        for entry in narrations[:5]:
            priority_flag = "[bold red]![/bold red]" if entry.priority else ""
            label, style = NARRATION_CATEGORY_STYLES.get(
                entry.category,
                (entry.category, "white"),
            )
            category_text = f"[{style}]{label}[/]"
            table.add_row(
                str(entry.tick),
                category_text,
                entry.message,
                priority_flag,
            )
        border_style = "yellow" if any(entry.priority for entry in narrations) else "blue"
        return Panel(table, title="Narrations", border_style=border_style)

    body = Text("No recent narrations", style="dim")
    return Panel(body, title="Narrations", border_style="green")


def _build_anneal_panel(snapshot: TelemetrySnapshot) -> Panel:
    anneal = snapshot.anneal
    promotion = snapshot.promotion

    meta_table = Table(title="Cycle", expand=True)
    meta_table.add_column("Cycle", justify="right")
    meta_table.add_column("Stage")
    meta_table.add_column("Dataset")
    meta_table.add_row(
        _safe_format(anneal.cycle if anneal is not None else None),
        anneal.stage if anneal is not None and anneal.stage else "-",
        anneal.dataset if anneal is not None and anneal.dataset else "-",
    )

    promotion_grid = Table.grid(expand=True)
    promotion_grid.add_column(justify="left")
    promotion_grid.add_column(justify="right")
    reason_text = "Awaiting first evaluation."
    promotion_border = _promotion_border_style(promotion)
    history_panel: Panel | None = None
    if promotion is None:
        promotion_grid.add_row("State", "—")
        promotion_grid.add_row("Pass streak", "0")
        promotion_grid.add_row("Required passes", "—")
        promotion_grid.add_row("Candidate ready", "no")
    else:
        state_label = promotion.state or "monitoring"
        promotion_grid.add_row("State", state_label)
        promotion_grid.add_row("Pass streak", str(promotion.pass_streak))
        promotion_grid.add_row("Required passes", str(promotion.required_passes))
        promotion_grid.add_row("Candidate ready", "yes" if promotion.candidate_ready else "no")
        if promotion.candidate_ready_tick is not None:
            promotion_grid.add_row("Ready tick", str(promotion.candidate_ready_tick))
        if promotion.last_result:
            promotion_grid.add_row("Last result", promotion.last_result)
        if promotion.last_evaluated_tick is not None:
            promotion_grid.add_row("Last evaluated", str(promotion.last_evaluated_tick))
        if promotion.candidate_metadata:
            promotion_grid.add_row("Candidate", _format_metadata_summary(promotion.candidate_metadata))
        if promotion.history:
            history_panel = _build_promotion_history_panel(promotion.history, promotion_border)
        reason_text = _derive_promotion_reason(promotion, anneal)
    promotion_grid.add_row("Reason", reason_text)
    promotion_panel = Panel(
        promotion_grid,
        title="Promotion Gate",
        border_style=promotion_border,
    )

    bc_accuracy = anneal.bc_accuracy if anneal is not None else None
    bc_threshold = anneal.bc_threshold if anneal is not None else None
    bc_passed = anneal.bc_passed if anneal is not None else True
    loss_flag = anneal.loss_flag if anneal is not None else False
    queue_flag = anneal.queue_flag if anneal is not None else False
    intensity_flag = anneal.intensity_flag if anneal is not None else False
    loss_baseline = anneal.loss_baseline if anneal is not None else None
    queue_baseline = anneal.queue_baseline if anneal is not None else None
    intensity_baseline = anneal.intensity_baseline if anneal is not None else None

    bc_table = Table(title="BC Gate", expand=True)
    bc_table.add_column("Accuracy", justify="right")
    bc_table.add_column("Threshold", justify="right")
    bc_table.add_column("Passed", justify="center")
    bc_table.add_row(
        _format_optional_float(bc_accuracy),
        _format_optional_float(bc_threshold),
        "✅" if bc_passed else "❌",
    )

    drift_table = Table.grid(expand=True)
    drift_table.add_column(justify="left")
    drift_table.add_row(
        "Loss drift: {} (baseline {})".format(
            "⚠️" if loss_flag else "OK",
            _format_optional_float(loss_baseline),
        )
    )
    drift_table.add_row(
        "Queue drift: {} (baseline {})".format(
            "⚠️" if queue_flag else "OK",
            _format_optional_float(queue_baseline),
        )
    )
    drift_table.add_row(
        "Intensity drift: {} (baseline {})".format(
            "⚠️" if intensity_flag else "OK",
            _format_optional_float(intensity_baseline),
        )
    )
    composite = Panel.fit(
        drift_table,
        title="Drift",
        border_style=("yellow" if (loss_flag or queue_flag or intensity_flag) else "green"),
    )

    container = Table.grid(expand=True)
    container.add_row(meta_table)
    container.add_row(promotion_panel)
    if history_panel is not None:
        container.add_row(history_panel)
    container.add_row(bc_table)
    container.add_row(composite)

    border_style = "red" if not bc_passed else ("yellow" if (loss_flag or queue_flag or intensity_flag) else "green")
    if promotion_border == "red":
        border_style = "red"
    elif promotion_border == "yellow" and border_style == "green":
        border_style = "yellow"
    return Panel(container, title="Anneal Status", border_style=border_style)


def _promotion_border_style(promotion: PromotionSnapshot | None) -> str:
    if promotion is None:
        return "blue"
    if promotion.last_result == "fail":
        return "red"
    if promotion.candidate_ready:
        return "green"
    return "yellow"


def _derive_promotion_reason(
    promotion: PromotionSnapshot,
    status: AnnealStatus | None,
) -> str:
    if promotion.candidate_ready:
        return "Candidate ready for promotion review."
    if promotion.last_result == "fail":
        reasons: list[str] = []
        if status is not None:
            if status.loss_flag:
                reasons.append("loss drift")
            if status.queue_flag:
                reasons.append("queue drift")
            if status.intensity_flag:
                reasons.append("intensity drift")
        if not reasons:
            reasons.append("evaluation failed")
        return "Hold: " + ", ".join(reasons)
    remaining = max(promotion.required_passes - promotion.pass_streak, 0)
    if remaining > 0:
        suffix = "es" if remaining != 1 else ""
        return f"Need {remaining} more consecutive pass{suffix}."
    if promotion.state == "promoted":
        return "Promotion recently executed."
    return "Monitoring next evaluation window."


def _format_metadata_summary(metadata: Mapping[str, Any]) -> str:
    ordered_keys = ("status", "mode", "cycle")
    parts: list[str] = []
    for key in ordered_keys:
        value = metadata.get(key)
        if value not in (None, "", []):
            parts.append(f"{key}={value}")
    extras = [f"{key}={value}" for key, value in metadata.items() if key not in ordered_keys and value not in (None, "", [])]
    parts.extend(extras)
    return ", ".join(parts) if parts else "—"


def _build_promotion_history_panel(history: Iterable[Mapping[str, Any]], border_style: str) -> Panel:
    table = Table(title="Promotion History", expand=True)
    table.add_column("Event")
    table.add_column("Tick", justify="right")
    table.add_column("Details")
    rows = list(history)
    for entry in reversed(rows[-3:]):
        event = str(entry.get("event", "—"))
        tick = entry.get("tick")
        tick_text = str(tick) if tick not in (None, "") else "—"
        details = _format_history_metadata(entry)
        table.add_row(event, tick_text, details)
    return Panel(table, border_style=border_style)


def _format_history_metadata(entry: Mapping[str, Any]) -> str:
    metadata = entry.get("metadata")
    parts: list[str] = []
    if isinstance(metadata, Mapping):
        for key, value in metadata.items():
            if value in (None, "", []):
                continue
            parts.append(f"{key}={value}")
    release = entry.get("release")
    if isinstance(release, Mapping):
        policy_hash = release.get("policy_hash")
        if policy_hash:
            parts.append(f"policy={policy_hash}")
    if not parts:
        return "—"
    return ", ".join(parts)


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
        tops = ", ".join(f"{action.action}:{action.probability:.2f}" for action in entry.top_actions[:3]) or "-"
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

    displayed = 0
    priority = ("queue_conflict_intensity", "employment_lateness", "late_help_events")
    seen: set[str] = set()
    for key in priority:
        if key in seen:
            continue
        series = history.get(key, [])
        if not series:
            continue
        latest = series[-1]
        trend_symbol, colour = _trend_from_series(series)
        label = _humanize_kpi(key)
        table.add_row(label, f"{latest:.2f}", f"[{colour}]{trend_symbol}[/]")
        displayed += 1
        seen.add(key)

    extra_keys = [key for key in sorted(history) if key not in seen]
    for key in extra_keys:
        series = history.get(key, [])
        if not series:
            continue
        latest = series[-1]
        trend_symbol, colour = _trend_from_series(series)
        table.add_row(_humanize_kpi(key), f"{latest:.2f}", f"[{colour}]{trend_symbol}[/]")
        displayed += 1

    if displayed == 0:
        body = Text("No KPI history yet", style="dim")
        return Panel(body, title="KPIs", border_style="green")
    border = "blue" if displayed <= 5 else "magenta"
    return Panel(table, title="KPIs", border_style=border)


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
    if key in mapping:
        return mapping[key]
    return key.replace("_", " ").title()


def run_dashboard(
    loop: SimulationLoop,
    *,
    refresh_interval: float = 1.0,
    max_ticks: int = 0,
    approve: str | None = None,
    defer: str | None = None,
    focus_agent: str | None = None,
    show_coords: bool = False,
    palette_state: PaletteState | None = None,
    on_tick: Callable[[SimulationLoop, ConsoleCommandExecutor, int], None] | None = None,
    agent_page_size: int = 6,
    agent_rotate_interval: int = 12,
    agent_autorotate: bool = True,
    personality_filter: str | None = None,
    show_personality_narration: bool = True,
    telemetry_provider: str | None = None,
    policy_provider: str | None = None,
) -> None:
    """Continuously render dashboard against a SimulationLoop instance."""
    from townlet.world.agents.snapshot import AgentSnapshot

    if not loop.world.agents:
        profile_name, resolved_personality = loop.world.select_personality_profile("observer_demo")
        loop.world.agents["observer_demo"] = AgentSnapshot(
            agent_id="observer_demo",
            position=(0, 0),
            needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
            wallet=1.0,
            personality=resolved_personality,
            personality_profile=profile_name,
        )
        loop.world.assign_jobs_to_agents()

    resolved_telemetry = telemetry_provider or telemetry_provider_name(loop)
    resolved_policy = policy_provider or policy_provider_name(loop)

    router = create_console_router(
        loop.telemetry,
        loop.world,
        promotion=loop.promotion,
        policy=loop.policy,
        policy_provider=resolved_policy,
        telemetry_provider=resolved_telemetry,
        config=loop.config,
    )
    client = TelemetryClient()
    console = Console()
    executor = ConsoleCommandExecutor(router)

    page_size = agent_page_size if agent_page_size > 0 else len(loop.world.agents) or 1
    rotate_enabled = agent_autorotate and agent_rotate_interval != 0
    rotate_interval = agent_rotate_interval if agent_rotate_interval > 0 else 0
    dashboard_state = DashboardState(
        agent_cards=AgentCardState(
            page_size=max(1, page_size),
            rotate=rotate_enabled,
            rotate_interval=max(1, rotate_interval) if rotate_enabled else rotate_interval,
        )
    )

    personality_ui_enabled = False
    try:
        personality_ui_enabled = bool(loop.config.personality_ui_enabled())
    except AttributeError:
        personality_ui_enabled = False

    if approve:
        executor.submit(ConsoleCommand(name="employment_exit", args=("approve", approve), kwargs={}))
    if defer:
        executor.submit(ConsoleCommand(name="employment_exit", args=("defer", defer), kwargs={}))

    tick = 0
    refresh_rate = 1.0 / max(refresh_interval, 1e-3)
    try:
        with Live(console=console, refresh_per_second=refresh_rate, transient=False) as live:
            while max_ticks <= 0 or tick < max_ticks:
                tick += 1
                loop_start = time.monotonic()
                artifacts = loop.step()
                if on_tick is not None:
                    on_tick(loop, executor, loop.tick)
                snapshot = client.from_console(router)
                refreshed = time.strftime("%H:%M:%S")
                panels = list(
                    render_snapshot(
                        snapshot,
                        tick=loop.tick,
                        refreshed=refreshed,
                        palette=palette_state,
                        state=dashboard_state,
                        focus_agent=focus_agent,
                        personality_filter=personality_filter,
                        personality_enabled=personality_ui_enabled,
                        show_personality_narration=show_personality_narration,
                    )
                )
                map_panel = _build_map_panel(
                    snapshot,
                    artifacts.envelope,
                    focus_agent,
                    show_coords=show_coords,
                )
                if map_panel is not None:
                    panels.append(map_panel)
                footer = Text(f"Tick: {loop.tick}", style="dim")
                panels.append(footer)
                live.update(Group(*panels))
                elapsed = time.monotonic() - loop_start
                sleep_for = max(0.0, refresh_interval - elapsed)
                if sleep_for:
                    time.sleep(sleep_for)
    except KeyboardInterrupt:
        console.print("[yellow]Dashboard interrupted by user.[/yellow]")
    finally:
        executor.shutdown()


def _build_map_panel(
    snapshot: TelemetrySnapshot,
    envelope: ObservationEnvelope,
    focus_agent: str | None,
    show_coords: bool = False,
) -> Panel | None:
    agents = snapshot.agents
    if not agents:
        return None
    agent_id = focus_agent if focus_agent and any(a.agent_id == focus_agent for a in agents) else agents[0].agent_id
    dto_lookup = {agent.agent_id: agent for agent in envelope.agents}
    dto_agent = dto_lookup.get(agent_id)
    if dto_agent is None or dto_agent.map is None:
        return None
    map_tensor = np.asarray(dto_agent.map, dtype=np.float32)
    if map_tensor.ndim != 3:
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

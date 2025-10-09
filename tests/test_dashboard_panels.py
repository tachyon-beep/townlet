import threading
from pathlib import Path
from types import SimpleNamespace

from rich.console import Console

from townlet.config import load_config
from townlet.console.handlers import create_console_router
from townlet.core.sim_loop import SimulationLoop
from townlet_ui.commands import CommandQueueFull, ConsoleCommandExecutor
from townlet_ui.dashboard import (
    AgentCardState,
    PaletteState,
    _build_agent_cards_panel,
    _build_palette_overlay,
    _build_perturbation_panel,
    dispatch_palette_selection,
    render_snapshot,
)
from townlet_ui.telemetry import (
    AgentSummary,
    FriendSummary,
    NarrationEntry,
    PersonalitySnapshotEntry,
    PerturbationSnapshot,
    RelationshipSummaryEntry,
    RelationshipSummarySnapshot,
    RivalSummary,
    SocialEventEntry,
    TelemetryClient,
    TelemetryHistory,
)


def _make_loop() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    world = loop.world
    from townlet.world.grid import AgentSnapshot

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.7, "hygiene": 0.6, "energy": 0.5},
        wallet=2.5,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(0, 1),
        needs={"hunger": 0.4, "hygiene": 0.8, "energy": 0.9},
        wallet=1.0,
    )
    world.assign_jobs_to_agents()  
    world.update_relationship("alice", "bob", trust=0.3, familiarity=0.2)
    loop.telemetry.emit_event(
        "loop.tick",
        {
            "tick": world.tick,
            "world": world,
            "observations": {},
            "rewards": {},
            "events": [],
            "policy_snapshot": {},
            "kpi_history": False,
            "reward_breakdown": {},
            "stability_inputs": {},
            "perturbations": {},
            "policy_identity": {},
            "possessed_agents": [],
            "social_events": [],
        },
    )
    world.apply_console([])
    world.consume_console_results()
    return loop


def test_agent_cards_and_perturbation_banner_render() -> None:
    loop = _make_loop()
    router = create_console_router(
        loop.telemetry,
        loop.world,
        policy=loop.policy,
        config=loop.config,
    )
    # Seed active and pending perturbations in telemetry
    loop.telemetry._latest_perturbations = {
        "active": {
            "demo-active": {"spec": "price_spike", "ticks_remaining": 20},
        },
        "pending": [
            {"event_id": "demo-pending", "spec": "utility_outage", "starts_in": 60},
        ],
        "cooldowns": {
            "spec": {"price_spike": 120},
            "agents": {"alice": {"price_spike": 60}},
        },
    }
    loop.telemetry._latest_relationship_summary = {
        "alice": {
            "top_friends": [{"agent": "bob", "trust": 0.6, "familiarity": 0.5, "rivalry": 0.1}],
            "top_rivals": [],
        },
        "churn": {},
    }

    snapshot = TelemetryClient().from_console(router)
    panels = list(render_snapshot(snapshot, tick=loop.tick, refreshed="00:00:00"))
    titles = [panel.title or "" for panel in panels]
    assert any(title.startswith("Agents") for title in titles)
    assert any(title.startswith("Perturbations") for title in titles)
    assert any(title.startswith("Perturbation Status") for title in titles)

    agent_texts: list[str] = []
    console = Console(record=True, width=120)
    for panel in panels:
        if (panel.title or "").startswith("Agents"):
            console = Console(record=True, width=120)
            console.print(panel)
            text_lower = console.export_text().lower()
            agent_texts.append(text_lower)
            assert "wallet" in text_lower and "attendance" in text_lower

        if (panel.title or "").startswith("Perturbations"):
            console = Console(record=True, width=120)
            console.print(panel)
            text = console.export_text()
            assert "demo-active" in text
            assert "demo-pending" in text

    assert any("friend" in text or "rivalry" in text for text in agent_texts)


def test_agent_cards_panel_renders_social_context() -> None:
    snapshot = SimpleNamespace()
    snapshot.agents = [
        AgentSummary(
            agent_id="alice",
            wallet=3.2,
            shift_state="on_shift",
            attendance_ratio=0.85,
            wages_withheld=0.4,
            lateness_counter=1,
            on_shift=True,
            job_id="bakery",
            needs={"hunger": 0.7, "hygiene": 0.5, "energy": 0.4},
            exit_pending=False,
            late_ticks_today=0,
            meals_cooked=2,
            meals_consumed=1,
            basket_cost=12.0,
        ),
        AgentSummary(
            agent_id="bob",
            wallet=1.8,
            shift_state="off_shift",
            attendance_ratio=0.6,
            wages_withheld=0.1,
            lateness_counter=3,
            on_shift=False,
            job_id="grocer",
            needs={"hunger": 0.2, "hygiene": 0.9, "energy": 0.8},
            exit_pending=True,
            late_ticks_today=2,
            meals_cooked=0,
            meals_consumed=1,
            basket_cost=9.5,
        ),
    ]
    snapshot.relationship_summary = RelationshipSummarySnapshot(
        per_agent={
            "alice": RelationshipSummaryEntry(
                top_friends=(FriendSummary(agent="bob", trust=0.75, familiarity=0.6, rivalry=0.1),),
                top_rivals=(RivalSummary(agent="eve", rivalry=0.7),),
            ),
            "bob": RelationshipSummaryEntry(
                top_friends=(),
                top_rivals=(),
            ),
        },
        churn_metrics={},
    )
    snapshot.history = None
    snapshot.social_events = (
        SocialEventEntry(
            type="chat_success",
            payload={"speaker": "alice", "listener": "bob", "quality": 0.8},
        ),
    )
    snapshot.perturbations = PerturbationSnapshot(
        active={},
        pending=(),
        cooldowns_spec={},
        cooldowns_agents={
            "bob": {"utility_outage": 3},
        },
    )

    panel = _build_agent_cards_panel(snapshot, tick=5, focus_agent="bob")
    assert panel is not None

    console = Console(record=True, width=120)
    console.print(panel)
    rendered = console.export_text()
    rendered_lower = rendered.lower()
    assert "alice" in rendered_lower
    assert "top friend bob" in rendered_lower
    assert "top rival eve" in rendered_lower
    assert "hunger" in rendered_lower and "energy" in rendered_lower
    assert "exit pending" in rendered_lower
    assert "alerts:" in rendered_lower
    assert "last social" in rendered_lower
    assert "cooldown" in rendered_lower


def test_agent_card_state_rotates_pages() -> None:
    agents = [
        AgentSummary(
            agent_id=f"agent{i}",
            wallet=1.0 + i,
            shift_state="on_shift" if i % 2 == 0 else "off_shift",
            attendance_ratio=0.8,
            wages_withheld=0.0,
            lateness_counter=0,
            on_shift=i % 2 == 0,
            job_id=None,
            needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
            exit_pending=False,
            late_ticks_today=0,
            meals_cooked=0,
            meals_consumed=0,
            basket_cost=0.0,
        )
        for i in range(4)
    ]
    snapshot = SimpleNamespace(
        agents=agents,
        relationship_summary=None,
        history=None,
        social_events=(),
        perturbations=PerturbationSnapshot(
            active={},
            pending=(),
            cooldowns_spec={},
            cooldowns_agents={},
        ),
    )
    state = AgentCardState(page_size=2, rotate=True, rotate_interval=1)

    panel_first = _build_agent_cards_panel(snapshot, tick=1, state=state)
    assert panel_first is not None
    console_first = Console(record=True, width=80)
    console_first.print(panel_first)
    rendered_first = console_first.export_text()
    assert "agent0" in rendered_first and "agent2" in rendered_first
    assert "agent1" not in rendered_first

    panel_second = _build_agent_cards_panel(snapshot, tick=2, state=state)
    assert panel_second is not None
    console_second = Console(record=True, width=80)
    console_second.print(panel_second)
    rendered_second = console_second.export_text()
    assert "agent1" in rendered_second or "agent3" in rendered_second


def test_perturbation_panel_states() -> None:
    snapshot = SimpleNamespace()
    snapshot.perturbations = PerturbationSnapshot(
        active={
            "active-spike": {
                "spec": "price_spike",
                "ticks_remaining": 15,
                "magnitude": 1.5,
            }
        },
        pending=(
            {
                "event_id": "pending-outage",
                "spec": "utility_outage",
                "starts_in": 30,
            },
        ),
        cooldowns_spec={"price_spike": 120},
        cooldowns_agents={"alice": {"utility_outage": 60}},
    )

    panel = _build_perturbation_panel(snapshot)
    assert panel is not None
    console = Console(record=True, width=120)
    console.print(panel)
    rendered = console.export_text().lower()
    assert "active-spike" in rendered
    assert "pending-outage" in rendered
    assert "price_spike" in rendered

    snapshot_empty = SimpleNamespace()
    snapshot_empty.perturbations = PerturbationSnapshot(
        active={},
        pending=(),
        cooldowns_spec={},
        cooldowns_agents={},
    )
    panel_empty = _build_perturbation_panel(snapshot_empty)
    assert panel_empty is not None
    console = Console(record=True, width=120)
    console.print(panel_empty)
    rendered_empty = console.export_text().lower()
    assert "no active perturbations" in rendered_empty


def test_agent_cards_panel_renders_sparklines_from_history() -> None:
    snapshot = SimpleNamespace()
    snapshot.agents = [
        AgentSummary(
            agent_id="alice",
            wallet=2.0,
            shift_state="on_shift",
            attendance_ratio=0.9,
            wages_withheld=0.2,
            lateness_counter=0,
            on_shift=True,
            job_id="bakery",
            needs={"hunger": 0.3, "hygiene": 0.4, "energy": 0.8},
            exit_pending=False,
            late_ticks_today=0,
            meals_cooked=1,
            meals_consumed=1,
            basket_cost=5.0,
        )
    ]
    snapshot.relationship_summary = RelationshipSummarySnapshot(
        per_agent={
            "alice": RelationshipSummaryEntry(
                top_friends=(),
                top_rivals=(RivalSummary(agent="bob", rivalry=0.5),),
            )
        },
        churn_metrics={},
    )
    snapshot.history = TelemetryHistory(
        needs={
            "alice": {
                "hunger": (0.1, 0.4, 0.6),
                "hygiene": (0.2, 0.3, 0.5),
                "energy": (0.5, 0.7, 0.8),
            }
        },
        wallet={"alice": (1.0, 1.2, 1.5)},
        rivalry={"alice": {"bob": (0.2, 0.3, 0.35)}},
    )
    snapshot.social_events = ()
    snapshot.perturbations = PerturbationSnapshot(
        active={},
        pending=(),
        cooldowns_spec={},
        cooldowns_agents={},
    )

    panel = _build_agent_cards_panel(snapshot, tick=10)
    assert panel is not None
    console = Console(record=True, width=120)
    console.print(panel)
    rendered = console.export_text().lower()
    assert "alice" in rendered
    assert any(ch in rendered for ch in ["=", "+", "*", "#", "%"])
    assert "n/a" not in rendered


def test_palette_overlay_renders_history_and_search() -> None:
    snapshot = SimpleNamespace(
        console_commands={
            "queue_inspect": {
                "mode": "viewer",
                "usage": "queue_inspect <object_id>",
                "description": "Inspect queue entries",
            },
            "set_spawn_delay": {
                "mode": "admin",
                "usage": "set_spawn_delay <ticks>",
                "description": "Adjust respawn delay",
            },
        },
        console_results=(
            {
                "name": "queue_inspect",
                "status": "error",
                "error": {"code": "usage", "message": "queue_inspect <object_id>"},
            },
            {
                "name": "social_events",
                "status": "ok",
                "result": {"events": 3},
            },
        ),
    )
    palette = PaletteState(visible=True, query="queue", mode_filter="viewer", history_limit=2)
    panel = _build_palette_overlay(snapshot, palette)
    assert panel is not None
    console = Console(record=True, width=100)
    console.print(panel)
    rendered = console.export_text().lower()
    assert "queue_inspect" in rendered
    assert "inspect queue entries" in rendered
    assert "social_events" in rendered
    assert "queue_inspect <object_id>" in rendered
    assert "personality:" in rendered


def test_palette_overlay_respects_mode_filter() -> None:
    snapshot = SimpleNamespace(
        console_commands={
            "queue_inspect": {
                "mode": "viewer",
                "usage": "queue_inspect <object_id>",
                "description": "Inspect queue entries",
            },
            "set_spawn_delay": {
                "mode": "admin",
                "usage": "set_spawn_delay <ticks>",
                "description": "Adjust respawn delay",
            },
        },
        console_results=(),
    )
    palette = PaletteState(visible=True, query="", mode_filter="admin")
    panel = _build_palette_overlay(snapshot, palette)
    assert panel is not None
    console = Console(record=True, width=100)
    console.print(panel)
    rendered = console.export_text().lower()
    assert "set_spawn_delay" in rendered
    assert "queue_inspect" not in rendered
    assert "personality:" in rendered


def test_dispatch_palette_selection_dispatches_and_updates_status() -> None:
    snapshot = SimpleNamespace(
        console_commands={
            "queue_inspect": {
                "mode": "viewer",
                "usage": "queue_inspect <object_id>",
                "description": "Inspect queue entries",
            }
        },
        console_results=(),
    )

    class _Router:
        def __init__(self) -> None:
            self.commands: list = []
            self.event = threading.Event()

        def dispatch(self, command) -> None:
            self.commands.append(command)
            self.event.set()

    router = _Router()
    executor = ConsoleCommandExecutor(router, autostart=False, max_pending=4)
    executor.start()

    palette = PaletteState(visible=True, query="queue")
    command = dispatch_palette_selection(snapshot, palette, executor)
    assert command is not None
    assert command.name == "queue_inspect"

    assert router.event.wait(timeout=0.5)
    assert router.commands[0].name == "queue_inspect"
    assert palette.status_message == "Dispatched queue_inspect"
    assert palette.status_style == "green"
    assert palette.pending >= 0

    executor.shutdown()


def test_dispatch_palette_selection_handles_queue_full() -> None:
    snapshot = SimpleNamespace(
        console_commands={
            "queue_inspect": {
                "mode": "viewer",
                "usage": "queue_inspect <object_id>",
                "description": "Inspect queue entries",
            }
        },
        console_results=(),
    )
    router = SimpleNamespace(dispatch=lambda command: None)
    executor = ConsoleCommandExecutor(router, autostart=False, max_pending=1)

    palette = PaletteState(visible=True, query="queue")
    dispatch_palette_selection(snapshot, palette, executor)
    assert palette.status_message == "Dispatched queue_inspect"

    palette.highlight_index = 0
    palette.status_message = None
    try:
        dispatch_palette_selection(snapshot, palette, executor)
        raise AssertionError("Expected CommandQueueFull")
    except CommandQueueFull:
        assert palette.status_message is not None
        assert "Queue saturated" in palette.status_message
        assert palette.status_style == "yellow"
        assert palette.pending >= 1

    executor.shutdown()


def test_dispatch_palette_selection_applies_personality_filter() -> None:
    snapshot = SimpleNamespace(
        console_commands={},
        console_results=(),
        personalities={
            "alice": PersonalitySnapshotEntry(
                profile="socialite",
                traits={"extroversion": 0.8, "forgiveness": 0.1, "ambition": 0.2},
                multipliers=None,
            )
        },
    )
    router = SimpleNamespace(dispatch=lambda command: None)
    executor = ConsoleCommandExecutor(router, autostart=False)
    palette = PaletteState(visible=True, query="profile:socialite")

    result = dispatch_palette_selection(
        snapshot,
        palette,
        executor,
        personality_enabled=True,
    )

    assert result is None
    assert palette.personality_filter == "profile:socialite"
    assert palette.status_message is not None
    assert "profile:socialite" in palette.status_message

    executor.shutdown()


def test_agent_cards_panel_filters_by_profile() -> None:
    summary = SimpleNamespace(per_agent={}, churn_metrics={})
    history = SimpleNamespace(needs={}, wallet={}, rivalry={})
    agents = [
        AgentSummary(
            agent_id="alice",
            wallet=5.0,
            shift_state="on_shift",
            attendance_ratio=0.9,
            wages_withheld=0.0,
            lateness_counter=0,
            on_shift=True,
            job_id="clerk",
            needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
            exit_pending=False,
            late_ticks_today=0,
            meals_cooked=0,
            meals_consumed=0,
            basket_cost=0.0,
        ),
        AgentSummary(
            agent_id="bob",
            wallet=3.0,
            shift_state="off_shift",
            attendance_ratio=0.8,
            wages_withheld=0.0,
            lateness_counter=0,
            on_shift=False,
            job_id="cook",
            needs={"hunger": 0.6, "hygiene": 0.4, "energy": 0.6},
            exit_pending=False,
            late_ticks_today=0,
            meals_cooked=0,
            meals_consumed=0,
            basket_cost=0.0,
        ),
    ]
    snapshot = SimpleNamespace(
        agents=agents,
        relationship_summary=summary,
        history=history,
        personalities={
            "alice": PersonalitySnapshotEntry(
                profile="socialite",
                traits={"extroversion": 0.8, "forgiveness": 0.2, "ambition": 0.3},
                multipliers=None,
            ),
            "bob": PersonalitySnapshotEntry(
                profile="stoic",
                traits={"extroversion": -0.2, "forgiveness": 0.5, "ambition": 0.1},
                multipliers=None,
            ),
        },
        social_events=(),
        perturbations=SimpleNamespace(cooldowns_agents={}),
    )

    panel = _build_agent_cards_panel(
        snapshot,
        tick=10,
        personality_filter="profile:socialite",
        personality_enabled=True,
    )
    assert panel is not None
    console = Console(record=True, width=120)
    console.print(panel)
    rendered = console.export_text()
    assert "alice" in rendered
    assert "bob" not in rendered
    assert "traits ext +0.80" in rendered.lower()


def test_agent_cards_panel_filter_notice_when_disabled() -> None:
    summary = SimpleNamespace(per_agent={}, churn_metrics={})
    history = SimpleNamespace(needs={}, wallet={}, rivalry={})
    agents = [
        AgentSummary(
            agent_id="alice",
            wallet=5.0,
            shift_state="on_shift",
            attendance_ratio=0.9,
            wages_withheld=0.0,
            lateness_counter=0,
            on_shift=True,
            job_id="clerk",
            needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
            exit_pending=False,
            late_ticks_today=0,
            meals_cooked=0,
            meals_consumed=0,
            basket_cost=0.0,
        ),
    ]
    snapshot = SimpleNamespace(
        agents=agents,
        relationship_summary=summary,
        history=history,
        personalities={},
        social_events=(),
        perturbations=SimpleNamespace(cooldowns_agents={}),
    )

    panel = _build_agent_cards_panel(
        snapshot,
        tick=5,
        personality_filter="profile:socialite",
        personality_enabled=False,
    )
    assert panel is not None
    console = Console(record=True, width=120)
    console.print(panel)
    rendered = console.export_text().lower()
    assert "personality filters require" in rendered


def test_agent_cards_panel_filters_by_trait_threshold() -> None:
    summary = SimpleNamespace(per_agent={}, churn_metrics={})
    history = SimpleNamespace(needs={}, wallet={}, rivalry={})
    agents = [
        AgentSummary(
            agent_id="alice",
            wallet=5.0,
            shift_state="on_shift",
            attendance_ratio=0.9,
            wages_withheld=0.0,
            lateness_counter=0,
            on_shift=True,
            job_id="clerk",
            needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
            exit_pending=False,
            late_ticks_today=0,
            meals_cooked=0,
            meals_consumed=0,
            basket_cost=0.0,
        ),
        AgentSummary(
            agent_id="bob",
            wallet=3.0,
            shift_state="off_shift",
            attendance_ratio=0.8,
            wages_withheld=0.0,
            lateness_counter=0,
            on_shift=False,
            job_id="cook",
            needs={"hunger": 0.6, "hygiene": 0.4, "energy": 0.6},
            exit_pending=False,
            late_ticks_today=0,
            meals_cooked=0,
            meals_consumed=0,
            basket_cost=0.0,
        ),
    ]
    snapshot = SimpleNamespace(
        agents=agents,
        relationship_summary=summary,
        history=history,
        personalities={
            "alice": PersonalitySnapshotEntry(
                profile="balanced",
                traits={"extroversion": 0.6, "forgiveness": 0.1, "ambition": 0.3},
                multipliers=None,
            ),
            "bob": PersonalitySnapshotEntry(
                profile="balanced",
                traits={"extroversion": 0.1, "forgiveness": 0.4, "ambition": 0.2},
                multipliers=None,
            ),
        },
        social_events=(),
        perturbations=SimpleNamespace(cooldowns_agents={}),
    )

    panel = _build_agent_cards_panel(
        snapshot,
        tick=7,
        personality_filter="trait:extroversion>=0.5",
        personality_enabled=True,
    )
    assert panel is not None
    console = Console(record=True, width=120)
    console.print(panel)
    rendered = console.export_text().lower()
    assert "alice" in rendered
    assert "bob" not in rendered


def test_render_snapshot_filters_personality_narrations_when_muted() -> None:
    narrations = [
        NarrationEntry(
            tick=5,
            category="personality_event",
            message="avery remained calm",
            priority=False,
            data={"agent": "avery"},
        ),
        NarrationEntry(
            tick=6,
            category="queue_conflict",
            message="queue conflict occurred",
            priority=False,
            data={},
        ),
    ]
    snapshot = SimpleNamespace(
        schema_version="0.9.7",
        schema_warning=None,
        narrations=narrations,
        transport=SimpleNamespace(
            connected=True,
            dropped_messages=0,
            last_success_tick=0,
            last_failure_tick=None,
            queue_length=0,
            last_flush_duration_ms=None,
            last_error=None,
        ),
        health=None,
        utilities={},
        employment=SimpleNamespace(
            pending=[],
            pending_count=0,
            exits_today=0,
            daily_exit_cap=0,
            queue_limit=0,
            review_window=0,
        ),
        conflict=SimpleNamespace(
            queue_cooldown_events=0,
            queue_ghost_step_events=0,
            queue_rotation_events=0,
            rivalry_events=[],
            queue_history=[],
            rivalry_agents=0,
        ),
        economy_settings={},
        perturbations=PerturbationSnapshot(
            active={},
            pending=(),
            cooldowns_agents={},
            cooldowns_spec={},
        ),
        agents=[],
        relationship_summary=None,
        history=None,
        social_events=(),
        anneal=None,
        promotion=None,
        kpis={},
        policy_inspector=[],
        relationship_overlay={},
        relationships=None,
        price_spikes=(),
        stability=SimpleNamespace(alerts=[]),
        relationship_updates=[],
    )

    panels = list(
        render_snapshot(
            snapshot,
            tick=10,
            refreshed="00:00:00",
            show_personality_narration=False,
        )
    )
    text_console = Console(record=True, width=120)
    narration_panel = next(panel for panel in panels if (panel.title or "") == "Narrations")
    text_console.print(narration_panel)
    rendered = text_console.export_text()
    assert "queue conflict occurred" in rendered
    assert "avery remained calm" not in rendered

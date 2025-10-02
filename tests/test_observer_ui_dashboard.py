from pathlib import Path

from dataclasses import replace

import pytest

from townlet.config import load_config
from townlet.console.handlers import create_console_router
from townlet.core.sim_loop import SimulationLoop
from townlet.policy.models import torch_available
from townlet_ui.dashboard import _build_map_panel, render_snapshot, run_dashboard, _promotion_border_style, _derive_promotion_reason
from townlet_ui.telemetry import TelemetryClient, AnnealStatus, PromotionSnapshot


def make_loop() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    world = loop.world
    if not world.agents:
        from townlet.world.grid import AgentSnapshot

        world.agents["alice"] = AgentSnapshot(
            agent_id="alice",
            position=(0, 0),
            needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
            wallet=1.0,
        )
        world.agents["bob"] = AgentSnapshot(
            agent_id="bob",
            position=(1, 0),
            needs={"hunger": 0.6, "hygiene": 0.4, "energy": 0.5},
            wallet=1.2,
        )
        world._assign_jobs_to_agents()  # type: ignore[attr-defined]
        world.update_relationship("alice", "bob", trust=0.2, familiarity=0.1)
    return loop


def test_render_snapshot_produces_panels() -> None:
    loop = make_loop()
    router = create_console_router(loop.telemetry, loop.world, policy=loop.policy, config=loop.config)
    for _ in range(3):
        loop.step()
    loop.world.update_relationship(
        "alice", "bob", trust=0.1, familiarity=0.05, rivalry=0.02
    )
    loop.step()
    snapshot = TelemetryClient().from_console(router)

    panels = list(render_snapshot(snapshot, tick=loop.tick, refreshed="00:00:00"))
    assert panels
    panel_titles = [getattr(p, "title", "") for p in panels]
    assert any((title or "").startswith("Employment") for title in panel_titles)
    assert any((title or "").startswith("Conflict") for title in panel_titles)
    assert any((title or "").startswith("Narrations") for title in panel_titles)
    assert any((title or "").startswith("Relationships") for title in panel_titles)
    assert any(
        (title or "").startswith("Relationship Updates") for title in panel_titles
    )
    assert any((title or "").startswith("Policy Inspector") for title in panel_titles)
    assert any(
        (title or "").startswith("Relationship Overlay") for title in panel_titles
    )
    assert any("Legend" in (title or "") for title in panel_titles)


def test_run_dashboard_advances_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    loop = make_loop()
    calls = {"sleep": 0}

    def fake_sleep(_seconds: float) -> None:
        calls["sleep"] += 1

    monkeypatch.setattr("townlet_ui.dashboard.time.sleep", fake_sleep)
    run_dashboard(loop, refresh_interval=0, max_ticks=2)
    assert calls["sleep"] == 2


def test_build_map_panel_produces_table() -> None:
    loop = make_loop()
    router = create_console_router(loop.telemetry, loop.world, policy=loop.policy, config=loop.config)
    for _ in range(2):
        loop.step()
    snapshot = TelemetryClient().from_console(router)
    obs_batch = loop.observations.build_batch(loop.world, terminated={})
    panel = _build_map_panel(snapshot, obs_batch, focus_agent=None)
    assert panel is not None
    assert "Local Map" in (panel.title or "")


def test_narration_panel_shows_styled_categories() -> None:
    loop = make_loop()
    router = create_console_router(loop.telemetry, loop.world, policy=loop.policy, config=loop.config)
    world = loop.world
    telemetry = loop.telemetry

    from townlet.world.grid import AgentSnapshot

    shower = world.objects["shower_1"]
    shower.stock["power_on"] = 0
    world.store_stock["shower_1"] = shower.stock

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(1, 1),
        needs={"hygiene": 0.1, "energy": 0.5},
        wallet=5.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(0, 0),
        needs={"hunger": 0.5, "energy": 0.2},
        wallet=1.0,
    )

    telemetry.publish_tick(
        tick=loop.tick,
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

    world.apply_console([])
    world.consume_console_results()

    events: list[dict[str, object]] = []

    # Outage attempt
    granted = world.queue_manager.request_access("shower_1", "alice", world.tick)
    assert granted is True
    world._sync_reservation("shower_1")
    assert world._start_affordance("alice", "shower_1", "use_shower") is False
    events.extend(world.drain_events())

    # Successful sleep
    granted = world.queue_manager.request_access("bed_1", "bob", world.tick)
    assert granted is True
    world._sync_reservation("bed_1")
    assert world._start_affordance("bob", "bed_1", "rest_sleep") is True
    running = world._running_affordances["bed_1"]
    running.duration_remaining = 0
    world.resolve_affordances(world.tick)
    events.extend(world.drain_events())

    telemetry.publish_tick(
        tick=loop.tick + 1,
        world=world,
        observations={},
        rewards={},
        events=events,
        policy_snapshot={},
        kpi_history=False,
        reward_breakdown={},
        stability_inputs={},
        perturbations={},
        policy_identity={},
        possessed_agents=[],
    )

    snapshot = TelemetryClient().from_console(router)
    assert snapshot.narrations, "Expected narrations to be populated"
    panels = list(render_snapshot(snapshot, tick=loop.tick + 1, refreshed="00:00:00"))
    narration_panel = next(panel for panel in panels if (panel.title or "").startswith("Narrations"))
    from rich.console import Console

    console = Console(record=True, width=120)
    console.print(narration_panel)
    rendered = console.export_text()
    assert "Utility Outage" in rendered


def test_policy_inspector_snapshot_contains_entries() -> None:
    loop = make_loop()
    router = create_console_router(loop.telemetry, loop.world, policy=loop.policy, config=loop.config)
    for _ in range(2):
        loop.step()
    snapshot = TelemetryClient().from_console(router)
    entries = snapshot.policy_inspector
    assert entries
    entry = entries[0]
    assert entry.top_actions
    assert entry.selected_action is not None


def test_promotion_reason_logic() -> None:
    promotion = PromotionSnapshot(
        state=None,
        pass_streak=0,
        required_passes=2,
        candidate_ready=False,
        candidate_ready_tick=None,
        last_result=None,
        last_evaluated_tick=None,
        candidate_metadata=None,
        current_release=None,
        history=(),
    )
    reason = _derive_promotion_reason(promotion, None)
    assert reason == "Need 2 more consecutive passes."

    anneal = AnnealStatus(
        stage="ppo",
        cycle=1.0,
        dataset="idle",
        bc_accuracy=0.95,
        bc_threshold=0.9,
        bc_passed=True,
        loss_flag=True,
        queue_flag=False,
        intensity_flag=True,
        loss_baseline=0.1,
        queue_baseline=5.0,
        intensity_baseline=3.0,
    )
    fail_reason = _derive_promotion_reason(
        PromotionSnapshot(
            state="monitoring",
            pass_streak=0,
            required_passes=2,
            candidate_ready=False,
            candidate_ready_tick=None,
            last_result="fail",
            last_evaluated_tick=5,
            candidate_metadata=None,
            current_release=None,
            history=(),
        ),
        anneal,
    )
    assert "loss drift" in fail_reason and "intensity drift" in fail_reason

    ready_reason = _derive_promotion_reason(
        PromotionSnapshot(
            state="ready",
            pass_streak=2,
            required_passes=2,
            candidate_ready=True,
            candidate_ready_tick=10,
            last_result="pass",
            last_evaluated_tick=10,
            candidate_metadata=None,
            current_release=None,
            history=(),
        ),
        anneal,
    )
    assert ready_reason == "Candidate ready for promotion review."


def test_promotion_border_styles() -> None:
    assert _promotion_border_style(None) == "blue"
    promo = PromotionSnapshot(
        state="monitoring",
        pass_streak=1,
        required_passes=3,
        candidate_ready=False,
        candidate_ready_tick=None,
        last_result="pass",
        last_evaluated_tick=1,
        candidate_metadata=None,
        current_release=None,
        history=(),
    )
    assert _promotion_border_style(promo) == "yellow"
    promo_fail = replace(promo, last_result="fail")
    assert _promotion_border_style(promo_fail) == "red"
    promo_ready = replace(promo, candidate_ready=True)
    assert _promotion_border_style(promo_ready) == "green"

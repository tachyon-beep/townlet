"""Run a scripted Townlet demo with dashboard timeline orchestration."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.demo.runner import (
    available_storylines,
    build_storyline,
    default_timeline,
    load_timeline,
    run_demo_dashboard,
    seed_demo_state,
)
from townlet.demo.timeline import DemoTimeline
from townlet_ui.dashboard import PaletteState


SCENARIO_CONFIG_MAP: dict[str, Path] = {
    "demo_story_arc": Path("configs/scenarios/demo_story_arc.yaml"),
    "legacy": Path("configs/examples/poc_hybrid.yaml"),
}
SCENARIO_TIMELINE_DIR = Path("configs/scenarios/timelines")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch a scripted Townlet demo run")
    parser.add_argument(
        "config",
        nargs="?",
        type=Path,
        help="Path to simulation configuration YAML",
    )
    parser.add_argument(
        "--config",
        dest="config_override",
        type=Path,
        help="Path to simulation configuration YAML (overrides positional value)",
    )
    parser.add_argument(
        "--scenario",
        choices=available_storylines(),
        default="demo_story_arc",
        help="Storyline identifier used for default configs and timelines",
    )
    parser.add_argument(
        "--ticks",
        type=int,
        default=240,
        help="Number of ticks to run before exiting (0 runs indefinitely)",
    )
    parser.add_argument(
        "--refresh",
        type=float,
        default=1.0,
        help="Dashboard refresh interval in seconds",
    )
    parser.add_argument(
        "--perturbation-plan",
        type=Path,
        help="Optional perturbation plan applied before the timeline",
    )
    parser.add_argument(
        "--relationships",
        action="store_true",
        help="Force enable relationship stage in the config before running",
    )
    parser.add_argument(
        "--history-window",
        type=int,
        default=30,
        help="Telemetry history window for dashboard sparklines (0 disables)",
    )
    parser.add_argument(
        "--timeline",
        type=Path,
        help="Optional YAML/JSON timeline overriding the default demo sequence",
    )
    parser.add_argument(
        "--narration-level",
        default="summary",
        help="Narration verbosity (e.g., off, summary, verbose)",
    )
    parser.add_argument(
        "--no-palette",
        action="store_true",
        help="Hide the command palette overlay during the demo",
    )
    parser.add_argument(
        "--personality-filter",
        help="Optional personality profile filter for agent cards (e.g., socialite)",
    )
    parser.add_argument(
        "--mute-personality-narration",
        action="store_true",
        help="Hide personality-driven narration entries in the CLI dashboard",
    )
    args = parser.parse_args()
    config_path = args.config_override or args.config
    if config_path is None:
        default_config = SCENARIO_CONFIG_MAP.get(args.scenario)
        if default_config is not None and default_config.exists():
            config_path = default_config
    if config_path is None:
        parser.error("A configuration path is required (provide --config or positional config)")
    args.config = config_path
    return args


def load_demo_timeline(path: Optional[Path], scenario: Optional[str]) -> DemoTimeline:
    if path is None:
        if scenario:
            timeline_path = SCENARIO_TIMELINE_DIR / f"{scenario}.yaml"
            if timeline_path.exists():
                return load_timeline(timeline_path)
            return build_storyline(scenario)
        return default_timeline()
    return load_timeline(path)


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.relationships:
        config.features.stages.relationships = max(
            config.features.stages.relationships,
            "A",
        )
    loop = SimulationLoop(config)

    seed_demo_state(
        loop.world,
        history_window=args.history_window,
        telemetry=loop.telemetry,
        narration_level=args.narration_level,
    )

    timeline = load_demo_timeline(args.timeline, args.scenario)
    if args.perturbation_plan:
        loop.perturbations.load_plan(args.perturbation_plan)
    palette_state = None if args.no_palette else PaletteState(visible=True, query="")
    if palette_state is not None:
        palette_state.clamp_history(args.history_window)

    run_demo_dashboard(
        loop,
        refresh_interval=args.refresh,
        max_ticks=args.ticks,
        timeline=timeline,
        palette_state=palette_state,
        personality_filter=args.personality_filter,
        show_personality_narration=not args.mute_personality_narration,
    )


if __name__ == "__main__":
    main()

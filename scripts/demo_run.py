"""Run a scripted Townlet demo with dashboard timeline orchestration."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.demo.runner import (
    default_timeline,
    load_timeline,
    run_demo_dashboard,
    seed_demo_state,
)
from townlet.demo.timeline import DemoTimeline
from townlet_ui.dashboard import PaletteState


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch a scripted Townlet demo run")
    parser.add_argument("config", type=Path, help="Path to simulation configuration YAML")
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
        "--no-palette",
        action="store_true",
        help="Hide the command palette overlay during the demo",
    )
    return parser.parse_args()


def load_demo_timeline(path: Optional[Path]) -> DemoTimeline:
    if path is None:
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

    seed_demo_state(loop.world, history_window=args.history_window)

    timeline = load_demo_timeline(args.timeline)
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
    )


if __name__ == "__main__":
    main()

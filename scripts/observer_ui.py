#!/usr/bin/env python
"""Launch the Townlet observer dashboard against a local simulation."""
from __future__ import annotations

import argparse
from pathlib import Path

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet_ui.dashboard import run_dashboard


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Townlet observer dashboard")
    parser.add_argument("config", type=Path, help="Simulation config file")
    parser.add_argument("--ticks", type=int, default=0, help="Maximum ticks to run (0 = infinite)")
    parser.add_argument(
        "--refresh",
        type=float,
        default=1.0,
        help="Refresh interval in seconds between dashboard updates",
    )
    parser.add_argument(
        "--focus-agent",
        type=str,
        help="Agent ID to use for map focus (default first agent)",
    )
    parser.add_argument(
        "--show-coordinates",
        action="store_true",
        help="Display row/column indices around the map",
    )
    parser.add_argument(
        "--approve",
        type=str,
        help="Approve pending employment exit for the specified agent ID at start",
    )
    parser.add_argument(
        "--defer",
        type=str,
        help="Defer pending employment exit for the specified agent ID at start",
    )
    parser.add_argument(
        "--agent-page-size",
        type=int,
        default=6,
        help="Number of agent cards to display per page (default 6)",
    )
    parser.add_argument(
        "--agent-rotate-interval",
        type=int,
        default=12,
        help="Ticks between automatic agent card rotations (0 to disable)",
    )
    parser.add_argument(
        "--disable-agent-autorotate",
        action="store_true",
        help="Disable automatic pagination of agent cards",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    loop = SimulationLoop(config)
    run_dashboard(
        loop,
        refresh_interval=args.refresh,
        max_ticks=args.ticks,
        approve=args.approve,
        defer=args.defer,
        focus_agent=args.focus_agent,
        show_coords=args.show_coordinates,
        agent_page_size=args.agent_page_size,
        agent_rotate_interval=args.agent_rotate_interval,
        agent_autorotate=not args.disable_agent_autorotate,
    )


if __name__ == "__main__":
    main()

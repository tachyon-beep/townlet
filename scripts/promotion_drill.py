#!/usr/bin/env python
"""Run a scripted promotion/rollback drill and capture artefacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from townlet.config import load_config
from townlet.console.handlers import ConsoleCommand, create_console_router
from townlet.core.sim_loop import SimulationLoop
from townlet.core.utils import policy_provider_name, telemetry_provider_name


def _ensure_candidate_ready(loop: SimulationLoop) -> None:
    loop.promotion.update_from_metrics(
        {
            "promotion": {
                "pass_streak": loop.config.stability.promotion.required_passes,
                "required_passes": loop.config.stability.promotion.required_passes,
                "candidate_ready": True,
                "last_result": "pass",
                "last_evaluated_tick": loop.tick,
            }
        },
        tick=loop.tick,
    )


def run_drill(config_path: Path, output_dir: Path, checkpoint: Path) -> dict[str, Any]:
    config = load_config(config_path)
    loop = SimulationLoop(config)
    router = create_console_router(
        loop.telemetry,
        loop.world,
        promotion=loop.promotion,
        scheduler=loop.perturbations,
        policy=loop.policy,
        policy_provider=policy_provider_name(loop),
        telemetry_provider=telemetry_provider_name(loop),
        mode="admin",
        config=config,
    )

    _ensure_candidate_ready(loop)

    initial = router.dispatch(ConsoleCommand(name="promotion_status", args=(), kwargs={}))

    promote = router.dispatch(
        ConsoleCommand(
            name="promote_policy",
            args=(str(checkpoint),),
            kwargs={"policy_hash": "drill-candidate", "cmd_id": "drill-promote"},
        )
    )

    rollback = router.dispatch(
        ConsoleCommand(
            name="rollback_policy",
            args=(),
            kwargs={"reason": "drill-rollback", "cmd_id": "drill-rollback"},
        )
    )

    history = loop.promotion.snapshot()["history"]

    summary = {
        "config": str(config_path),
        "checkpoint": str(checkpoint),
        "initial": initial,
        "promote": promote,
        "rollback": rollback,
        "history": history,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "promotion_drill_summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run promotion/rollback drill")
    parser.add_argument("--config", type=Path, required=True, help="Path to simulation config")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/m7/drill"),
        help="Directory to write drill artefacts",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=Path("promotion_drill_checkpoint.pt"),
        help="Logical checkpoint identifier used during promotion command",
    )
    args = parser.parse_args(argv)

    summary = run_drill(
        args.config.expanduser(),
        args.output.expanduser(),
        args.checkpoint.expanduser(),
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

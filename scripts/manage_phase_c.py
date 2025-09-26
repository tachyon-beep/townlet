"""Helper script to toggle Phase C social reward stages in configs."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

import yaml

VALID_STAGES = {"OFF", "C1", "C2", "C3"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage Phase C social reward flags")
    subparsers = parser.add_subparsers(dest="command", required=True)

    set_stage = subparsers.add_parser("set-stage", help="Update features.stages.social_rewards")
    set_stage.add_argument("config", type=Path, help="Path to simulation YAML config")
    set_stage.add_argument("--stage", required=True, choices=sorted(VALID_STAGES))
    set_stage.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write updated config to this path (default: stdout)",
    )
    set_stage.add_argument(
        "--in-place",
        action="store_true",
        help="Write changes back to the input config path",
    )

    schedule = subparsers.add_parser(
        "schedule",
        help="Manage training.social_reward_* overrides and schedule entries",
    )
    schedule.add_argument("config", type=Path, help="Path to simulation YAML config")
    schedule.add_argument(
        "--override",
        choices=sorted(VALID_STAGES),
        default=None,
        help="Set training.social_reward_stage_override to this stage",
    )
    schedule.add_argument(
        "--schedule",
        metavar="ENTRY",
        action="append",
        default=None,
        help="Append schedule entry in the form cycle:stage (e.g. 0:OFF).",
    )
    schedule.add_argument(
        "--clear",
        action="store_true",
        help="Remove existing training.social_reward_schedule entries before applying updates",
    )
    schedule.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write updated config to this path (default: stdout)",
    )
    schedule.add_argument(
        "--in-place",
        action="store_true",
        help="Write changes back to the input config path",
    )

    return parser.parse_args()


def load_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"Config at {path} must be a mapping")
    return data


def ensure_nested(mapping: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    current = mapping
    for key in keys:
        value = current.get(key)
        if not isinstance(value, dict):
            value = {}
            current[key] = value
        current = value
    return current


def write_config(data: Dict[str, Any], *, output: Path | None, in_place: bool, source: Path) -> None:
    target: Path | None
    if in_place:
        target = source
    else:
        target = output

    dumped = yaml.safe_dump(data, sort_keys=False)
    if target is None:
        print(dumped)
    else:
        target.write_text(dumped)


def handle_set_stage(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    stages = ensure_nested(config, ["features", "stages"])
    stages["social_rewards"] = args.stage
    write_config(config, output=args.output, in_place=args.in_place, source=args.config)


def parse_schedule_entries(entries: List[str]) -> List[Dict[str, Any]]:
    parsed: List[Dict[str, Any]] = []
    for entry in entries:
        if ":" not in entry:
            raise ValueError(f"Schedule entry '{entry}' must be in cycle:stage form")
        cycle_text, stage = entry.split(":", 1)
        stage = stage.strip().upper()
        if stage not in VALID_STAGES:
            raise ValueError(f"Invalid social reward stage '{stage}'")
        try:
            cycle = int(cycle_text.strip())
        except ValueError as exc:  # pragma: no cover - validation guard
            raise ValueError(f"Cycle must be an integer: '{cycle_text}'") from exc
        if cycle < 0:
            raise ValueError("Cycle must be non-negative")
        parsed.append({"cycle": cycle, "stage": stage})
    return parsed


def handle_schedule(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    training = ensure_nested(config, ["training"])
    if args.override is not None:
        training["social_reward_stage_override"] = args.override
    schedule_entries: List[Dict[str, Any]]
    schedule_entries = []
    if not args.clear:
        existing = training.get("social_reward_schedule", [])
        if isinstance(existing, list):
            for item in existing:
                if isinstance(item, dict) and {"cycle", "stage"} <= set(item):
                    schedule_entries.append({"cycle": int(item["cycle"]), "stage": str(item["stage"]).upper()})
    if args.schedule:
        schedule_entries.extend(parse_schedule_entries(args.schedule))
    if schedule_entries:
        schedule_entries = sorted(schedule_entries, key=lambda item: item["cycle"])
        training["social_reward_schedule"] = schedule_entries
    elif args.clear:
        training.pop("social_reward_schedule", None)
    write_config(config, output=args.output, in_place=args.in_place, source=args.config)


def main() -> None:
    args = parse_args()
    if args.command == "set-stage":
        handle_set_stage(args)
    elif args.command == "schedule":
        handle_schedule(args)
    else:  # pragma: no cover - argparse enforces choices
        raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()

#!/usr/bin/env python
"""Evaluate promotion readiness from anneal results payloads."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_INPUT_PATH = Path("artifacts/m7/anneal_results.json")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate promotion readiness using anneal results JSON.",
    )
    parser.add_argument(
        "--input",
        dest="input_path",
        type=Path,
        default=None,
        help=(
            "Path to JSON payload emitted by run_training.py --mode anneal."
            " Defaults to stdin if omitted."
        ),
    )
    parser.add_argument(
        "--summary",
        dest="summary_path",
        type=Path,
        default=None,
        help="Alias for --input (legacy compatibility).",
    )
    parser.add_argument(
        "--format",
        choices=["human", "json"],
        default="json",
        help="Output format (human readable or JSON).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Always exit 0 (useful for exploratory checks).",
    )
    return parser.parse_args(argv)


def _load_payload(path: Path | None) -> Dict[str, Any]:
    if path is None:
        data = sys.stdin.read()
        if not data.strip():
            raise ValueError("No input provided on stdin")
        return json.loads(data)
    data = path.expanduser().read_text()
    return json.loads(data)


def _derive_status(results: List[Dict[str, Any]]) -> str:
    status = "PASS"
    for stage in results:
        mode = stage.get("mode")
        if mode == "bc" and not stage.get("passed", True):
            return "FAIL"
        if mode == "ppo" and (
            bool(stage.get("anneal_loss_flag"))
            or bool(stage.get("anneal_queue_flag"))
            or bool(stage.get("anneal_intensity_flag"))
        ):
            status = "HOLD"
    return status


def _collect_reasons(results: List[Dict[str, Any]]) -> List[str]:
    reasons: List[str] = []
    for stage in results:
        mode = stage.get("mode")
        if mode == "bc" and not stage.get("passed", True):
            reasons.append(f"bc_stage_failed_cycle_{stage.get('cycle')}")
        if mode == "ppo":
            if stage.get("anneal_loss_flag"):
                reasons.append(f"loss_flag_cycle_{stage.get('cycle')}")
            if stage.get("anneal_queue_flag"):
                reasons.append(f"queue_flag_cycle_{stage.get('cycle')}")
            if stage.get("anneal_intensity_flag"):
                reasons.append(f"intensity_flag_cycle_{stage.get('cycle')}")
    return reasons


def evaluate(payload: Dict[str, Any]) -> Dict[str, Any]:
    results = payload.get("results")
    promotion_block = payload.get("promotion")
    if not isinstance(promotion_block, dict):
        promotion_block = {}

    simple_payload = False
    if not isinstance(results, list):
        bc_accuracy = payload.get("bc_accuracy")
        bc_threshold = payload.get("bc_threshold")
        if bc_accuracy is None or bc_threshold is None:
            raise ValueError("Payload must include a 'results' array or BC fields")
        bc_passed = bool(payload.get("bc_passed", bc_accuracy >= bc_threshold))
        results = [
            {
                "mode": "bc",
                "cycle": payload.get("cycle", 0),
                "passed": bc_passed,
                "accuracy": bc_accuracy,
                "threshold": bc_threshold,
            }
        ]
        promotion_block = promotion_block or {}
        candidate_ready = bool(payload.get("candidate_ready", bc_passed))
        status = payload.get("status") or ("pass" if bc_passed else "fail")
        simple_payload = True
    else:
        status = payload.get("status") or _derive_status(results)
        candidate_ready = bool(promotion_block.get("candidate_ready", False))

    status_lower = str(status).lower()
    reasons = _collect_reasons(results)

    if simple_payload:
        decision = "PROMOTE" if status_lower == "pass" else "HOLD"
    else:
        if status_lower == "pass" and candidate_ready:
            decision = "PROMOTE"
        elif status_lower == "pass":
            decision = "HOLD"
            reasons.append("candidate_not_ready")
        elif status_lower == "hold":
            decision = "HOLD"
        else:
            decision = "FAIL"

    return {
        "status": status_lower,
        "decision": decision,
        "candidate_ready": candidate_ready,
        "promotion": promotion_block,
        "results": results,
        "reasons": reasons,
    }


def _print_human(summary: Dict[str, Any]) -> None:
    lines = [
        f"Decision: {summary['decision']}",
        f"Status:   {summary['status']}",
        f"Ready?:   {'yes' if summary['candidate_ready'] else 'no'}",
    ]
    promotion = summary.get("promotion", {})
    if isinstance(promotion, dict) and promotion:
        streak = promotion.get("pass_streak")
        required = promotion.get("required_passes")
        lines.append(
            f"Pass streak: {streak}/{required} (last result: {promotion.get('last_result')})"
        )
    reasons = summary.get("reasons") or []
    if reasons:
        lines.append("Reasons:")
        lines.extend(f"  - {reason}" for reason in reasons)
    print("\n".join(lines))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.input_path and args.summary_path:
        print("Provide either --input or --summary, not both.", file=sys.stderr)
        return 2
    source_path = args.input_path or args.summary_path
    payload = _load_payload(source_path)
    summary = evaluate(payload)
    if args.format == "json":
        print(json.dumps(summary, indent=2))
    else:
        _print_human(summary)
    if args.dry_run:
        return 0
    decision = summary["decision"]
    if decision == "PROMOTE":
        return 0
    if decision == "HOLD":
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

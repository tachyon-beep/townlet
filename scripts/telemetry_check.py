"""Validate Townlet telemetry payloads against known schema versions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

SUPPORTED_SCHEMAS = {
    "0.2.0": {
        "employment_keys": {
            "pending",
            "pending_count",
            "exits_today",
            "daily_exit_cap",
            "queue_limit",
            "review_window",
        },
        "job_required_keys": {
            "job_id",
            "on_shift",
            "wallet",
            "shift_state",
            "attendance_ratio",
            "late_ticks_today",
            "wages_withheld",
        },
    }
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Townlet telemetry JSON")
    parser.add_argument("payload", type=Path, help="Path to telemetry JSON file (snapshot or smoke metrics)")
    parser.add_argument(
        "--schema",
        type=str,
        help="Override schema version (defaults to payload's schema_version field)",
    )
    return parser.parse_args()


def load_payload(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("Telemetry payload must be a JSON object")
    return data


def validate(payload: Dict[str, Any], schema_version: str) -> None:
    schema = SUPPORTED_SCHEMAS.get(schema_version)
    if schema is None:
        raise ValueError(f"Unsupported schema_version '{schema_version}'. Known: {sorted(SUPPORTED_SCHEMAS)}")

    employment = payload.get("employment") or payload.get("employment_metrics")
    if employment is None:
        raise ValueError("Payload missing employment metrics section")

    missing_employment = schema["employment_keys"] - employment.keys()
    if missing_employment:
        raise ValueError(f"Employment metrics missing keys: {sorted(missing_employment)}")

    jobs = payload.get("jobs")
    if isinstance(jobs, dict):
        for agent_id, agent_payload in jobs.items():
            missing_agent = schema["job_required_keys"] - agent_payload.keys()
            if missing_agent:
                raise ValueError(
                    f"Agent '{agent_id}' missing job keys: {sorted(missing_agent)} (schema {schema_version})"
                )


def main() -> None:
    args = parse_args()
    payload = load_payload(args.payload)
    schema_version = args.schema or payload.get("schema_version") or payload.get("enforce_job_loop") and "0.2.0"
    if schema_version is None:
        raise ValueError("Could not determine schema_version; specify with --schema")
    validate(payload, schema_version)
    print(f"Telemetry payload valid for schema {schema_version}.")


if __name__ == "__main__":
    main()

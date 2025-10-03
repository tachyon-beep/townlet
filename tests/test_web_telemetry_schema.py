from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from townlet_ui.telemetry import TelemetryClient

FIXTURE_DIR = Path("tests/data/web_telemetry")
SNAPSHOT_PATH = FIXTURE_DIR / "snapshot.json"
DIFF_PATH = FIXTURE_DIR / "diff.json"


def _load_payload(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _apply_diff(base: dict, diff: dict) -> dict:
    merged = deepcopy(base)
    merged["schema_version"] = diff.get("schema_version", merged.get("schema_version"))
    if "tick" in diff:
        merged["tick"] = diff["tick"]
    for key, value in diff.get("changes", {}).items():
        merged[key] = value
    for key in diff.get("removed", []):
        merged.pop(key, None)
    merged.setdefault("payload_type", "snapshot")
    return merged


def test_snapshot_fixture_parses_with_telemetry_client() -> None:
    payload = _load_payload(SNAPSHOT_PATH)
    # ensure payload advertises snapshot semantics
    assert payload.get("payload_type", "snapshot") == "snapshot"
    client = TelemetryClient()
    parsed = client.parse_payload(payload)
    # sanity check a couple of core fields
    assert parsed.schema_version
    assert parsed.transport.connected in {True, False}
    assert parsed.employment.pending_count >= 0


def test_diff_fixture_applies_cleanly() -> None:
    snapshot_payload = _load_payload(SNAPSHOT_PATH)
    diff_payload = _load_payload(DIFF_PATH)
    assert diff_payload.get("payload_type") == "diff"

    client = TelemetryClient()
    baseline = client.parse_payload(snapshot_payload)
    incremental = client.parse_payload(diff_payload)

    recomposed_payload = _apply_diff(snapshot_payload, diff_payload)
    recomposed_client = TelemetryClient()
    recomposed = recomposed_client.parse_payload(recomposed_payload)

    # TelemetryClient stores the original payload under `raw`; the diff snapshot keeps
    # only the incremental fields. Compare everything except the raw dictionary.
    incremental_dict = incremental.__dict__.copy()
    recomposed_dict = recomposed.__dict__.copy()
    incremental_dict.pop("raw", None)
    recomposed_dict.pop("raw", None)
    assert recomposed_dict == incremental_dict

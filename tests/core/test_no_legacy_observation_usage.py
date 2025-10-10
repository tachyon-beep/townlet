from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src" / "townlet"

WHITELIST_PATHS = {
    (SRC_ROOT / "core" / "sim_loop.py").resolve(),
    (SRC_ROOT / "factories" / "world_factory.py").resolve(),
    (SRC_ROOT / "adapters" / "world_default.py").resolve(),
    (SRC_ROOT / "config" / "observations.py").resolve(),
}

EXCLUDED_DIRS = {
    (SRC_ROOT / "observations").resolve(),
}

TOKEN_WHITELISTS: dict[str, set[Path]] = {
    "telemetry._ingest_loop_tick": {
        (SRC_ROOT / "telemetry" / "publisher.py").resolve(),
    },
}

FORBIDDEN_TOKENS = {
    "loop.observations": "legacy loop.observations access",
    "_policy_observation_batch": "legacy policy observation cache",
    "telemetry._ingest_loop_tick": "manual telemetry ingestion helper",
}


def _is_excluded(path: Path) -> bool:
    resolved = path.resolve()
    return any(resolved == excluded or excluded in resolved.parents for excluded in EXCLUDED_DIRS)


def _is_whitelisted(path: Path) -> bool:
    resolved = path.resolve()
    return resolved in WHITELIST_PATHS


def _token_whitelisted(token: str, path: Path) -> bool:
    resolved = path.resolve()
    return resolved in TOKEN_WHITELISTS.get(token, set())


def test_no_legacy_observation_usage() -> None:
    offences: list[str] = []

    for path in SRC_ROOT.rglob("*.py"):
        if _is_excluded(path):
            continue

        rel_path = path.relative_to(PROJECT_ROOT)
        text = path.read_text(encoding="utf-8")

        if "ObservationBuilder" in text and not _is_whitelisted(path):
            offences.append(f"{rel_path}: unexpected ObservationBuilder reference")

        for token, message in FORBIDDEN_TOKENS.items():
            if token in text and not _token_whitelisted(token, path):
                offences.append(f"{rel_path}: {message}")

    assert not offences, "Legacy observation pathways detected:\n" + "\n".join(sorted(offences))

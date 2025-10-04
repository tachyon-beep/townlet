#!/usr/bin/env python
"""Audit behaviour cloning datasets for checksum and metadata freshness."""
from __future__ import annotations

from collections.abc import Mapping
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

DEFAULT_VERSIONS_PATH = Path("data/bc_datasets/versions.json")
REQUIRED_VERSION_KEYS = {"manifest", "checksums", "captures_dir"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit BC dataset catalogue")
    parser.add_argument(
        "--versions",
        type=Path,
        default=DEFAULT_VERSIONS_PATH,
        help="Path to versions.json (default: data/bc_datasets/versions.json)",
    )
    parser.add_argument(
        "--exit-on-failure",
        action="store_true",
        help="Return non-zero exit code if any dataset fails validation",
    )
    return parser.parse_args()


def load_versions(path: Path) -> Mapping[str, Mapping[str, object]]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text())
    if not isinstance(data, Mapping):
        raise ValueError("versions.json must contain a JSON object")
    return data


def audit_dataset(name: str, payload: Mapping[str, object]) -> dict[str, object]:
    missing_keys = [key for key in REQUIRED_VERSION_KEYS if key not in payload]
    findings: list[str] = []
    status = "PASS"

    manifest_path = Path(payload.get("manifest", ""))
    checksums_path = Path(payload.get("checksums", ""))
    captures_dir = Path(payload.get("captures_dir", ""))

    if missing_keys:
        findings.append(f"Missing keys: {', '.join(missing_keys)}")
        status = "FAIL"

    manifest_exists = manifest_path.exists()
    checksums_exists = checksums_path.exists()
    captures_exists = captures_dir.exists()
    if not manifest_exists:
        findings.append(f"Manifest missing: {manifest_path}")
        status = "FAIL"
    if not checksums_exists:
        findings.append(f"Checksum file missing: {checksums_path}")
        status = "FAIL"
    if not captures_exists:
        findings.append(f"Captures dir missing: {captures_dir}")
        status = "WARN"

    checksum_data: dict[str, dict[str, str]] = {}
    if checksums_exists:
        data = json.loads(checksums_path.read_text())
        if isinstance(data, Mapping):
            checksum_data = {str(k): dict(v) for k, v in data.items() if isinstance(v, Mapping)}
        else:
            findings.append("checksums file is not an object")
            status = "FAIL"

    checksum_failures: list[str] = []
    if checksum_data:
        for sample_name, entry in checksum_data.items():
            sample_path = captures_dir / Path(entry.get("sample", sample_name)).name
            meta_path = captures_dir / Path(entry.get("meta", f"{sample_name}.json")).name
            expected_digest = entry.get("sha256")
            if not expected_digest:
                checksum_failures.append(f"{sample_name}: missing sha256")
                continue
            if not sample_path.exists() or not meta_path.exists():
                checksum_failures.append(
                    f"{sample_name}: sample/meta missing ({sample_path}, {meta_path})"
                )
                continue
            digest = hashlib.sha256(sample_path.read_bytes() + meta_path.read_bytes()).hexdigest()
            if digest != expected_digest:
                checksum_failures.append(
                    f"{sample_name}: checksum mismatch expected={expected_digest} actual={digest}"
                )
        if checksum_failures:
            status = "FAIL"
            findings.extend(checksum_failures)

    manifest_entries: list[dict] = []
    if manifest_exists:
        manifest_data = json.loads(manifest_path.read_text())
        if isinstance(manifest_data, list):
            manifest_entries = [entry for entry in manifest_data if isinstance(entry, dict)]
        else:
            findings.append("manifest is not a list")
            status = "FAIL"

    stale_entries: list[str] = []
    for entry in manifest_entries:
        meta_path = captures_dir / Path(entry.get("meta", "")).name
        if not meta_path.exists():
            stale_entries.append(meta_path.name)
    if stale_entries:
        findings.append("Stale manifest entries: " + ", ".join(stale_entries))
        status = "WARN" if status != "FAIL" else status

    dataset_info = {
        "name": name,
        "status": status,
        "manifest": str(manifest_path),
        "checksums": str(checksums_path),
        "captures": str(captures_dir),
        "findings": findings,
        "sample_count": len(manifest_entries),
    }
    return dataset_info


def audit_catalog(versions_path: Path) -> dict[str, object]:
    datasets = load_versions(versions_path)
    results = []
    failures = 0
    warnings = 0
    for name, payload in datasets.items():
        if not isinstance(payload, Mapping):
            continue
        report = audit_dataset(name, payload)
        results.append(report)
        if report["status"] == "FAIL":
            failures += 1
        elif report["status"] == "WARN":
            warnings += 1
    return {
        "versions_path": str(versions_path),
        "datasets": results,
        "failures": failures,
        "warnings": warnings,
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


def main() -> None:
    args = parse_args()
    report = audit_catalog(args.versions)
    print(json.dumps(report, indent=2))
    if args.exit_on_failure and report["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":  # pragma: no cover
    main()

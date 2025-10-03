"""Validate affordance manifest files for schema compliance.

This CLI loads each supplied YAML manifest using the Townlet affordance manifest
loader, reporting checksums and entry counts. Non-compliant manifests cause a
non-zero exit status so the script can run in CI.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List

from townlet.config.affordance_manifest import (
    AffordanceManifest,
    AffordanceManifestError,
    load_affordance_manifest,
)
from townlet.world.preconditions import (
    PreconditionSyntaxError,
    compile_preconditions,
)

DEFAULT_SEARCH_ROOT = Path("configs/affordances")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Townlet affordance manifest YAML files",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help=(
            "Manifest files or directories to validate."
            " Directories are searched recursively for *.yaml and *.yml files."
            f" Defaults to {DEFAULT_SEARCH_ROOT} if no arguments are given."
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if no manifests are discovered (useful in CI).",
    )
    return parser.parse_args()


def discover_manifests(inputs: Iterable[str]) -> List[Path]:
    if not inputs:
        inputs = [str(DEFAULT_SEARCH_ROOT)]
    manifests: List[Path] = []
    for entry in inputs:
        path = Path(entry).expanduser()
        if path.is_dir():
            for candidate in sorted(path.rglob("*.yml")):
                manifests.append(candidate)
            for candidate in sorted(path.rglob("*.yaml")):
                manifests.append(candidate)
        elif path.suffix.lower() in {".yml", ".yaml"}:
            manifests.append(path)
        else:
            # Non-YAML files are ignored, but still warn so users know.
            print(f"[warn] Skipping non-manifest path: {path}", file=sys.stderr)
    # Deduplicate while preserving order.
    unique: List[Path] = []
    seen: set[Path] = set()
    for manifest in manifests:
        if manifest not in seen:
            unique.append(manifest)
            seen.add(manifest)
    return unique


def validate_manifest(path: Path) -> AffordanceManifest:
    try:
        manifest = load_affordance_manifest(path)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Manifest not found: {path}") from exc
    except AffordanceManifestError as exc:
        raise RuntimeError(f"Manifest {path} invalid: {exc}") from exc
    for affordance in manifest.affordances:
        try:
            compile_preconditions(affordance.preconditions)
        except PreconditionSyntaxError as exc:
            raise RuntimeError(
                "Manifest "
                f"{path} invalid: affordance '{affordance.affordance_id}' preconditions "
                f"failed to compile ({exc})"
            ) from exc
    return manifest


def main() -> int:
    args = parse_args()
    manifests = discover_manifests(args.paths)
    if not manifests:
        message = "No affordance manifests found."
        if args.strict:
            print(f"[error] {message}", file=sys.stderr)
            return 1
        print(f"[info] {message}")
        return 0

    failures: List[str] = []
    for manifest_path in manifests:
        try:
            manifest = validate_manifest(manifest_path)
        except RuntimeError as exc:
            failures.append(str(exc))
            continue
        print(
            f"[ok] {manifest.path} sha256={manifest.checksum}"
            f" objects={manifest.object_count} affordances={manifest.affordance_count}"
        )

    if failures:
        print("[error] One or more manifests failed validation:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

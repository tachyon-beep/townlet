"""Utilities for validating affordance manifest files."""

from __future__ import annotations

import hashlib
import logging
from collections.abc import Iterable, Mapping
from typing import Any, cast
from dataclasses import dataclass
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ManifestObject:
    """Represents an interactive object entry from the manifest."""

    object_id: str
    object_type: str
    stock: dict[str, int]
    position: tuple[int, int] | None = None


@dataclass(frozen=True)
class ManifestAffordance:
    """Represents an affordance definition with preconditions and hooks."""

    affordance_id: str
    object_type: str
    duration: int
    effects: dict[str, float]
    preconditions: list[str]
    hooks: dict[str, list[str]]


@dataclass(frozen=True)
class AffordanceManifest:
    """Normalised manifest contents and checksum metadata."""

    path: Path
    checksum: str
    objects: list[ManifestObject]
    affordances: list[ManifestAffordance]

    @property
    def object_count(self) -> int:
        """Return number of object entries defined in the manifest."""

        return len(self.objects)

    @property
    def affordance_count(self) -> int:
        """Return number of affordance entries defined in the manifest."""

        return len(self.affordances)


class AffordanceManifestError(ValueError):
    """Raised when an affordance manifest fails validation."""


_ALLOWED_HOOK_KEYS = {"before", "after", "fail"}


def load_affordance_manifest(path: Path) -> AffordanceManifest:
    """Load and validate an affordance manifest, returning structured entries.

    Args:
        path: Path to the YAML manifest file.

    Raises:
        FileNotFoundError: If the manifest does not exist.
        AffordanceManifestError: If schema validation or duplicate detection fails.
    """

    if not path.exists():
        raise FileNotFoundError(f"Affordance manifest not found: {path}")

    raw_bytes = path.read_bytes()
    checksum = hashlib.sha256(raw_bytes).hexdigest()
    payload = yaml.safe_load(raw_bytes.decode("utf-8")) or []
    if not isinstance(payload, Iterable) or isinstance(payload, Mapping):
        raise AffordanceManifestError(
            f"Affordance manifest {path} must be a list of entries"
        )

    objects: list[ManifestObject] = []
    affordances: list[ManifestAffordance] = []
    seen_ids: set[str] = set()

    for index, entry in enumerate(payload):
        if not isinstance(entry, Mapping):
            raise AffordanceManifestError(
                f"Entry {index} in {path} must be a mapping, found {type(entry).__name__}"
            )
        entry_type = str(entry.get("type", "affordance")).lower()
        if entry_type == "object":
            obj = _parse_object_entry(entry, path, index)
            _ensure_unique(obj.object_id, seen_ids, path, index)
            objects.append(obj)
        elif entry_type == "affordance":
            affordance = _parse_affordance_entry(entry, path, index)
            _ensure_unique(affordance.affordance_id, seen_ids, path, index)
            affordances.append(affordance)
        else:
            raise AffordanceManifestError(
                f"Entry {index} in {path} has unsupported type '{entry_type}'"
            )

    logger.info(
        "Loaded affordance manifest %s (objects=%d, affordances=%d, sha256=%s)",
        path,
        len(objects),
        len(affordances),
        checksum,
    )
    return AffordanceManifest(
        path=path,
        checksum=checksum,
        objects=objects,
        affordances=affordances,
    )


def _parse_object_entry(
    entry: Mapping[str, object], path: Path, index: int
) -> ManifestObject:
    object_id = _require_string(entry, "id", path, index)
    object_type = _require_string(entry, "object_type", path, index)
    stock_raw = entry.get("stock", {})
    if not isinstance(stock_raw, Mapping):
        raise AffordanceManifestError(
            f"Entry {index} ({object_id}) in {path} has invalid 'stock' field"
        )
    stock: dict[str, int] = {}
    for key, value in stock_raw.items():
        if not isinstance(key, str):
            raise AffordanceManifestError(
                f"Entry {index} ({object_id}) in {path} has non-string stock key"
            )
        try:
            int_value = int(cast(Any, value))
        except (TypeError, ValueError):
            raise AffordanceManifestError(
                f"Entry {index} ({object_id}) in {path} has non-integer stock for '{key}'"
            ) from None
        if int_value < 0:
            raise AffordanceManifestError(
                f"Entry {index} ({object_id}) in {path} has negative stock for '{key}'"
            )
        stock[key] = int_value
    position = _parse_position(
        entry.get("position"), path=path, index=index, entry_id=object_id
    )
    return ManifestObject(
        object_id=object_id,
        object_type=object_type,
        stock=stock,
        position=position,
    )


def _parse_affordance_entry(
    entry: Mapping[str, object], path: Path, index: int
) -> ManifestAffordance:
    affordance_id = _require_string(entry, "id", path, index)
    object_type = _require_string(entry, "object_type", path, index)

    duration_raw = entry.get("duration")
    if duration_raw is None:
        raise AffordanceManifestError(
            f"Entry {index} ({affordance_id}) in {path} is missing 'duration'"
        )
    try:
        duration = int(cast(Any, duration_raw))
    except (TypeError, ValueError):
        raise AffordanceManifestError(
            f"Entry {index} ({affordance_id}) in {path} has non-integer duration"
        ) from None
    if duration <= 0:
        raise AffordanceManifestError(
            f"Entry {index} ({affordance_id}) in {path} must have duration > 0"
        )

    effects_raw = entry.get("effects")
    if not isinstance(effects_raw, Mapping) or not effects_raw:
        raise AffordanceManifestError(
            f"Entry {index} ({affordance_id}) in {path} must define non-empty 'effects'"
        )
    effects: dict[str, float] = {}
    for name, value in effects_raw.items():
        if not isinstance(name, str):
            raise AffordanceManifestError(
                f"Entry {index} ({affordance_id}) in {path} has non-string effect name"
            )
        try:
            effects[name] = float(value)
        except (TypeError, ValueError):
            raise AffordanceManifestError(
                f"Entry {index} ({affordance_id}) in {path} has non-numeric effect for '{name}'"
            ) from None

    preconds_raw = entry.get("preconds", [])
    preconditions = _parse_string_list(
        preconds_raw,
        field="preconds",
        path=path,
        index=index,
        entry_id=affordance_id,
    )

    hooks_raw = entry.get("hooks", {})
    hooks: dict[str, list[str]] = {}
    if hooks_raw:
        if not isinstance(hooks_raw, Mapping):
            raise AffordanceManifestError(
                f"Entry {index} ({affordance_id}) in {path} has invalid 'hooks' mapping"
            )
        for key, value in hooks_raw.items():
            if key not in _ALLOWED_HOOK_KEYS:
                raise AffordanceManifestError(
                    f"Entry {index} ({affordance_id}) in {path} has unknown hook '{key}'"
                )
            hooks[key] = _parse_string_list(
                value,
                field=f"hooks.{key}",
                path=path,
                index=index,
                entry_id=affordance_id,
            )

    return ManifestAffordance(
        affordance_id=affordance_id,
        object_type=object_type,
        duration=duration,
        effects=effects,
        preconditions=preconditions,
        hooks=hooks,
    )


def _parse_position(
    value: object,
    *,
    path: Path,
    index: int,
    entry_id: str,
) -> tuple[int, int] | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple)) and len(value) == 2:
        try:
            x = int(cast(Any, value[0]))
            y = int(cast(Any, value[1]))
            return (x, y)
        except (TypeError, ValueError):
            raise AffordanceManifestError(
                f"Entry {index} ({entry_id}) in {path} has non-integer position coordinates"
            ) from None
    raise AffordanceManifestError(
        f"Entry {index} ({entry_id}) in {path} has invalid position (expected [x, y])"
    )


def _parse_string_list(
    value: object,
    *,
    field: str,
    path: Path,
    index: int,
    entry_id: str,
) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, str):
        return [value]
    if not isinstance(value, Iterable) or isinstance(value, Mapping):
        raise AffordanceManifestError(
            f"Entry {index} ({entry_id}) in {path} has invalid '{field}' list"
        )
    items: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise AffordanceManifestError(
                f"Entry {index} ({entry_id}) in {path} has non-string value in '{field}'"
            )
        if not item.strip():
            raise AffordanceManifestError(
                f"Entry {index} ({entry_id}) in {path} has empty string in '{field}'"
            )
        items.append(item)
    return items


def _require_string(
    entry: Mapping[str, object],
    field: str,
    path: Path,
    index: int,
) -> str:
    value = entry.get(field)
    if value is None:
        raise AffordanceManifestError(
            f"Entry {index} in {path} is missing required field '{field}'"
        )
    if not isinstance(value, str) or not value.strip():
        raise AffordanceManifestError(
            f"Entry {index} in {path} must provide non-empty string for '{field}'"
        )
    return value.strip()


def _ensure_unique(entry_id: str, seen: set[str], path: Path, index: int) -> None:
    if entry_id in seen:
        raise AffordanceManifestError(
            f"Entry {index} in {path} has duplicate id '{entry_id}'"
        )
    seen.add(entry_id)

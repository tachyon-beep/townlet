"""Snapshot configuration models and validators."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class SnapshotStorageConfig(BaseModel):
    """Location and retention policy for snapshot storage."""

    root: Path = Field(default=Path("snapshots"))

    @model_validator(mode="after")
    def _validate_root(self) -> SnapshotStorageConfig:
        if str(self.root).strip() == "":
            raise ValueError("snapshot.storage.root must not be empty")
        return self


class SnapshotAutosaveConfig(BaseModel):
    """Autosave cadence and retention settings."""

    cadence_ticks: int | None = Field(default=None, ge=1)
    retain: int = Field(default=3, ge=1, le=1000)

    @model_validator(mode="after")
    def _validate_cadence(self) -> SnapshotAutosaveConfig:
        if self.cadence_ticks is not None and self.cadence_ticks < 100:
            raise ValueError("snapshot.autosave.cadence_ticks must be at least 100 ticks when enabled")
        return self


class SnapshotIdentityConfig(BaseModel):
    """Identity metadata embedded in snapshot files."""

    observation_variant: Literal["hybrid", "full", "compact", "infer"] = "infer"
    policy_hash: str | None = None
    policy_artifact: Path | None = None
    anneal_ratio: float | None = Field(default=None, ge=0.0, le=1.0)

    _HEX40 = re.compile(r"^[0-9a-fA-F]{40}$")
    _HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
    _BASE64 = re.compile(r"^[A-Za-z0-9+/=]{32,88}$")

    @model_validator(mode="after")
    def _validate_policy_hash(self) -> SnapshotIdentityConfig:
        if self.policy_hash is None:
            return self
        candidate = self.policy_hash.strip()
        if not candidate:
            raise ValueError("snapshot.identity.policy_hash must not be blank if provided")
        if not (self._HEX40.match(candidate) or self._HEX64.match(candidate) or self._BASE64.match(candidate)):
            raise ValueError("snapshot.identity.policy_hash must be a 40/64-char hex or base64-encoded digest")
        self.policy_hash = candidate
        return self

    @model_validator(mode="after")
    def _validate_variant(self) -> SnapshotIdentityConfig:
        if self.observation_variant == "infer":
            return self
        supported: set[str] = {"hybrid", "full", "compact"}
        if self.observation_variant not in supported:
            raise ValueError(
                f"snapshot.identity.observation_variant must be one of {sorted(supported)} or 'infer'"
            )
        return self


class SnapshotMigrationsConfig(BaseModel):
    """Toggle for applying snapshot migrations on load."""

    handlers: dict[str, str] = Field(default_factory=dict)
    auto_apply: bool = False
    allow_minor: bool = False

    @model_validator(mode="after")
    def _validate_handlers(self) -> SnapshotMigrationsConfig:
        for legacy_id, target in self.handlers.items():
            if not str(legacy_id).strip():
                raise ValueError("snapshot.migrations.handlers keys must not be empty")
            if not str(target).strip():
                raise ValueError("snapshot.migrations.handlers values must not be empty")
        return self


class SnapshotGuardrailsConfig(BaseModel):
    """Snapshot validation guardrails and allowlists."""

    require_exact_config: bool = True
    allow_downgrade: bool = False
    allowed_paths: list[Path] = Field(default_factory=list)


class SnapshotConfig(BaseModel):
    """Grouping of snapshot-related configuration sections."""

    storage: SnapshotStorageConfig = SnapshotStorageConfig()
    autosave: SnapshotAutosaveConfig = SnapshotAutosaveConfig()
    identity: SnapshotIdentityConfig = SnapshotIdentityConfig()
    migrations: SnapshotMigrationsConfig = SnapshotMigrationsConfig()
    guardrails: SnapshotGuardrailsConfig = SnapshotGuardrailsConfig()
    capture_on_failure: bool = False

    @model_validator(mode="after")
    def _validate_observation_override(self) -> SnapshotConfig:
        if self.identity.observation_variant != "infer" and self.identity.observation_variant not in {
            "hybrid",
            "full",
            "compact",
        }:
            raise ValueError(
                "snapshot.identity.observation_variant must be one of ['hybrid', 'full', 'compact', 'infer']"
            )
        return self


__all__ = [
    "SnapshotAutosaveConfig",
    "SnapshotConfig",
    "SnapshotGuardrailsConfig",
    "SnapshotIdentityConfig",
    "SnapshotMigrationsConfig",
    "SnapshotStorageConfig",
]


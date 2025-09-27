# WP-05 Technical Design — Snapshot & Config Identity

## 1. Scope & Goals
- Raise snapshot schema to v1.4 so it captures policy/config identity alongside deterministic state (world, RNG streams, anneal progress).
- Introduce a migration framework that allows controlled upgrades when `config_id` changes, while preserving “fail fast” guarantees when no migration exists.
- Make snapshot health observable through telemetry, console tooling, and audit logs.

Non-goals: replace storage backend, add remote persistence, or design full policy promotion tooling (tracked separately).

## 2. Schema Updates (v1.4)
### 2.1 Additions
- `identity.policy_hash: str` — immutable digest representing the policy binary/checkpoint in use.
- `identity.policy_artifact: str | null` — optional path/URI to the artefact that produced the hash.
- `identity.observation_variant: str` — explicit variant at capture time (`full|hybrid|compact`).
- `identity.anneal_ratio: float | null` — fraction (0..1) showing mixed scripted vs learned weight when anneal is active.
- `rng`: replace legacy single-state field with
  ```json
  {
    "world": "<base64>",
    "events": "<base64>",
    "policy": "<base64>"
  }
  ```
  Each value encodes a pickled RNG state (Python `random.Random` or numpy PCG64 if we migrate later).
- `migrations.applied`: ordered list of migration IDs applied during load (empty on fresh saves).
- `migrations.required`: populated when loader detects mismatch but a migration exists; persists the recommendation if operator declines auto-apply.

### 2.2 Backwards Compatibility
- Loader supports v1.3 by inferring identity fields from `SimulationConfig` (`policy_hash` from config, `observation_variant` from `features.systems.observations`, `anneal_ratio=None`, RNG→`world` only). Migration metadata stays empty.
- Any snapshot < v1.3 (legacy deployments) remains unsupported; loader continues to reject with schema error.
- `SnapshotManager.save` writes `schema_version="1.4"` and fills new fields. Export helpers (`snapshot_from_world`) accept optional `policy_hash`, `anneal_ratio`, and RNG handles.

## 3. Configuration & Runtime Plumbing
### 3.1 SnapshotConfig (new)
Add `SnapshotConfig` to `SimulationConfig` with sections:
- `storage.root: Path` (default `snapshots/`).
- `autosave.cadence_ticks: int | None`, `autosave.retain: int`.
- `identity.policy_hash: str` (required), `identity.policy_artifact: Path | None`, `identity.observation_variant: ObservationVariant | "infer"`, `identity.anneal_ratio: float | None`.
- `migrations.handlers: dict[str, str]`, `migrations.auto_apply: bool`, `migrations.allow_minor: bool`.
- `guardrails.require_exact_config: bool`, `guardrails.allow_downgrade: bool`.

### 3.2 Policy Hash Source
- `PolicyRunner` exposes `active_policy_hash()` returning deterministic hash of the loaded policy checkpoint (SHA256 of weight file plus observation variant).
- When policy runner is not initialised (viewer-only replay), fallback to `snapshot.identity.policy_hash` from config.

### 3.3 Anneal Ratio Source
- `PolicyRunner` already tracks anneal context in `_anneal_context`; expose `current_anneal_ratio()` and `current_stage()` for snapshot capture.
- Simulation loop obtains anneal ratio during persistence step.

### 3.4 RNG Streams
- `SimulationLoop` owns three RNGs (`world_rng`, `event_rng`, `policy_rng`) seeded at config load. Replace direct `random.getstate()` in `WorldState` with references to these objects.
- Snapshot capture serialises each stream; loader restores by setting `setstate()` on the owning RNG instances.

## 4. Migration Framework
### 4.1 Registry
- New module `townlet.snapshots.migrations` exposing `SnapshotMigrationRegistry` singleton.
- API: `register(from_config: str, to_config: str, handler: MigrationHandler)` where handler signature is `handler(state: SnapshotState, config: SimulationConfig) -> SnapshotState`.
- Handlers must be idempotent; they can mutate state in place or return new copy. Registry enforces deterministic ordering (sorted by `from_config` → `to_config`).

### 4.2 Load Flow
1. Loader reads snapshot → `SnapshotState`.
2. If `state.config_id == config.config_id`: no migration; ensure identity fields align.
3. Else lookup migrations where `from=state.config_id`, `to=config.config_id`.
4. If none and `snapshot.guardrails.require_exact_config` is `True`: raise `SnapshotConfigMismatch` (`E_SNAPSHOT_CONFIG_MISMATCH`).
5. If handler exists:
   - When `auto_apply` enabled: run handler(s), append identifiers to `state.migrations.applied`, log action, and verify `state.config_id` updated.
   - When disabled: raise `SnapshotMigrationRequired` with `migrations.required` populated so console/telemetry can surface instructions.
6. If handler chain fails, wrap exception in `SnapshotMigrationError` with context (which step failed, message).

### 4.3 Error Taxonomy
- `E_SNAPSHOT_SCHEMA_MISMATCH` — schema version unsupported.
- `E_SNAPSHOT_CONFIG_MISMATCH` — config IDs differ and no migration allowed.
- `E_SNAPSHOT_MIGRATION_REQUIRED` — migration handlers exist but auto-apply disabled; includes handler IDs.
- `E_SNAPSHOT_MIGRATION_FAILED` — handler raised; message includes handler name and root cause.
- `E_SNAPSHOT_IDENTITY_MISMATCH` — post-load identity values disagree with config (policy hash, observation variant) even after migration.

Errors propagate through console commands and telemetry; `SnapshotManager` converts them into structured dicts for logging.

## 5. Observability & Tooling
- Telemetry payload gets new block `snapshot_identity` with `policy_hash`, `config_id`, `anneal_ratio`, `last_saved_tick`, `schema_version`.
- Console command `snapshot_inspect <path>` returns identity + migration metadata.
- `snapshot_migrate <path>` attempts migrations according to config; optionally accepts `--force` to override guardrails (admin only).
- Audit log entry (`logs/console/snapshot.jsonl`) records command, result, applied migrations, and duration.
- Telemetry emits `snapshot.migration_applied` event with handler list; failures produce `snapshot.migration_failed` including error code.

## 6. Testing Strategy
- Unit tests: RNG multi-stream round-trip, policy hash/anneal metadata persistence, migration registry (success/failure), configuration validation, console command validation.
- Integration test: simulate loading v1.3 snapshot under new config with registered migration; assert telemetry/log outputs.
- Property-based: optional quickcheck ensuring serialise→deserialize retains RNG state and identity under random world snapshots.

## 7. Rollout Plan
1. Implement config model + validation; update sample configs/tests.
2. Add policy runner helpers and RNG restructuring.
3. Implement schema changes + loader compatibility.
4. Introduce migration registry with seed handler (e.g., fill anneal ratio defaults).
5. Ship console/telemetry enhancements.
6. Update docs (`OPS_HANDBOOK`, `WORK_PACKAGES`, release notes) and mark WP-05 milestones complete.

Risks: policy hash discovery may require coordination with training infra; schedule buffer for exposing hash from checkpoint loader. Ensure migrations are optional until registry populated to avoid blocking existing operations.

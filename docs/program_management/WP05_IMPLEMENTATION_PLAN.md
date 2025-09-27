# WP-05 Implementation Plan — Snapshot & Config Identity

## Objectives
- Guarantee deterministic save/load cycles that capture world state, RNG streams, policy hash, observation variant, and anneal ratio.
- Enforce `config_id` integrity with explicit migration hooks when restoring legacy snapshots.
- Provide operators/devs with tooling, telemetry, and documentation to manage snapshots safely and diagnose mismatches.

## High-Level Milestones
1. **Schema & Config Alignment** — Finalise snapshot schema, config surfaces, and guardrails.
2. **Deterministic Persistence** — Capture/restore full world + RNG + policy metadata with round-trip guarantees.
3. **Migration & Compatibility Layer** — Design registry-driven migrations with validation, testing, and logging.
4. **Operator Experience** — Surface snapshot diagnostics via telemetry/console, document workflows, and gate CI.

## Phase Breakdown

### Phase 5.1 — Schema & Infrastructure Foundations
- **Step 5.1-S1: Spec Reconciliation**
  - Task: Consolidate requirements from `docs/program_management/snapshots/REQUIREMENTS.md`, `ARCHITECTURE_INTERFACES.md`, and `CONCEPTUAL_DESIGN.md` into a schema checklist (fields, invariants, determinism expectations).
  - Task: Identify current coverage in `src/townlet/snapshots/state.py` and gaps (e.g., multi-stream RNG, observation variant, anneal ratio, policy hash).
  - Task: Draft schema changelog (v1.3 → v1.4?) and publish in `docs/program_management/snapshots/REQUIREMENTS.md` appendices.
- **Step 5.1-S2: Configuration Surface Audit**
  - Task: Review `SimulationConfig` for existing `config_id` usage, determine new fields (e.g., `snapshot.migrations`, `snapshot.policy_hash_source`).
  - Task: Propose defaults and validation rules; update `docs/program_management/PROJECT_PLAN.md` if additional gates required.
- **Step 5.1-S3: Technical Design Write-Up**
  - Task: Produce implementation note (short design) covering schema updates, migration strategy, and error taxonomy; circulate via `docs/program_management/MASTER_PLAN_PROGRESS.md` or standalone supplement.

### Phase 5.2 — Deterministic Snapshot Capture
- **Step 5.2-S1: RNG Stream Management**
  - Task: Extend `WorldState` RNG handling to capture `world`, `events`, `policy` streams separately (consider `random.Random` instances or numpy RNG). Ensure tick loop seeds/restores correctly.
  - Task: Update `snapshot_from_world` to serialise all RNG streams with encoding symmetry; adjust `apply_snapshot_to_world` to restore them.
- **Step 5.2-S2: Policy & Config Metadata Capture**
  - Task: Define data source for active policy hash (e.g., pointer in policy runner or checkpoint manifest). Expose via `SimulationLoop` or `PolicyRuntime`.
  - Task: Persist observation variant, anneal ratio, and policy hash into snapshot payload.
  - Task: Update telemetry export/import to include deterministic metadata (for diffing issues).
- **Step 5.2-S3: Snapshot Persistence Enhancements**
  - Task: Version bump `SNAPSHOT_SCHEMA_VERSION` and adjust `SnapshotManager.save/load` to write new fields.
  - Task: Implement backward-compatible read (recognise v1.3, populate missing fields with defaults, flag that migration may be needed).
  - Task: Introduce checksum or signature (optional stretch) for integrity; log on save/load.
- **Status (2025-10-02):** ✅ Multi-stream RNG plumbing, policy identity capture, and schema v1.4 landed. Regression suite (`tests/test_snapshot_manager.py`) covers round-trips and backwards compatibility.

### Phase 5.3 — Migration Framework & Validation
- **Step 5.3-S1: Migration Registry Design**
  - Task: Add `SnapshotMigrationRegistry` module with API to register migrations keyed by `(from_config_id, to_config_id)`.
  - Task: Define migration interface (e.g., `apply(state: SnapshotState, config: SimulationConfig) -> SnapshotState`).
- **Step 5.3-S2: Enforcement & Error Handling**
  - Task: Update `SnapshotManager.load` to consult registry; on mismatch attempt migrations sequentially; bubble descriptive errors when missing or failed.
  - Task: Emit audit logs/telemetry when migrations run, including summary of modifications.
- **Step 5.3-S3: Reference Migrations & Tests**
  - Task: Implement sample migration (e.g., add default anneal ratio for v1.3 snapshots) to validate pipeline.
  - Task: Write pytest coverage for success/failure paths, including multi-step migrations and registry miss scenarios.
  - Task: Document migration authoring in developer docs.
- **Status (2025-10-02):** ✅ Registry shipped (`townlet.snapshots.migrations`), SnapshotManager auto-applies registered chains with telemetry logging, and new tests (`tests/test_snapshot_migrations.py`) cover success/missing-path scenarios. Authoring guidance appended to WP05 design note.

### Phase 5.4 — Console & Telemetry Tooling
- **Step 5.4-S1: Snapshot Diagnostics Commands**
  - Task: Add console commands (`snapshot_inspect`, `snapshot_migrate`, `snapshot_validate`) gated by admin mode.
  - Task: Provide descriptive error codes and help strings; ensure idempotent `cmd_id` usage.
- **Step 5.4-S2: Telemetry & Alerting**
  - Task: Expose latest snapshot metadata (config_id, policy hash, RNG checksums) via telemetry payloads and UI-friendly structures.
  - Task: Add alerts when snapshot load fails or migration triggered; integrate with stability console notifications.
- **Step 5.4-S3: Logging & Audit Trail**
  - Task: Log snapshot save/load events with config_id, policy hash, rng fingerprints, and migration outcomes.
  - Task: Consider storing audit entries under `logs/console/snapshot*.jsonl` for ops traceability.
- **Status (2025-10-02):** ✅ Console commands (`snapshot_inspect`, `snapshot_validate`, admin-only `snapshot_migrate`) implemented with telemetry exposure for policy identity and migration history; ops handbook updated.

### Phase 5.5 — Testing, CI, and Docs
- **Step 5.5-S1: Testing Matrix Expansion**
  - Task: Add unit tests for RNG round-trips, metadata persistence, migration registry, and error handling.
  - Task: Introduce integration test simulating snapshot save/load across config bump (mock migration).
  - Task: Optionally add property-based fuzz for snapshot serialization consistency.
- **Step 5.5-S2: CI Wiring**
  - Task: Ensure new tests included in default `pytest` target; update CI config/documentation if dedicated suite required.
  - Task: Run `ruff`/`mypy` adjustments for new modules.
- **Step 5.5-S3: Documentation & Ops Updates**
  - Task: Update `docs/ops/OPS_HANDBOOK.md` with snapshot workflow, migration usage, troubleshooting.
  - Task: Refresh `docs/program_management/snapshots/REQUIREMENTS.md` and `ARCHITECTURE_INTERFACES.md` to reference new schema version and tooling.
  - Task: Note completion in `docs/program_management/WORK_PACKAGES.md` once DoD met.

## Dependencies & Risk Mitigation
- Verify availability of policy hash source; coordinate with policy/runtime owners if new APIs needed.
- Confirm RNG handling aligns with training harness expectations; coordinate with RL team before altering seeding logic.
- Migration registry introduces operational risk; start with dry-run mode and thorough testing before enabling in production environments.
- Ensure documentation includes rollback procedure if migrations corrupt state; maintain backups of original snapshot files.

## Acceptance Criteria Recap
- Snapshot round-trips reproduce world state and RNG seeds deterministically.
- Snapshots persist `config_id`, policy hash, observation variant, anneal ratio, and multi-stream RNG states.
- Loading with mismatched `config_id` blocks unless approved migration runs successfully; errors are actionable.
- Console/telemetry expose snapshot health and migration activity.
- Tests and docs cover new behaviour; CI stays green.

## Phase 5.1 Findings (Step 5.1-S1)

### Snapshot Requirements Checklist
| Requirement | Source |
| --- | --- |
| Snapshot payload must include world state, RNG seeds (world/events/policy), policy hash, `config_id`, observation variant, anneal ratio | `docs/program_management/snapshots/REQUIREMENTS.md:157`
| `config_id` recorded in snapshots, logs, and release metadata; mismatched snapshots require migrations | `docs/program_management/snapshots/REQUIREMENTS.md:4-27`
| Tick loop persistence step records config/variant hashes during snapshot save | `docs/program_management/snapshots/ARCHITECTURE_INTERFACES.md:34`
| Snapshot load rejects `config_id` mismatch unless migration defined | `docs/program_management/snapshots/ARCHITECTURE_INTERFACES.md:134-136`
| Deterministic replay relies on three RNG streams captured/restored | `docs/program_management/snapshots/CONCEPTUAL_DESIGN.md:450-454`

### Current Coverage Assessment
| Item | Implementation refs | Status | Notes |
| --- | --- | --- | --- |
| World state (agents, objects, queues, employment, relationships) serialised | `src/townlet/snapshots/state.py:60-213` | Met | Existing schema captures core world/primitives with regression tests (`tests/test_snapshot_manager.py:34-198`). |
| `config_id` persisted & validated on load | `src/townlet/snapshots/state.py:33-109`, `src/townlet/snapshots/state.py:298-315` | Met | Loader raises on mismatch; no migration escape hatch yet. |
| Multi-stream RNG capture (`world`, `events`, `policy`) | `src/townlet/world/grid.py:121-164`, `src/townlet/snapshots/state.py:228-252` | Gap | Only single Python RNG state saved; event/policy streams not modelled. |
| Policy hash persistence | _n/a_ | Gap | No policy hash field or source of truth captured during snapshot save. |
| Observation variant + anneal ratio persistence | _n/a_ | Gap | Values live in `SimulationConfig`/training metadata but are not written to snapshots. |
| Config migration support | `src/townlet/snapshots/state.py:309-314` | Gap | Hard failure on mismatch; registry/run-time migrations absent. |
| Telemetry/config hash logging alongside snapshots | `src/townlet/snapshots/state.py:216-266` | Partial | Telemetry payload saved, but config/policy hashes not exposed for ops diffing. |

## Phase 5.1 Findings (Step 5.1-S2)

### Existing Configuration Surface
- `SimulationConfig` currently exposes `config_id` as the only snapshot-related identity field. No dedicated `snapshot` section or migration knobs exist in `src/townlet/config/loader.py`.
- Policy metadata (hash, checkpoint pointers) is not represented in config; training sections (`training`, `ppo`, `bc`) focus on optimisation settings.
- No controls for snapshot cadence, retention, or migration behaviour are presently configurable; behaviour is hard-coded in `SnapshotManager` callers.

### Proposed Configuration Extensions
| Section | Fields | Purpose | Default | Validation / Notes |
| --- | --- | --- | --- | --- |
| `snapshot.storage` | `root: Path` | Declare canonical save directory for snapshots; keeps ops + automation aligned. | `snapshots/` | Must resolve within workspace; validate path exists/creatable. |
| `snapshot.autosave` | `cadence_ticks: int | None`, `retain: int` | Enable optional periodic snapshots and retention policy. | `None`, `3` | `cadence_ticks` ≥ 100 when set; `retain` ≥ 1. |
| `snapshot.identity` | `policy_hash: str`, `policy_artifact: Path | None`, `observation_variant: ObservationVariant | "infer"`, `anneal_ratio: float | None` | Provide authoritative runtime identity to embed in snapshot payload. | `policy_hash` required; others optional | `policy_hash` must be 40/64 hex or base64 digest; if `observation_variant="infer"`, fall back to `features.systems.observations`. |
| `snapshot.migrations` | `handlers: dict[str, str]`, `auto_apply: bool`, `allow_minor: bool` | Map legacy `config_id` values to migration entrypoints; control auto-run behaviour. | `{}`, `False`, `False` | Keys must match legacy config IDs; values are import paths (`module:function`). Auto-apply toggles whether migrations run without operator confirmation. |
| `snapshot.guardrails` | `require_exact_config: bool`, `allow_downgrade: bool` | Express policy for mismatched `config_id` / schema loads. | `True`, `False` | If `require_exact_config` is `True`, migrations must be configured; `allow_downgrade` gates loading snapshots with newer schema. |

### Follow-Up Actions
- Add a `SnapshotConfig` Pydantic model to `src/townlet/config/loader.py` encapsulating the sections above; expose via `SimulationConfig.snapshot`.
- Wire config validation to ensure policy hash is provided for release configs; test fixture updates (`tests/test_config_loader.py`) will need sample values.
- Update project documentation (`docs/program_management/PROJECT_PLAN.md`, `docs/ops/OPS_HANDBOOK.md`) once the configuration changes are implemented to instruct operators on new knobs and promotion gates.

### Technical Design Reference
- Detailed technical design (schema deltas, migration flow, error taxonomy) captured in `docs/program_management/WP05_DESIGN_NOTE.md`.

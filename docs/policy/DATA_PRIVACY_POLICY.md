# Townlet Data & Privacy Policy

_Version: v0.1.0 — 2025-10-06_

_Owners:_ Security & Privacy Lead, Operations Lead  
_Reviewers:_ Program Manager, RL Lead, DevEx Lead

## Purpose
This document defines how Townlet collects, stores, processes, and deletes runtime data. It
extends the documentation roadmap commitment in `docs/program_management/DOCUMENTATION_PLAN.md`
and governs all telemetry, logs, training artefacts, and observational assets produced by the
Townlet platform.

## Scope
- Telemetry streams emitted by simulation shards, training harnesses, and promotion tooling.
- Console, watcher, and dashboard outputs written to disk or shared with operators.
- Snapshots, promotion bundles, golden rollouts, and auxiliary artefacts archived under
  `artifacts/`, `logs/`, or `tmp/`.
- Personally identifying information (PII) or pseudo-identifiers that may surface in agent labels,
  narration, or operator annotations.
- Processes operated by internal staff (engineering, ops, research, marketing) and sanctioned
  external reviewers. Third-party integrations remain out of scope for this revision.

## Data Inventory & Handling Controls
- **Runtime telemetry**
  - Contents: agent events, needs, reward breakdown, conflict stats, promotion metrics.
  - Source: `TelemetryPublisher` → NDJSON writers.
  - Storage: `logs/telemetry_*.jsonl` and optional TCP sinks.
  - Retention: 30 days raw, 180 days aggregated summaries.
  - Access: Ops, RL, DevEx.
  - Notes: privacy mode hashes agent IDs; streamer mode strips names before export.
- **Console & audit logs**
  - Contents: admin commands, results, issuer, `cmd_id`, errors.
  - Source: `townlet.console` audit logger.
  - Storage: `logs/console/*.jsonl`.
  - Retention: 90 days.
  - Access: Ops, Security.
  - Notes: admin mode requires tokens; CI enforces rotation.
- **Watcher & summary artefacts**
  - Contents: alert snapshots, KPI summaries, markdown digests.
  - Source: `scripts/telemetry_watch.py`, `telemetry_summary.py`.
  - Storage: `artifacts/phase*/` and operator workspaces.
  - Retention: 90 days.
  - Access: Ops, Program Mgmt.
  - Notes: enable privacy mode before sharing externally.
- **Promotion bundles**
  - Contents: BC/anneal metrics, promotion decisions, watcher output.
  - Source: `scripts/promotion_evaluate.py`, CI workflows.
  - Storage: `artifacts/m7/` bundle directories.
  - Retention: 180 days.
  - Access: Ops, RL, Program Mgmt.
  - Notes: contains policy hashes; treat as confidential release history.
- **Training logs**
  - Contents: PPO/BC NDJSON, checkpoints, replay manifests.
  - Source: `scripts/run_training.py`.
  - Storage: `logs/ppo_*.jsonl`, `artifacts/training/`.
  - Retention: 90 days (checkpoints 30 days unless promotion requires longer).
  - Access: RL, Ops.
  - Notes: purge replay manifests once promotion closes.
- **Snapshots & configs**
  - Contents: simulation snapshots, config YAML, migration metadata.
  - Source: `SnapshotManager`, console exports.
  - Storage: `artifacts/snapshots/`.
  - Retention: 180 days.
  - Access: Engineering, Ops.
  - Notes: tag with `config_id`; purge superseded versions after migration confirmation.
- **Observation samples**
  - Contents: tensor dumps, social snippets, golden fixtures.
  - Source: test harnesses and capture scripts.
  - Storage: `tests/data/`, `docs/samples/`, `tmp/rollout_goldens/`.
  - Retention: keep goldens indefinitely; temp data 30 days.
  - Access: Engineering, QA.
  - Notes: privacy mode must redact agent names before publishing external fixtures.
- **Observer UI captures**
  - Contents: GIFs, transcripts, usability artefacts.
  - Source: `scripts/observer_ui.py` and demo tooling.
  - Storage: `docs/samples/observer_*`.
  - Retention: 30 days unless re-approved.
  - Access: Product, Marketing, Ops.
  - Notes: run in privacy or streamer mode before distribution.

## Access Controls
- **Role separation:** Viewer mode exposes read-only console commands; admin endpoints require
  bearer tokens issued by operations. Tokens scoped per environment and rotated quarterly.
- **Authentication audit:** Every admin command writes audit records with issuer and `cmd_id`. CI
  verifies audit log rotation and file permissions on each release branch.
- **Data at rest:** Artefact directories inherit restrictive permissions (`chmod 750`) in official
  environments. Promotion bundles stored in enclave storage with access logged by ops.
- **Data in transit:** Telemetry transports default to TLS when using TCP endpoints. File and stdout
  transports remain local to the shard host.

## Privacy Features
- **Privacy mode:** When enabled, agent identifiers are hashed and narrator output swaps to neutral
  descriptors. Console, watcher, and telemetry payloads honour the hashed IDs.
- **Streamer mode:** Optional CLI flag for observer tooling that redacts agent names and personal
  narrative beats; intended for demo streams.
- **Redaction hooks:** Telemetry publisher exposes `redact_personal_identifiers` helper used by
  console snapshots, watcher summaries, and documentation capture scripts.
- **Consent boundaries:** Operator annotations or free-form notes must avoid real person data. Any
  dataset containing real user info triggers incident response (see below).

## Retention & Deletion
- Apply retention windows listed in the inventory table. Ops automates log pruning via nightly cron
  jobs; engineering ensures CI artefacts older than 30 days are removed from shared runners.
- When promotion bundles supersede prior releases, archive the outgoing bundle in cold storage for
  180 days, then purge after compliance review.
- On request from Security/Privacy, perform ad-hoc deletion: locate artefacts via `scripts/audit_*`
  utilities, confirm SHA before removal, then record in `docs/program_management/APPROVAL_LOG.md`.

## Data Subject & Compliance Considerations
- Townlet uses synthetic agents; nonetheless, treat agent IDs and narration as pseudo-identifiers.
- External demos must run in privacy or streamer mode to avoid leaking internal labels.
- Prior to public release, marketing assets undergo Privacy review to confirm redaction and that no
  operator notes remain in captures.
- This policy aligns with internal compliance guidelines (ISO-style control families); use it as the
  baseline when engaging actual user telemetry in future phases.

## Incident Response
1. **Detection:** Alerts from monitoring, operator reports, or CI log scans flag possible privacy
   breaches.
2. **Containment:** Disable external exports, rotate tokens, and enable privacy mode if not already
   active.
3. **Assessment:** Security/Privacy lead audits affected artefacts, classifies data exposure, and
   identifies impacted stakeholders.
4. **Remediation:** Purge offending artefacts, patch redaction gaps, and update telemetry/console
   code paths if needed.
5. **Reporting:** Document incident summary, root cause, and corrective actions in
   `docs/program_management/APPROVAL_LOG.md` and incident tracker; share with program management.

## Change Management
- Version this policy with semantic tags. Increment the version when scope or retention windows
  change, and note updates in the approval log.
- Schedule quarterly reviews alongside milestone checkpoints (M7–M9) to ensure privacy controls
  follow new telemetry fields or observer features.
- Pull requests updating this policy must tag the owners listed above for review and sign-off.

## References
- `docs/program_management/DOCUMENTATION_PLAN.md`
- `docs/program_management/MASTER_PLAN_PROGRESS.md`
- `docs/ops/OPS_HANDBOOK.md`
- `docs/program_management/snapshots/ARCHITECTURE_INTERFACES.md`

# Risk Register

## R-01: Unauthenticated Console & Telemetry Access
- **Likelihood**: High
- **Impact**: Critical
- **Mitigation Strategy**: Implement WP-001 (authn/authz, token management) and enforce secure transport (WP-003).
- **Owner Recommendation**: Simulation Platform Lead
- **Monitoring**: Add authentication audit logs, failed login counters, and include console access checks in CI smoke tests. Review quarterly.

## R-02: Snapshot Path Traversal & Data Exfiltration
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation Strategy**: Ship WP-002 to restrict file access to configured snapshot roots; add read-only viewer mode.
- **Owner Recommendation**: Security Champion / Simulation Platform
- **Monitoring**: Log all snapshot path requests, alert on attempts outside allowlist. Conduct quarterly penetration testing.

## R-03: Plaintext Telemetry Transport
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation Strategy**: Deliver WP-003 to add TLS and client authentication; disable plaintext TCP in production configs.
- **Owner Recommendation**: Infrastructure Engineering
- **Monitoring**: TLS certificate expiry alerts, telemetry channel health dashboards. Review during release readiness.

## R-04: Telemetry Flush Blocking Simulation
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation Strategy**: Execute WP-004 (async flushing) and implement observability via WP-007.
- **Owner Recommendation**: Core Simulation Team
- **Monitoring**: Track tick duration metrics, enqueue depth, and flush latency. Add alert for sustained flush failures.

## R-05: High Telemetry Payload Volume
- **Likelihood**: High
- **Impact**: Medium
- **Mitigation Strategy**: Complete WP-005 to reduce payload size and adopt diff streaming.
- **Owner Recommendation**: Telemetry/Insights Team
- **Monitoring**: Measure payload size trend, drop counts, and transport bandwidth. Review after each release.

## R-06: Mutable World Snapshots Causing State Corruption
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation Strategy**: Apply WP-006 to return immutable copies and expand regression tests.
- **Owner Recommendation**: Simulation Platform Lead
- **Monitoring**: Add tests for external mutation attempts; observe anomaly reports from QA. Reassess bi-monthly.

## R-07: Lack of Containerised Deployment Path
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation Strategy**: Deliver WP-008 to produce Docker images, compose manifests, and deployment runbooks.
- **Owner Recommendation**: DevOps / Release Engineering
- **Monitoring**: Track environment drift incidents, ensure images built on every release. Review per milestone.

## R-08: Incomplete Training & Promotion Pipeline
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation Strategy**: Execute WP-009 and WP-010 to finish training orchestration and resolve scaffolding debt.
- **Owner Recommendation**: Applied RL Team Lead
- **Monitoring**: Monitor promotion cadence, evaluation metrics, and backlog burndown. Review after each promotion rehearsal.

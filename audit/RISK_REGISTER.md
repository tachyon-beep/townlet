# Risk Register

## R-101: Unauthenticated Console / Admin Commands
- **Likelihood**: High
- **Impact**: Critical
- **Mitigation Strategy**: Deliver WP-101 (authn/authz) and ensure TLS transport via WP-102.
- **Owner Recommendation**: Simulation Platform Lead
- **Monitoring**: Track failed auth counters, review access logs weekly, include auth smoke test in CI.

## R-102: Plaintext Telemetry Channel Exposure
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation Strategy**: Implement WP-102 to add TLS and peer validation; disable plaintext TCP in production configs.
- **Owner Recommendation**: Infrastructure / DevOps
- **Monitoring**: Certificate expiry alerts, TLS handshake metrics, quarterly penetration tests.

## R-103: Silent Telemetry Payload Loss
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation Strategy**: Ship WP-103 and WP-108 to expose drop metrics, alerts, and structured logs; profile via WP-109.
- **Owner Recommendation**: Telemetry & Insights Team
- **Monitoring**: Dashboard on queue depth/drops, alert when drops >0 for 5 consecutive minutes, regression tests in CI.

## R-104: WorldState Monolith Inhibits Safe Change
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation Strategy**: Split responsibilities through WP-104 and close TODO hooks via WP-106 while adding profiling from WP-109.
- **Owner Recommendation**: Core Simulation Team
- **Monitoring**: Module size KPI, change failure rate, architecture review before large features.

## R-105: Missing Compact Observation Variant Breaks Feature Flag
- **Likelihood**: High
- **Impact**: Medium
- **Mitigation Strategy**: Complete WP-105 to deliver compact tensors and regression tests.
- **Owner Recommendation**: Applied RL Team
- **Monitoring**: Test coverage for compact variant, config smoke tests in CI, backlog review after delivery.

## R-106: No Containerised Deployment Path
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation Strategy**: Introduce Docker/Compose assets via WP-107 and document operational steps.
- **Owner Recommendation**: Release Engineering
- **Monitoring**: Track environment drift incidents, ensure container build runs per release, quarterly ops drills.

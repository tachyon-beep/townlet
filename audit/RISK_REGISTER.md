# Risk Register

## R-001: Unauthenticated Admin Console Access
- **Category**: Security
- **Likelihood**: High (default config disables auth)
- **Impact**: Critical
- **Current Controls**: Optional token-based auth; disabled by default.
- **Mitigation Strategy**: Implement WP-301 to enforce viewer mode when auth disabled and require tokens for admin actions.
- **Risk Owner Recommendation**: Platform engineering / gameplay operations.
- **Monitoring & Review**: Add CI check ensuring configs shipped in `configs/` keep auth enabled; surface warning logs during startup.

## R-002: Plaintext Telemetry Exposure
- **Category**: Security
- **Likelihood**: Medium (TLS requires deliberate configuration, TCP currently nudges operators toward allow_plaintext)
- **Impact**: High
- **Current Controls**: Warning log when plaintext TCP is enabled.
- **Mitigation Strategy**: Deliver WP-302 and WP-308 to make TLS the default and document certificate handling.
- **Risk Owner Recommendation**: Telemetry/infrastructure team.
- **Monitoring & Review**: Audit deployment configs for `allow_plaintext=true`; add runtime telemetry flag exposing TLS status via `export_state()`.

## R-003: Telemetry Flush Thread Failure
- **Category**: Operational
- **Likelihood**: Medium
- **Impact**: High
- **Current Controls**: None; failures silently terminate the daemon thread.
- **Mitigation Strategy**: Execute WP-303 and WP-304 to wrap the worker with exception handling and propagate health state.
- **Risk Owner Recommendation**: Observability lead.
- **Monitoring & Review**: Emit heartbeat metrics (queue length, worker_alive) and alert when stale.

## R-004: WorldState Scalability Limits
- **Category**: Performance
- **Likelihood**: High (O(n²) neighbourhood scans)
- **Impact**: High
- **Current Controls**: Manual profiling notes in `docs/engineering/WORLDSTATE_REFACTOR.md`.
- **Mitigation Strategy**: Complete WP-305 and WP-306 to introduce spatial indexing and modularise responsibilities.
- **Risk Owner Recommendation**: Simulation core team.
- **Monitoring & Review**: Track tick duration percentiles and agent counts; add perf regressions to CI once indexing lands.

## R-005: Compact Observation Stub Blocks Experiments
- **Category**: Enhancement
- **Likelihood**: High (compact mode currently unusable)
- **Impact**: Medium
- **Current Controls**: Tests skip compact verification by using zero tensors.
- **Mitigation Strategy**: Implement WP-309.
- **Risk Owner Recommendation**: RL research / training team.
- **Monitoring & Review**: Add scenario smoke tests using compact variant after implementation.

## R-006: Low API Documentation Coverage
- **Category**: Best Practice
- **Likelihood**: Medium
- **Impact**: Medium
- **Current Controls**: High-level docs; no automated checks.
- **Mitigation Strategy**: Deliver WP-307 to raise docstring coverage and add tooling.
- **Risk Owner Recommendation**: Developer experience / documentation owner.
- **Monitoring & Review**: Introduce docstring coverage badge or CI threshold.

## R-007: Affordance Outcome Metadata Loss
- **Category**: Technical Debt
- **Likelihood**: Medium
- **Impact**: Medium
- **Current Controls**: Partial metadata appended to inventory list.
- **Mitigation Strategy**: Execute WP-310.
- **Risk Owner Recommendation**: Gameplay systems team.
- **Monitoring & Review**: Telemetry validation to ensure richer metadata persists after rollout.


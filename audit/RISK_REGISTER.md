# Risk Register

| ID | Risk Description | Likelihood | Impact | Mitigation Strategy | Owner | Monitoring |
| --- | --- | --- | --- | --- | --- | --- |
| R-01 | Simulation CLI does not advance ticks, blocking smoke tests and operations. | High | High | Implement WP-001 to fix iteration and add regression tests. | Simulation Platform Lead | Add CLI smoke test to CI; review after each release. |
| R-02 | Dynamic affordance hook imports allow arbitrary code execution via environment variables. | Medium | High | Ship WP-002 to restrict imports to trusted namespaces. | Gameplay Systems Lead | Security review of hook configuration; audit environment variables in deployment scripts quarterly. |
| R-03 | Telemetry TCP transport sends plaintext data (no TLS/auth), exposing sensitive metrics and console output. | Medium | High | Deliver WP-003 to add TLS/auth support and warn on plaintext. | Infrastructure/DevOps | Telemetry deployment checklist; monitor transport configuration in staging/prod. |
| R-04 | Observation/local view logic scales O(n²); larger agent counts will cause severe slowdown. | Medium | Medium | Execute WP-005 to introduce cached spatial indices and profiling. | Simulation Platform Lead | Add performance benchmarks to CI and track telemetry tick duration. |
| R-05 | Dependencies have only lower bounds; upstream releases can break builds unpredictably. | High | Medium | Complete WP-007 to introduce lock/constraints files and document upgrade cadence. | Build/Tooling Owner | Include dependency audit in release checklist; quarterly freshness review. |
| R-06 | Lack of integration tests for CLI and telemetry flush worker risks regression reoccurrence. | Medium | Medium | Implement WP-004 and WP-010 to add regression tests and health metrics. | QA Lead | CI dashboards; monitor telemetry health payloads for worker liveness. |

# Quick Wins (High Impact, < 1 Day)

1. **Iterate Simulation Loop in CLI (WP-001)**  
   - Update `scripts/run_simulation.py` to loop over `SimulationLoop.run()` and emit a simple smoke test.  
   - Restores core workflow immediately; estimated effort <2 hours.

2. **Document Telemetry TCP Insecurity**  
   - Add a prominent warning in `docs/ops` and README noting that TCP transport is plaintext and should not be used in untrusted networks until WP-003 lands.  
   - Mitigates risk while engineering secure transport; effort ~1 hour.

3. **Deduplicate Affordance Outcome Trimming (WP-009)**  
   - Remove duplicated log trimming lines and include affordance/object IDs in metadata.  
   - Improves debugging fidelity; effort <2 hours.

4. **Add CLI Smoke Test to CI (WP-004 subset)**  
   - Create a lightweight pytest invoking `run_simulation.main()` for a few ticks to guard future regressions.  
   - Provides immediate regression coverage; effort ~2 hours.

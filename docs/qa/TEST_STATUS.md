# Test Status — Post-LR1 (2025-10-06)

Full repository test run (`pytest`) completes without failures:

- 325 passed, 1 skipped (`tests/test_policy_models.py`) in 14.47s.
- Skip reason: torch-dependent model suite; run torch-specific coverage separately when GPU runtimes are available.

No other pytest targets are currently failing, so no deferrals or xfails are required.

Keep this file updated whenever tests are deliberately deferred or temporarily skipped so CI reflects the active scope only.

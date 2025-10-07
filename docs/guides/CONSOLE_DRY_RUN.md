# Console Dry Run — Employment Loop Controls (2025-09-25)

## Objectives
- Validate employment console commands (`telemetry_snapshot`, `employment_status`, `employment_exit review/approve/defer`) end-to-end against a live simulation shard.
- Verify schema-version warnings appear when expected.
- Capture operator-facing checklist for incident response (employment backlog).

## Scenario Setup
- Config: `configs/examples/poc_hybrid.yaml` (employment flag enabled).
- Enable console auth for the session:
  ```python
  from townlet.config import ConsoleAuthConfig, ConsoleAuthTokenConfig
  config = config.model_copy(
      update={
          "console_auth": ConsoleAuthConfig(
              enabled=True,
              require_auth_for_viewer=False,
              tokens=[
                  ConsoleAuthTokenConfig(token="viewer-token", role="viewer"),
                  ConsoleAuthTokenConfig(token="admin-token", role="admin"),
              ],
          )
      }
  )
  ```
- Commands executed via Python harness (simulating Typer CLI integration until CLI ships).
- Run `source .venv/bin/activate && PYTHONPATH=src python scripts/console_dry_run.py` (script below) or follow manual steps.
- If the `[ml]` or `[api]` extras are missing, the script logs stub-policy or stub-telemetry warnings; commands that require those capabilities will be skipped safely.
- For a headless check before launching the dashboard, run `python scripts/run_simulation.py configs/examples/poc_hybrid.yaml --ticks 50`. Telemetry is muted by default; add `--stream-telemetry` to mirror payloads on stdout or `--telemetry-path out.jsonl` to capture them for later inspection.

## Manual Command Script (Python)
```python
from pathlib import Path
from townlet.config import load_config
from townlet.console.handlers import ConsoleCommand, create_console_router
from townlet.core.sim_loop import SimulationLoop
from townlet.core.utils import policy_provider_name, telemetry_provider_name

config = load_config(Path("configs/examples/poc_hybrid.yaml"))
config.employment.enforce_job_loop = True
loop = SimulationLoop(config)
world = loop.world
router = create_console_router(
    loop.telemetry,
    world,
    policy=loop.policy,
    policy_provider=policy_provider_name(loop),
    telemetry_provider=telemetry_provider_name(loop),
    config=config,
)

# Step 1: Prime agents and advance sim.
for _ in range(20):
    loop.step()
print(router.dispatch(ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={})))

# Step 2: Enqueue employment exits.
world.employment.enqueue_exit(world, "agent_0", world.tick)
print(router.dispatch(ConsoleCommand(name="employment_exit", args=("review",), kwargs={})))
print(router.dispatch(ConsoleCommand(name="employment_exit", args=("approve", "agent_0"), kwargs={})))
print(router.dispatch(ConsoleCommand(name="employment_exit", args=("defer", "agent_0"), kwargs={})))
print(router.dispatch(ConsoleCommand(name="employment_status", args=(), kwargs={})))

print("=== latest console_results ===")
print(loop.telemetry.latest_console_results())

print("=== console audit tail ===")
audit_path = Path("logs/console/commands.jsonl")
if audit_path.exists():
    print(audit_path.read_text().splitlines()[-1])
else:
    print("(console audit log not found; ensure log directory exists)")

print("=== force_chat agent_0->agent_1 ===")
payload = {
    "name": "force_chat",
    "mode": "admin",
    "cmd_id": "chat-demo",
    "auth": {"token": "admin-token"},
    "kwargs": {
        "payload": {
            "speaker": "agent_0",
            "listener": "agent_1",
            "quality": 0.75,
        }
    },
}
loop.telemetry.queue_console_command(payload)
loop.step()
print(loop.telemetry.latest_console_results()[-1])

# Tip: In automated tests you can advance the simulation with
# `SimulationLoop.run_for_ticks(n)`, which optionally collects per-tick
# `TickArtifacts` for assertions while keeping the API consistent with the
# CLI helpers.
```

## Checklist
- [x] `telemetry_snapshot` payload includes employment metrics and `schema_version`.
- [x] `employment_exit review` shows pending queue entry after manual enqueue.
- [x] `employment_exit approve` marks agent for manual exit (check `employment_status` reflects pending manual exit or removal).
- [x] `employment_exit defer` clears queue entry.
- [x] No schema warning emitted when shard version matches console support.
- [x] `console_results` reports command outcomes for the latest tick.
- [x] `logs/console/commands.jsonl` appended an entry matching the last command `cmd_id`.
- [x] `force_chat` response shows updated relationship ties for both agents.

## Observations
- Employment queue cleared successfully; manual approve triggered immediate lifecycle exit next evaluation tick.
- `employment_status` reflected zero pending entries post-defer, matching expectations.
- No schema mismatch warnings (shard version `0.2.0`).

## Follow-up
- Record dry-run completion in `docs/engineering/IMPLEMENTATION_NOTES.md`.
- Mark Risk R5 mitigated in work-package register.
- Once Typer CLI lands, port this script into an automated CLI test harness.

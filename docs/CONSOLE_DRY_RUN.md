# Console Dry Run — Employment Loop Controls (2025-09-25)

## Objectives
- Validate employment console commands (`telemetry_snapshot`, `employment_status`, `employment_exit review/approve/defer`) end-to-end against a live simulation shard.
- Verify schema-version warnings appear when expected.
- Capture operator-facing checklist for incident response (employment backlog).

## Scenario Setup
- Config: `configs/examples/poc_hybrid.yaml` (employment flag enabled).
- Commands executed via Python harness (simulating Typer CLI integration until CLI ships).
- Run `source .venv/bin/activate && PYTHONPATH=src python scripts/console_dry_run.py` (script below) or follow manual steps.

## Manual Command Script (Python)
```python
from pathlib import Path
from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.console.handlers import ConsoleCommand, create_console_router

config = load_config(Path("configs/examples/poc_hybrid.yaml"))
config.employment.enforce_job_loop = True
loop = SimulationLoop(config)
world = loop.world
router = create_console_router(loop.telemetry, world)

# Step 1: Prime agents and advance sim.
for _ in range(20):
    loop.step()
print(router.dispatch(ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={})))

# Step 2: Enqueue employment exits.
world._employment_enqueue_exit("agent_0", world.tick)
print(router.dispatch(ConsoleCommand(name="employment_exit", args=("review",), kwargs={})))
print(router.dispatch(ConsoleCommand(name="employment_exit", args=("approve", "agent_0"), kwargs={})))
print(router.dispatch(ConsoleCommand(name="employment_exit", args=("defer", "agent_0"), kwargs={})))
print(router.dispatch(ConsoleCommand(name="employment_status", args=(), kwargs={})))
```

## Checklist
- [x] `telemetry_snapshot` payload includes employment metrics and `schema_version`.
- [x] `employment_exit review` shows pending queue entry after manual enqueue.
- [x] `employment_exit approve` marks agent for manual exit (check `employment_status` reflects pending manual exit or removal).
- [x] `employment_exit defer` clears queue entry.
- [x] No schema warning emitted when shard version matches console support.

## Observations
- Employment queue cleared successfully; manual approve triggered immediate lifecycle exit next evaluation tick.
- `employment_status` reflected zero pending entries post-defer, matching expectations.
- No schema mismatch warnings (shard version `0.2.0`).

## Follow-up
- Record dry-run completion in `docs/IMPLEMENTATION_NOTES.md`.
- Mark Risk R5 mitigated in work-package register.
- Once Typer CLI lands, port this script into an automated CLI test harness.

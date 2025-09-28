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
router = create_console_router(loop.telemetry, world, policy=loop.policy, config=config)

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

print("=== latest console_results ===")
print(loop.telemetry.latest_console_results())

print("=== console audit tail ===")
audit_path = Path("logs/console/commands.jsonl")
if audit_path.exists():
    print(audit_path.read_text().splitlines()[-1])
else:
    print("(console audit log not found; ensure log directory exists)")

print("=== force_chat agent_0->agent_1 ===")
loop.telemetry.queue_console_command(
    {
        "name": "force_chat",
        "mode": "admin",
        "cmd_id": "chat-demo",
        "kwargs": {
            "payload": {
                "speaker": "agent_0",
                "listener": "agent_1",
                "quality": 0.75,
            }
        },
    }
)
loop.step()
print(loop.telemetry.latest_console_results()[-1])
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

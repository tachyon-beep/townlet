from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world.grid import AgentSnapshot


def make_loop_with_employment() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.employment.enforce_job_loop = True
    config.employment.grace_ticks = 0
    config.employment.absent_cutoff = 10
    config.employment.absence_slack = 3
    config.employment.late_tick_penalty = 0.0
    for job in config.jobs.values():
        job.start_tick = 5
        job.end_tick = 7
        job.location = (0, 0)
    config.behavior.job_arrival_buffer = 0
    loop = SimulationLoop(config)
    world = loop.world
    world.agents.clear()
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(5, 5),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    world._assign_jobs_to_agents()  # type: ignore[attr-defined]
    return loop


def advance_ticks(loop: SimulationLoop, ticks: int) -> None:
    for _ in range(ticks):
        loop.step()


def test_on_time_shift_records_attendance() -> None:
    loop = make_loop_with_employment()
    world = loop.world

    # Run through the shift and a post-shift tick.
    advance_ticks(loop, 10)

    alice = world.agents["alice"]
    assert alice.shift_state == "post_shift"
    assert alice.attendance_ratio == pytest.approx(1.0)
    assert alice.late_ticks_today == 0
    assert alice.wages_withheld == 0
    assert alice.job_id is not None
    job = loop.config.jobs[alice.job_id]
    expected_ticks = job.end_tick - job.start_tick + 1
    assert alice.inventory.get("wages_earned", 0) == expected_ticks


def test_late_arrival_accumulates_wages_withheld() -> None:
    loop = make_loop_with_employment()
    world = loop.world
    assert world.agents["bob"].job_id is not None
    job = loop.config.jobs[world.agents["bob"].job_id]
    # Keep Bob away past shift start then move him to the job location.
    advance_ticks(loop, 6)
    world.agents["bob"].position = (0, 0)
    advance_ticks(loop, 6)

    bob = world.agents["bob"]
    assert bob.shift_state == "post_shift"
    assert bob.attendance_ratio < 1.0
    assert bob.late_ticks_today > 0
    assert bob.wages_withheld > 0
    assert bob.inventory.get("wages_earned", 0) < (job.end_tick - job.start_tick + 1)


def test_employment_exit_queue_respects_cap_and_manual_override() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.employment.enforce_job_loop = True
    config.employment.daily_exit_cap = 1
    config.employment.exit_review_window = 10
    config.employment.max_absent_shifts = 1
    loop = SimulationLoop(config)
    world = loop.world
    world.agents.clear()
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 1.0},
        wallet=1.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(0, 0),
        needs={"hunger": 1.0},
        wallet=1.0,
    )
    world._assign_jobs_to_agents()  # type: ignore[attr-defined]
    world.agents["alice"].absent_shifts_7d = 1
    world.agents["bob"].absent_shifts_7d = 1

    terminated = loop.lifecycle.evaluate(world, tick=0)
    assert terminated.get("alice") is True
    assert terminated.get("bob") is False
    if terminated.get("alice"):
        world.agents.pop("alice")
    assert world.employment_queue_snapshot()["pending_count"] == 1

    # Manual approval should bypass the daily cap.
    assert world.employment_request_manual_exit("bob", tick=0)
    manual = loop.lifecycle.evaluate(world, tick=1)
    assert manual.get("bob") is True
    if manual.get("bob"):
        world.agents.pop("bob")
    assert world.employment_queue_snapshot()["pending_count"] == 0

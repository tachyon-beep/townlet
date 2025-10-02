from __future__ import annotations

from pathlib import Path

import pytest

from scripts.telemetry_watch import (
    _parse_health_line,
    check_health_thresholds,
    stream_health_records,
)


def test_parse_health_line() -> None:
    line = (
        "tick_health tick=12 duration_ms=6.5 queue=2 dropped=0 "
        "perturbations_pending=1 perturbations_active=0 exit_queue=3"
    )
    record = _parse_health_line(line)
    assert record["tick"] == 12
    assert record["duration_ms"] == pytest.approx(6.5)
    assert record["queue"] == 2
    assert record["telemetry_queue"] == 2
    assert record["exit_queue"] == 3


def test_stream_health_records(tmp_path: Path) -> None:
    log = tmp_path / "health.log"
    log.write_text(
        "tick_health tick=5 duration_ms=4.2 queue=1 dropped=0 perturbations_pending=0 "
        "perturbations_active=0 exit_queue=0\n",
        encoding="utf-8",
    )
    records = list(stream_health_records(log, follow=False, interval=0.01))
    assert len(records) == 1
    assert records[0]["tick"] == 5


def test_health_thresholds_raise() -> None:
    record = {
        "tick": 7,
        "duration_ms": 12.0,
        "queue": 3.0,
        "telemetry_queue": 3.0,
        "dropped": 0.0,
        "telemetry_dropped": 0.0,
        "perturbations_pending": 1.0,
        "perturbations_active": 0.0,
        "exit_queue": 0.0,
    }
    args = type(
        "Args",
        (),
        {
            "tick_duration_max": 10.0,
            "telemetry_queue_max": None,
            "telemetry_dropped_max": None,
            "perturbations_pending_max": None,
            "perturbations_active_max": None,
            "exit_queue_max": None,
        },
    )()
    with pytest.raises(SystemExit):
        check_health_thresholds(record, args)

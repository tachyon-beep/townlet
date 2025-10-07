from __future__ import annotations

import importlib
from pathlib import Path

FORBIDDEN = {
    "queue_console",
    "drain_console_buffer",
    "flush_transitions",
    "active_policy_hash",
    "publish_tick",
    "record_loop_failure",
    "close",
}


def test_ports_do_not_expose_forbidden_symbols() -> None:
    for module_name in (
        "townlet.ports.world",
        "townlet.ports.policy",
        "townlet.ports.telemetry",
    ):
        module = importlib.import_module(module_name)
        source = Path(module.__file__).read_text(encoding="utf-8")
        for forbidden in FORBIDDEN:
            assert forbidden not in source, f"{module_name} leaks forbidden API '{forbidden}'"

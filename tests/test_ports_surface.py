from __future__ import annotations

import importlib
import pathlib

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
    modules = (
        "townlet.ports.world",
        "townlet.ports.policy",
        "townlet.ports.telemetry",
    )
    for module_name in modules:
        module = importlib.import_module(module_name)
        source = pathlib.Path(module.__file__).read_text(encoding="utf-8")
        for symbol in FORBIDDEN:
            assert symbol not in source, f"{module_name} leaks forbidden symbol {symbol}"

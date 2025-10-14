from __future__ import annotations

from copy import deepcopy
from typing import Any

BASE_GLOBAL_CONTEXT: dict[str, Any] = {
    "queue_metrics": {
        "cooldown_events": 0,
        "ghost_step_events": 0,
        "rotation_events": 0,
    },
    "queues": {},
    "employment_snapshot": {},
    "job_snapshot": {},
    "economy_snapshot": {},
    "economy_settings": {},
    "price_spikes": {},
    "utilities": {"power": True, "water": True},
    "relationship_snapshot": {},
    "relationship_metrics": {},
    "relationship_updates": [],
    "queue_affinity_metrics": {},
    "running_affordances": {},
    "stability_metrics": {},
    "promotion_state": {},
    "anneal_context": {},
    "perturbations": {},
}


def build_global_context(**sections: Any) -> dict[str, Any]:
    """Return a DTO global_context payload seeded with base defaults."""

    context = deepcopy(BASE_GLOBAL_CONTEXT)
    for key, value in sections.items():
        if value is None:
            continue
        context[key] = deepcopy(value)
    return context


from townlet_ui.telemetry import TelemetryClient


def test_telemetry_client_parses_agent_needs_and_perturbations() -> None:
    client = TelemetryClient(history_window=2)
    payload = {
        "schema_version": "0.9.7",
        "employment": {
            "pending": [],
            "pending_count": 0,
            "exits_today": 0,
            "daily_exit_cap": 2,
            "queue_limit": 8,
            "review_window": 1440,
        },
        "jobs": {
            "alice": {
                "wallet": 1.5,
                "shift_state": "on_time",
                "attendance_ratio": 0.8,
                "wages_withheld": 0.0,
                "lateness_counter": 0,
                "on_shift": True,
                "job_id": "bakery",
                "exit_pending": False,
                "late_ticks_today": 0,
                "meals_cooked": 3,
                "meals_consumed": 1,
                "basket_cost": 0.42,
                "needs": {"hunger": 0.6, "hygiene": 0.7, "energy": 0.5},
            }
        },
        "conflict": {
            "queues": {
                "cooldown_events": 0,
                "ghost_step_events": 0,
                "rotation_events": 0,
            },
            "queue_history": [],
            "rivalry": {},
            "rivalry_events": [],
        },
        "relationships": {},
        "relationship_snapshot": {},
        "relationship_updates": [],
        "relationship_overlay": {},
        "anneal_status": {},
        "policy_snapshot": {},
        "promotion": {},
        "stability": {"alerts": [], "metrics": {}},
        "kpi_history": {},
        "transport": {
            "connected": True,
            "dropped_messages": 0,
            "queue_length": 0,
        },
        "health": None,
        "economy_settings": {},
        "price_spikes": {},
        "utilities": {},
        "affordance_runtime": {},
        "narrations": [],
        "narration_state": {},
        "social_events": [],
        "relationship_summary": {},
        "perturbations": {
            "active": {
                "ps-1": {
                    "spec": "price_spike",
                    "ticks_remaining": 30,
                }
            },
            "pending": [
                {
                    "event_id": "outage-1",
                    "spec": "utility_outage",
                    "starts_in": 60,
                }
            ],
            "cooldowns": {
                "spec": {"price_spike": 120},
                "agents": {"alice": {"price_spike": 60}},
            },
        },
        "history": {
            "needs": {
                "alice": {
                    "hunger": [0.1, 0.2, 0.3],
                    "energy": [0.5, 0.6, 0.7],
                }
            },
            "wallet": {"alice": [1.0, 1.2, 1.4]},
            "rivalry": {"alice|bob": [0.1, 0.2, 0.15]},
        },
    }

    snapshot = client.parse_snapshot(payload)
    assert snapshot.agents[0].needs == {
        "hunger": 0.6,
        "hygiene": 0.7,
        "energy": 0.5,
    }
    assert "ps-1" in snapshot.perturbations.active
    assert snapshot.perturbations.pending[0]["event_id"] == "outage-1"
    assert snapshot.perturbations.cooldowns_spec["price_spike"] == 120
    assert snapshot.history is not None
    history = snapshot.history
    needs_history = history.needs["alice"]
    assert needs_history["hunger"] == (0.2, 0.3)
    assert history.wallet["alice"] == (1.2, 1.4)
    rivalry_history = history.rivalry["alice"]["bob"]
    assert rivalry_history == (0.2, 0.15)

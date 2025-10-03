from pathlib import Path

from townlet.config import (
    PerturbationKind,
    PerturbationSchedulerConfig,
    PriceSpikeEventConfig,
    SimulationConfig,
    load_config,
)


def test_simulation_config_exposes_perturbations() -> None:
    config_path = Path("configs/examples/poc_hybrid.yaml")
    if not config_path.exists():
        return
    config: SimulationConfig = load_config(config_path)
    scheduler = config.perturbations
    assert scheduler.max_concurrent_events >= 1
    assert scheduler.events == {}


def test_price_spike_event_config_parses_ranges() -> None:
    cfg = PerturbationSchedulerConfig(
        events={
            "price_spike": {
                "kind": PerturbationKind.PRICE_SPIKE,
                "prob_per_day": 0.3,
                "cooldown_ticks": 120,
                "duration": [30, 90],
                "magnitude": [1.1, 1.6],
            }
        }
    )
    assert "price_spike" in cfg.events
    event = cfg.events["price_spike"]
    assert isinstance(event, PriceSpikeEventConfig)
    assert event.duration.min == 30 and event.duration.max == 90
    assert event.magnitude.min == 1.1 and event.magnitude.max == 1.6

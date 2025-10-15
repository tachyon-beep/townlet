"""Stability analyzers - modular components for monitoring simulation health.

DESIGN#3.1: Analyzer Extraction (WP5 Phase 3.1)

Each analyzer implements the StabilityAnalyzer protocol and focuses on
a specific aspect of simulation stability:

- FairnessAnalyzer: Queue conflict and fairness pressure detection
- RivalryTracker: High-intensity rivalry event spikes
- RewardVarianceAnalyzer: Reward distribution variance tracking
- OptionThrashDetector: Option switching rate monitoring
- StarvationDetector: Sustained hunger incident tracking

All analyzers support:
- analyze(): Compute metrics from world state
- check_alert(): Determine if alert threshold exceeded
- reset(): Clear state for new simulation
- export_state(): Serialize state for snapshots
- import_state(): Restore state from snapshots
"""

from __future__ import annotations

from townlet.stability.analyzers.base import NullAnalyzer, StabilityAnalyzer
from townlet.stability.analyzers.fairness import FairnessAnalyzer
from townlet.stability.analyzers.option_thrash import OptionThrashDetector
from townlet.stability.analyzers.reward_variance import RewardVarianceAnalyzer
from townlet.stability.analyzers.rivalry import RivalryTracker
from townlet.stability.analyzers.starvation import StarvationDetector

__all__ = [
    "StabilityAnalyzer",
    "NullAnalyzer",
    "FairnessAnalyzer",
    "RivalryTracker",
    "RewardVarianceAnalyzer",
    "OptionThrashDetector",
    "StarvationDetector",
]

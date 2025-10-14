"""Promotion service adapter (torch-free).

This service wraps the PromotionManager and provides helpers for tracking
promotion evaluation results. All operations are torch-free.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from townlet.config import SimulationConfig
    from townlet.stability.promotion import PromotionManager


class PromotionServiceAdapter:
    """Torch-free promotion tracking service.

    Wraps PromotionManager and provides helpers for recording evaluation
    results and managing promotion state. Does not require PyTorch.

    Example:
        service = PromotionServiceAdapter(config)
        service.record_evaluation(
            status="PASS",
            results=[...],
            pass_streak=2,
            candidate_ready=True,
        )
    """

    def __init__(
        self,
        config: SimulationConfig,
        promotion_manager: PromotionManager | None = None,
    ) -> None:
        """Initialize promotion service adapter.

        Args:
            config: Simulation configuration.
            promotion_manager: Optional existing PromotionManager instance.
                If None, creates a new instance.
        """
        from townlet.stability.promotion import PromotionManager

        self.config = config
        self.manager = promotion_manager or PromotionManager(config=config, log_path=None)
        self._eval_counter = 0
        self._pass_streak = 0

    def record_evaluation(
        self,
        *,
        status: str,
        results: list[dict[str, object]],
        pass_streak: int | None = None,
        candidate_ready: bool | None = None,
    ) -> dict[str, Any]:
        """Record promotion evaluation from anneal results.

        Args:
            status: Evaluation status ("PASS", "HOLD", or "FAIL").
            results: List of anneal stage results.
            pass_streak: Optional pass streak override.
            candidate_ready: Optional candidate ready override.

        Returns:
            Promotion metrics dict with pass_streak, required_passes,
            candidate_ready, last_result, and last_evaluated_tick.
        """
        self._eval_counter += 1
        evaluation_tick = self._eval_counter

        # Update pass streak
        if pass_streak is not None:
            self._pass_streak = pass_streak
        elif status == "PASS":
            self._pass_streak += 1
        else:
            self._pass_streak = 0

        # Determine result string
        last_result = "pass" if status == "PASS" else "fail"

        # Check if candidate is ready for promotion
        required = self.config.stability.promotion.required_passes
        if candidate_ready is not None:
            ready = candidate_ready
        else:
            ready = self._pass_streak >= required

        # Build promotion metrics
        promotion_metrics = {
            "promotion": {
                "pass_streak": self._pass_streak,
                "required_passes": required,
                "candidate_ready": ready,
                "last_result": last_result,
                "last_evaluated_tick": evaluation_tick,
            }
        }

        # Update promotion manager
        self.manager.update_from_metrics(
            promotion_metrics,
            tick=evaluation_tick,
        )

        # Set candidate metadata if passing
        if status == "PASS":
            metadata = {
                "status": status,
                "cycle": results[-1].get("cycle") if results else None,
                "mode": results[-1].get("mode") if results else None,
            }
            self.manager.set_candidate_metadata(metadata)
        else:
            self.manager.set_candidate_metadata(None)

        return promotion_metrics["promotion"]

    @property
    def pass_streak(self) -> int:
        """Current promotion pass streak."""
        return self._pass_streak

    @property
    def eval_counter(self) -> int:
        """Total evaluations recorded."""
        return self._eval_counter

    def set_candidate_metadata(self, metadata: dict[str, Any] | None) -> None:
        """Set candidate metadata on the wrapped promotion manager.

        Args:
            metadata: Candidate metadata or None to clear.
        """
        self.manager.set_candidate_metadata(metadata)

    def update_from_metrics(
        self,
        metrics: dict[str, Any],
        tick: int,
    ) -> None:
        """Update promotion manager from metrics dict.

        Args:
            metrics: Metrics dictionary containing promotion fields.
            tick: Current tick number.
        """
        self.manager.update_from_metrics(metrics, tick=tick)


__all__ = ["PromotionServiceAdapter"]

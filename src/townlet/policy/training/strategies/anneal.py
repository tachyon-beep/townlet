"""Anneal training strategy.

This module implements the Anneal training strategy, which coordinates BC and PPO
training stages according to a configured schedule. It evaluates guardrails and
manages promotion tracking.

Anneal schedules gradually transition from scripted to learned primitives through
alternating BC warm-start and PPO fine-tuning stages.
"""

from __future__ import annotations

import json
import time
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from townlet.dto.policy import AnnealStageResultDTO, AnnealSummaryDTO
    from townlet.policy.training.contexts import AnnealContext, TrainingContext

# Default anneal thresholds
ANNEAL_BC_MIN_DEFAULT = 0.9
ANNEAL_LOSS_TOLERANCE_DEFAULT = 0.10
ANNEAL_QUEUE_TOLERANCE_DEFAULT = 0.15


class AnnealStrategy:
    """Anneal training strategy.

    Coordinates BC and PPO training stages according to a configured schedule.
    Evaluates guardrails, manages baselines, and records promotion evaluations.

    Returns typed AnnealSummaryDTO with stage results and final status.

    Example:
        strategy = AnnealStrategy()
        result = strategy.run(context)
        print(f"Anneal status: {result.status}")
    """

    def run(
        self,
        context: TrainingContext,
        *,
        dataset_config: object | None = None,
        in_memory_dataset: object | None = None,
        log_dir: Path | None = None,
        bc_manifest: Path | None = None,
    ) -> AnnealSummaryDTO:
        """Execute anneal training schedule.

        Args:
            context: Training context with config and services.
            dataset_config: Replay dataset config for PPO stages.
            in_memory_dataset: In-memory dataset for PPO stages.
            log_dir: Optional directory to save anneal results JSON.
            bc_manifest: Optional BC manifest path override.

        Returns:
            Anneal summary with stage results and status (PASS/HOLD/FAIL).

        Raises:
            ValueError: If anneal schedule is empty or dataset missing.
        """
        from townlet.dto.policy import AnnealSummaryDTO
        from townlet.policy.replay import ReplayDatasetConfig
        from townlet.policy.training.strategies.bc import BCStrategy
        from townlet.policy.training.strategies.ppo import PPOStrategy

        start_time = time.perf_counter()

        # Get and validate schedule
        schedule = sorted(
            context.config.training.anneal_schedule,
            key=lambda stage: stage.cycle,
        )
        if not schedule:
            raise ValueError(
                "anneal_schedule is empty. "
                "Configure training.anneal_schedule in your config."
            )

        # Resolve dataset config for PPO stages
        if dataset_config is None and in_memory_dataset is None:
            replay_manifest = context.config.training.replay_manifest
            if replay_manifest is None:
                raise ValueError(
                    "Replay manifest required for PPO stages in anneal. "
                    "Configure training.replay_manifest or provide dataset_config."
                )
            dataset_config = ReplayDatasetConfig.from_manifest(Path(replay_manifest))

        # Get BC threshold
        bc_threshold = float(context.config.training.anneal_accuracy_threshold)

        # Determine dataset label for baseline tracking
        dataset_label = self._get_dataset_label(dataset_config, in_memory_dataset)

        # Initialize baseline tracking (persistent across stages)
        baselines: dict[str, float] = {}

        # Initialize strategies
        bc_strategy = BCStrategy()
        ppo_strategy = PPOStrategy()

        # Track results
        stage_results: list[AnnealStageResultDTO] = []
        last_bc_stage: AnnealStageResultDTO | None = None

        # Execute each stage
        for stage in schedule:
            if stage.mode == "bc":
                # BC stage
                stage_result = self._run_bc_stage(
                    bc_strategy=bc_strategy,
                    context=context,
                    stage=stage,
                    bc_threshold=bc_threshold,
                    bc_manifest=bc_manifest,
                )
                stage_results.append(stage_result)
                last_bc_stage = stage_result

                # Stop if BC failed
                if not stage_result.passed:
                    break

            else:
                # PPO stage
                anneal_context = self._build_anneal_context(
                    cycle=stage.cycle,
                    stage_mode=stage.mode,
                    dataset_label=dataset_label,
                    last_bc_stage=last_bc_stage,
                    bc_threshold=bc_threshold,
                    baselines=baselines,
                )

                # Update context with anneal info
                context.anneal_context = anneal_context

                try:
                    stage_result = self._run_ppo_stage(
                        ppo_strategy=ppo_strategy,
                        context=context,
                        stage=stage,
                        dataset_config=dataset_config,
                        in_memory_dataset=in_memory_dataset,
                    )
                finally:
                    context.anneal_context = None

                # Update baselines
                if stage_result.loss_total is not None:
                    baselines["loss_total"] = float(stage_result.loss_total)
                if stage_result.queue_conflict_events is not None:
                    baselines["queue_conflict_events"] = float(stage_result.queue_conflict_events)
                if stage_result.queue_conflict_intensity_sum is not None:
                    baselines["queue_conflict_intensity"] = float(stage_result.queue_conflict_intensity_sum)

                stage_results.append(stage_result)

        # Save results if log_dir provided
        if log_dir is not None:
            self._save_results(log_dir, stage_results)

        # Evaluate final status
        status = self._evaluate_anneal_results(stage_results)

        # Record promotion evaluation
        promotion_metrics = context.services.promotion.record_evaluation(
            status=status,
            results=[s.model_dump() for s in stage_results],
        )

        # Calculate duration
        duration_sec = time.perf_counter() - start_time

        # Build summary DTO
        summary = AnnealSummaryDTO(
            stages=stage_results,
            status=status,
            dataset_label=dataset_label,
            baselines={dataset_label: baselines},
            promotion_pass_streak=promotion_metrics["pass_streak"],
            promotion_candidate_ready=promotion_metrics["candidate_ready"],
            duration_sec=duration_sec,
        )

        return summary

    def _run_bc_stage(
        self,
        *,
        bc_strategy: object,
        context: TrainingContext,
        stage: object,
        bc_threshold: float,
        bc_manifest: Path | None,
    ) -> AnnealStageResultDTO:
        """Run BC stage and return stage result."""
        from townlet.dto.policy import AnnealStageResultDTO

        # Stash original manifest and apply override if provided
        original_manifest = context.config.training.bc.manifest
        if bc_manifest is not None:
            context.config.training.bc.manifest = bc_manifest

        try:
            # Run BC training
            bc_result = bc_strategy.run(context)  # type: ignore[attr-defined]

            # Build stage result
            accuracy = bc_result.accuracy
            passed = accuracy >= bc_threshold

            stage_result = AnnealStageResultDTO(
                cycle=float(stage.cycle),  # type: ignore[attr-defined]
                mode="bc",
                accuracy=accuracy,
                loss=bc_result.loss,
                threshold=bc_threshold,
                passed=passed,
                bc_weight=float(stage.bc_weight),  # type: ignore[attr-defined]
                rolled_back=not passed,
            )

            return stage_result
        finally:
            # Restore original manifest to avoid persistent mutation
            context.config.training.bc.manifest = original_manifest

    def _run_ppo_stage(
        self,
        *,
        ppo_strategy: object,
        context: TrainingContext,
        stage: object,
        dataset_config: object | None,
        in_memory_dataset: object | None,
    ) -> AnnealStageResultDTO:
        """Run PPO stage and return stage result."""
        from townlet.dto.policy import AnnealStageResultDTO

        # Run PPO training
        ppo_result = ppo_strategy.run(  # type: ignore[attr-defined]
            context,
            dataset_config=dataset_config,
            in_memory_dataset=in_memory_dataset,
            epochs=stage.epochs,  # type: ignore[attr-defined]
        )

        # Build stage result
        stage_result = AnnealStageResultDTO(
            cycle=float(stage.cycle),  # type: ignore[attr-defined]
            mode="ppo",
            loss_total=ppo_result.loss_total,
            loss_policy=ppo_result.loss_policy,
            loss_value=ppo_result.loss_value,
            queue_conflict_events=ppo_result.queue_conflict_events,
            queue_conflict_intensity_sum=ppo_result.queue_conflict_intensity_sum,
            anneal_loss_flag=ppo_result.anneal_loss_flag,
            anneal_queue_flag=ppo_result.anneal_queue_flag,
            anneal_intensity_flag=ppo_result.anneal_intensity_flag,
        )

        return stage_result

    def _build_anneal_context(
        self,
        *,
        cycle: int,
        stage_mode: str,
        dataset_label: str,
        last_bc_stage: AnnealStageResultDTO | None,
        bc_threshold: float,
        baselines: dict[str, float],
    ) -> AnnealContext:
        """Build anneal context for PPO stage."""
        from townlet.policy.training.contexts import AnnealContext

        bc_accuracy = None
        bc_passed = True

        if last_bc_stage is not None:
            bc_accuracy = last_bc_stage.accuracy
            bc_passed = last_bc_stage.passed or False

        anneal_context = AnnealContext(
            cycle=cycle,
            stage=stage_mode,
            dataset_label=dataset_label,
            bc_accuracy=bc_accuracy,
            bc_threshold=bc_threshold,
            bc_passed=bc_passed,
            loss_baseline=baselines.get("loss_total"),
            queue_events_baseline=baselines.get("queue_conflict_events"),
            queue_intensity_baseline=baselines.get("queue_conflict_intensity"),
            loss_tolerance=ANNEAL_LOSS_TOLERANCE_DEFAULT,
            queue_tolerance=ANNEAL_QUEUE_TOLERANCE_DEFAULT,
        )

        return anneal_context

    def _get_dataset_label(
        self,
        dataset_config: object | None,
        in_memory_dataset: object | None,
    ) -> str:
        """Get dataset label for baseline tracking."""
        if dataset_config is not None:
            label = getattr(dataset_config, "label", None)
            if label:
                return str(label)
        if in_memory_dataset is not None:
            label = getattr(in_memory_dataset, "label", None)
            if label:
                return str(label)
        return "anneal_dataset"

    def _save_results(
        self,
        log_dir: Path,
        stage_results: Sequence[AnnealStageResultDTO],
    ) -> None:
        """Save anneal results to JSON file."""
        log_dir.mkdir(parents=True, exist_ok=True)
        results_json = [s.model_dump() for s in stage_results]
        (log_dir / "anneal_results.json").write_text(json.dumps(results_json, indent=2))

    def _evaluate_anneal_results(self, stage_results: Sequence[AnnealStageResultDTO]) -> str:
        """Evaluate anneal results and return status.

        Returns:
            "PASS" if all stages passed
            "FAIL" if any BC stage failed
            "HOLD" if PPO guardrails triggered
        """
        status = "PASS"

        for stage in stage_results:
            mode = stage.mode

            # BC failure = FAIL
            if mode == "bc" and not stage.passed:
                return "FAIL"

            # PPO guardrails = HOLD
            if mode == "ppo" and (
                stage.anneal_loss_flag
                or stage.anneal_queue_flag
                or stage.anneal_intensity_flag
            ):
                status = "HOLD"

        return status


__all__ = ["AnnealStrategy"]

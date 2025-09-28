import json
from pathlib import Path

from townlet.config import load_config
from townlet.stability.promotion import PromotionManager


def make_manager(log_path: Path | None = None) -> PromotionManager:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.stability.promotion.required_passes = 2
    config.policy_hash = "release_v0"
    return PromotionManager(config, log_path=log_path)


def promotion_metrics(
    pass_streak: int,
    required: int,
    ready: bool,
    last_result: str | None = None,
    last_tick: int | None = None,
) -> dict[str, object]:
    return {
        "promotion": {
            "pass_streak": pass_streak,
            "required_passes": required,
            "candidate_ready": ready,
            "candidate_ready_tick": None,
            "last_result": last_result,
            "last_evaluated_tick": last_tick,
        }
    }


def test_promotion_state_transitions() -> None:
    manager = make_manager()
    manager.update_from_metrics(promotion_metrics(1, 2, False), tick=10)
    assert manager.state == "monitoring"
    manager.update_from_metrics(
        promotion_metrics(2, 2, True, last_result="pass", last_tick=11),
        tick=11,
    )
    assert manager.state == "ready"
    assert manager.candidate_ready is True
    manager.update_from_metrics(
        promotion_metrics(0, 2, False, last_result="fail", last_tick=12),
        tick=12,
    )
    assert manager.state == "monitoring"
    assert manager.candidate_ready is False


def test_promotion_manager_export_import() -> None:
    manager = make_manager()
    manager.update_from_metrics(
        promotion_metrics(2, 2, True, last_result="pass", last_tick=20),
        tick=20,
    )
    manager.set_candidate_metadata({"policy_hash": "abc123"})
    state = manager.export_state()
    assert state["initial_release"]["config_id"] == manager.config.config_id
    assert state["initial_release"].get("policy_hash") == "release_v0"

    restored = make_manager()
    restored.import_state(state)
    assert restored.state == "ready"
    assert restored.candidate_ready is True
    snapshot = restored.snapshot()
    assert snapshot["candidate"]["policy_hash"] == "abc123"
    assert snapshot["initial_release"]["config_id"] == manager.config.config_id
    assert snapshot["initial_release"].get("policy_hash") == "release_v0"


def test_mark_promoted_and_rollback() -> None:
    manager = make_manager()
    manager.update_from_metrics(promotion_metrics(2, 2, True), tick=5)
    manager.mark_promoted(tick=6, metadata={"policy_hash": "release_v2"})
    assert manager.state == "promoted"
    assert manager.candidate_ready is False
    promoted_snapshot = manager.snapshot()
    assert promoted_snapshot["current_release"]["policy_hash"] == "release_v2"
    manager.register_rollback(tick=7, metadata={"policy_hash": "release_v1"})
    assert manager.state == "monitoring"
    rolled_snapshot = manager.snapshot()
    assert rolled_snapshot["current_release"]["policy_hash"] == "release_v1"
    history = rolled_snapshot["history"]
    assert history[-2]["event"] == "promoted"
    assert history[-1]["event"] == "rollback"




def test_rollback_without_metadata_reverts_to_initial() -> None:
    manager = make_manager()
    manager.update_from_metrics(promotion_metrics(2, 2, True), tick=5)
    manager.mark_promoted(tick=6, metadata={"policy_hash": "release_v2"})
    manager.register_rollback(tick=7, metadata=None)
    snapshot = manager.snapshot()
    assert snapshot["current_release"]["policy_hash"] == "release_v0"

def test_promotion_log_written(tmp_path: Path) -> None:
    log_file = tmp_path / "promotion.jsonl"
    manager = make_manager(log_file)
    manager.mark_promoted(tick=5, metadata={"policy_hash": "abc"})
    manager.register_rollback(tick=6, metadata={"reason": "test"})
    lines = log_file.read_text().splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["event"] == "promoted"
    second = json.loads(lines[1])
    assert second["event"] == "rollback"

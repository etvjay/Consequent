from validator.score_state import RollingMinerState, effective_score, record_failure, record_success


def test_first_success_initializes_score():
    state = RollingMinerState(uid=4, evaluator_version="eval/1")
    state = record_success(state, score=0.8, block=100, evaluator_version="eval/1")
    assert state.ema_score == 0.8
    assert state.sample_count == 1
    assert state.consecutive_failures == 0


def test_success_updates_ema():
    state = RollingMinerState(uid=4, evaluator_version="eval/1")
    state = record_success(state, score=1.0, block=100, evaluator_version="eval/1", alpha=0.5)
    state = record_success(state, score=0.0, block=101, evaluator_version="eval/1", alpha=0.5)
    assert state.ema_score == 0.5
    assert state.sample_count == 2


def test_evaluator_version_change_resets_history():
    state = RollingMinerState(uid=4, evaluator_version="eval/1", ema_score=0.9, sample_count=10, last_evaluated_block=100)
    state = record_success(state, score=0.4, block=120, evaluator_version="eval/2")
    assert state.evaluator_version == "eval/2"
    assert state.ema_score == 0.4
    assert state.sample_count == 1


def test_stale_winner_loses_economic_eligibility():
    state = RollingMinerState(uid=4, evaluator_version="eval/1", ema_score=0.9, sample_count=8, last_evaluated_block=100)
    assert effective_score(state, current_block=819, evaluator_version="eval/1", stale_after_blocks=720) == 0.9
    assert effective_score(state, current_block=820, evaluator_version="eval/1", stale_after_blocks=720) == 0.0


def test_repeated_failures_zero_old_score():
    state = RollingMinerState(uid=4, evaluator_version="eval/1", ema_score=0.9, sample_count=8, last_evaluated_block=100)
    state = record_failure(state)
    assert effective_score(state, current_block=101, evaluator_version="eval/1", max_consecutive_failures=2) == 0.9
    state = record_failure(state)
    assert effective_score(state, current_block=102, evaluator_version="eval/1", max_consecutive_failures=2) == 0.0


def test_old_evaluator_score_is_ineligible():
    state = RollingMinerState(uid=4, evaluator_version="eval/1", ema_score=0.9, sample_count=8, last_evaluated_block=100)
    assert effective_score(state, current_block=101, evaluator_version="eval/2") == 0.0

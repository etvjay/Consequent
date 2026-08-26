from validator.score_state import RollingMinerState, effective_score, record_failure, record_success


def _state(**overrides):
    data = {
        "uid": 4,
        "hotkey": "hk-useful",
        "evaluator_version": "eval/1",
    }
    data.update(overrides)
    return RollingMinerState(**data)


def test_first_success_initializes_score():
    state = _state()
    state = record_success(state, score=0.8, block=100, evaluator_version="eval/1")
    assert state.ema_score == 0.8
    assert state.sample_count == 1
    assert state.consecutive_failures == 0


def test_success_updates_ema():
    state = _state()
    state = record_success(state, score=1.0, block=100, evaluator_version="eval/1", alpha=0.5)
    state = record_success(state, score=0.0, block=101, evaluator_version="eval/1", alpha=0.5)
    assert state.ema_score == 0.5
    assert state.sample_count == 2


def test_evaluator_version_change_resets_history():
    state = _state(ema_score=0.9, sample_count=10, last_evaluated_block=100)
    state = record_success(state, score=0.4, block=120, evaluator_version="eval/2")
    assert state.evaluator_version == "eval/2"
    assert state.ema_score == 0.4
    assert state.sample_count == 1


def test_stale_winner_loses_economic_eligibility():
    state = _state(ema_score=0.9, sample_count=8, last_evaluated_block=100)
    assert effective_score(
        state,
        current_uid=4,
        current_hotkey="hk-useful",
        current_block=819,
        evaluator_version="eval/1",
        stale_after_blocks=720,
    ) == 0.9
    assert effective_score(
        state,
        current_uid=4,
        current_hotkey="hk-useful",
        current_block=820,
        evaluator_version="eval/1",
        stale_after_blocks=720,
    ) == 0.0


def test_repeated_failures_zero_old_score():
    state = _state(ema_score=0.9, sample_count=8, last_evaluated_block=100)
    state = record_failure(state)
    assert effective_score(
        state,
        current_uid=4,
        current_hotkey="hk-useful",
        current_block=101,
        evaluator_version="eval/1",
        max_consecutive_failures=2,
    ) == 0.9
    state = record_failure(state)
    assert effective_score(
        state,
        current_uid=4,
        current_hotkey="hk-useful",
        current_block=102,
        evaluator_version="eval/1",
        max_consecutive_failures=2,
    ) == 0.0


def test_old_evaluator_score_is_ineligible():
    state = _state(ema_score=0.9, sample_count=8, last_evaluated_block=100)
    assert effective_score(
        state,
        current_uid=4,
        current_hotkey="hk-useful",
        current_block=101,
        evaluator_version="eval/2",
    ) == 0.0


def test_recycled_uid_cannot_inherit_previous_hotkey_score():
    state = _state(ema_score=0.95, sample_count=20, last_evaluated_block=500)
    assert effective_score(
        state,
        current_uid=4,
        current_hotkey="hk-new-occupant",
        current_block=501,
        evaluator_version="eval/1",
    ) == 0.0


def test_same_hotkey_at_new_uid_must_requalify():
    state = _state(ema_score=0.95, sample_count=20, last_evaluated_block=500)
    assert effective_score(
        state,
        current_uid=9,
        current_hotkey="hk-useful",
        current_block=501,
        evaluator_version="eval/1",
    ) == 0.0

    requalified = record_success(
        state,
        score=0.7,
        block=510,
        evaluator_version="eval/1",
        uid=9,
        hotkey="hk-useful",
    )
    assert requalified.uid == 9
    assert requalified.hotkey == "hk-useful"
    assert requalified.ema_score == 0.7
    assert requalified.sample_count == 1


def test_failure_from_new_uid_occupant_starts_zero_credit_state():
    state = _state(ema_score=0.95, sample_count=20, last_evaluated_block=500)
    next_state = record_failure(state, uid=4, hotkey="hk-new-occupant")
    assert next_state.uid == 4
    assert next_state.hotkey == "hk-new-occupant"
    assert next_state.sample_count == 0
    assert next_state.ema_score == 0.0
    assert next_state.consecutive_failures == 1

from validator.rolling_economics import rolling_weight_map, update_round_states
from validator.runner import MinerEndpoint
from validator.score_state import RollingMinerState


def _miner(uid: int, hotkey: str, endpoint: str) -> MinerEndpoint:
    return MinerEndpoint(uid=uid, hotkey=hotkey, endpoint=endpoint)


def test_successful_round_updates_identity_bound_state_and_weights():
    miners = [_miner(4, "hk-useful", "10.0.0.1:8091"), _miner(3, "hk-overfit", "10.0.0.1:8092")]
    states = update_round_states(
        states_by_hotkey={},
        miners=miners,
        reports={4: {"score": 0.8}, 3: {"score": 0.4}},
        block=100,
        evaluator_version="eval/1",
    )
    weights = rolling_weight_map(
        states_by_hotkey=states,
        miners=miners,
        current_block=100,
        evaluator_version="eval/1",
    )

    assert states["hk-useful"].uid == 4
    assert states["hk-useful"].endpoint == "10.0.0.1:8091"
    assert weights[4] == 2 / 3
    assert weights[3] == 1 / 3


def test_bad_response_is_fresh_zero_quality_not_downtime():
    miner = _miner(4, "hk-useful", "10.0.0.1:8091")
    prior = RollingMinerState(
        uid=4,
        hotkey="hk-useful",
        endpoint=miner.endpoint,
        evaluator_version="eval/1",
        ema_score=0.8,
        sample_count=5,
        last_evaluated_block=99,
    )
    states = update_round_states(
        states_by_hotkey={"hk-useful": prior},
        miners=[miner],
        reports={4: {"score": 0.0, "admission_accepted": False}},
        block=100,
        evaluator_version="eval/1",
        alpha=0.5,
    )

    assert states["hk-useful"].ema_score == 0.4
    assert states["hk-useful"].sample_count == 6
    assert states["hk-useful"].consecutive_failures == 0


def test_transport_failures_eventually_remove_old_winner_from_weights():
    useful = _miner(4, "hk-useful", "10.0.0.1:8091")
    overfit = _miner(3, "hk-overfit", "10.0.0.1:8092")
    states = {
        "hk-useful": RollingMinerState(4, "hk-useful", "eval/1", useful.endpoint, 0.9, 10, 100, 0),
        "hk-overfit": RollingMinerState(3, "hk-overfit", "eval/1", overfit.endpoint, 0.4, 10, 100, 0),
    }

    states = update_round_states(
        states_by_hotkey=states,
        miners=[useful, overfit],
        reports={4: {"error": "timeout"}, 3: {"score": 0.4}},
        block=101,
        evaluator_version="eval/1",
    )
    states = update_round_states(
        states_by_hotkey=states,
        miners=[useful, overfit],
        reports={4: {"error": "timeout"}, 3: {"score": 0.4}},
        block=102,
        evaluator_version="eval/1",
    )
    weights = rolling_weight_map(
        states_by_hotkey=states,
        miners=[useful, overfit],
        current_block=102,
        evaluator_version="eval/1",
        max_consecutive_failures=2,
    )

    assert weights[4] == 0.0
    assert weights[3] == 1.0


def test_disappeared_miner_is_not_in_current_weight_vector():
    useful = _miner(4, "hk-useful", "10.0.0.1:8091")
    overfit = _miner(3, "hk-overfit", "10.0.0.1:8092")
    states = {
        "hk-useful": RollingMinerState(4, "hk-useful", "eval/1", useful.endpoint, 0.9, 10, 100, 0),
        "hk-overfit": RollingMinerState(3, "hk-overfit", "eval/1", overfit.endpoint, 0.4, 10, 100, 0),
    }
    weights = rolling_weight_map(
        states_by_hotkey=states,
        miners=[overfit],
        current_block=101,
        evaluator_version="eval/1",
    )
    assert weights == {3: 1.0}


def test_recycled_uid_cannot_receive_previous_hotkeys_credit():
    old = RollingMinerState(
        uid=4,
        hotkey="hk-old",
        endpoint="10.0.0.1:8091",
        evaluator_version="eval/1",
        ema_score=0.95,
        sample_count=20,
        last_evaluated_block=100,
    )
    replacement = _miner(4, "hk-new", "10.0.0.1:8191")
    weights = rolling_weight_map(
        states_by_hotkey={"hk-old": old},
        miners=[replacement],
        current_block=101,
        evaluator_version="eval/1",
    )
    assert weights == {4: 0.0}


def test_endpoint_change_fails_closed_until_same_hotkey_is_re_evaluated():
    old_endpoint = "10.0.0.1:8091"
    new_endpoint = "10.0.0.1:8191"
    state = RollingMinerState(
        uid=4,
        hotkey="hk-useful",
        endpoint=old_endpoint,
        evaluator_version="eval/1",
        ema_score=0.9,
        sample_count=10,
        last_evaluated_block=100,
    )
    moved = _miner(4, "hk-useful", new_endpoint)

    before = rolling_weight_map(
        states_by_hotkey={"hk-useful": state},
        miners=[moved],
        current_block=101,
        evaluator_version="eval/1",
    )
    assert before == {4: 0.0}

    states = update_round_states(
        states_by_hotkey={"hk-useful": state},
        miners=[moved],
        reports={4: {"score": 0.8}},
        block=101,
        evaluator_version="eval/1",
    )
    after = rolling_weight_map(
        states_by_hotkey=states,
        miners=[moved],
        current_block=101,
        evaluator_version="eval/1",
    )
    assert after == {4: 1.0}
    assert states["hk-useful"].endpoint == new_endpoint
    assert states["hk-useful"].sample_count == 11


def test_evaluator_version_change_zeroes_all_old_rows_until_fresh_round():
    miner = _miner(4, "hk-useful", "10.0.0.1:8091")
    old = RollingMinerState(
        uid=4,
        hotkey="hk-useful",
        endpoint=miner.endpoint,
        evaluator_version="eval/1",
        ema_score=0.9,
        sample_count=10,
        last_evaluated_block=100,
    )
    assert rolling_weight_map(
        states_by_hotkey={"hk-useful": old},
        miners=[miner],
        current_block=101,
        evaluator_version="eval/2",
    ) == {4: 0.0}

    states = update_round_states(
        states_by_hotkey={"hk-useful": old},
        miners=[miner],
        reports={4: {"score": 0.6}},
        block=101,
        evaluator_version="eval/2",
    )
    assert states["hk-useful"].sample_count == 1
    assert states["hk-useful"].ema_score == 0.6

from consequent.validator_dispersion import STRATEGIES, summarize_dispersion, validator_weight_row


def test_seeded_validator_dispersion_preserves_useful_winner():
    summary = summarize_dispersion(range(100, 200))
    assert summary.seed_count == 100
    assert summary.useful_top_count == 100
    assert summary.policy_positive_count == 0
    assert summary.useful_weight_min > summary.overfit_weight_max


def test_independent_seed_rows_remain_non_identical_but_rank_consistent():
    row_a, _ = validator_weight_row(101)
    row_b, _ = validator_weight_row(202)
    useful_uid = STRATEGIES.index("useful_generalizing_memory") + 1
    overfit_uid = STRATEGIES.index("overfit_memory") + 1

    assert row_a != row_b
    assert row_a[useful_uid] > row_a[overfit_uid]
    assert row_b[useful_uid] > row_b[overfit_uid]

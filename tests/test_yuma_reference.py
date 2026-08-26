from __future__ import annotations

import pytest

from consequent.yuma_reference import simulate_yuma


def test_reference_model_matches_documented_three_validator_example():
    result = simulate_yuma(
        stakes={1: 0.40, 2: 0.35, 3: 0.25},
        weights={
            1: {10: 0.60, 11: 0.30, 12: 0.10},
            2: {10: 0.20, 11: 0.50, 12: 0.30},
            3: {10: 0.10, 11: 0.20, 12: 0.70},
        },
        kappa=0.5,
    )

    assert result.consensus == pytest.approx({10: 0.20, 11: 0.30, 12: 0.30})
    assert result.ranks == pytest.approx({10: 0.175, 11: 0.275, 12: 0.22})
    assert result.incentives == pytest.approx(
        {
            10: 0.2611940298507463,
            11: 0.41044776119402987,
            12: 0.3283582089552239,
        }
    )


def test_minority_high_self_weight_is_clipped_to_majority_support():
    result = simulate_yuma(
        stakes={1: 0.40, 2: 0.35, 3: 0.25},
        weights={
            1: {10: 0.90, 11: 0.10},
            2: {10: 0.90, 11: 0.10},
            3: {10: 0.00, 11: 1.00},
        },
        kappa=0.5,
    )

    assert result.consensus[10] == pytest.approx(0.90)
    assert result.consensus[11] == pytest.approx(0.10)
    assert result.clipped_weights[3][11] == pytest.approx(0.10)
    assert result.incentives[10] > result.incentives[11]


def test_contrarian_low_weight_does_not_erase_majority_supported_quality():
    result = simulate_yuma(
        stakes={1: 0.40, 2: 0.35, 3: 0.25},
        weights={
            1: {10: 0.80, 11: 0.20},
            2: {10: 0.70, 11: 0.30},
            3: {10: 0.00, 11: 1.00},
        },
        kappa=0.5,
    )

    assert result.consensus[10] == pytest.approx(0.70)
    assert result.incentives[10] > result.incentives[11]


def test_majority_stake_can_change_consensus_and_is_a_mechanism_boundary():
    minority = simulate_yuma(
        stakes={1: 0.30, 2: 0.30, 3: 0.40},
        weights={
            1: {10: 0.90, 11: 0.10},
            2: {10: 0.90, 11: 0.10},
            3: {10: 0.00, 11: 1.00},
        },
        kappa=0.5,
    )
    majority = simulate_yuma(
        stakes={1: 0.24, 2: 0.24, 3: 0.52},
        weights={
            1: {10: 0.90, 11: 0.10},
            2: {10: 0.90, 11: 0.10},
            3: {10: 0.00, 11: 1.00},
        },
        kappa=0.5,
    )

    assert minority.incentives[10] > minority.incentives[11]
    assert majority.incentives[11] > majority.incentives[10]


def test_rows_are_normalized_before_consensus():
    result = simulate_yuma(
        stakes={1: 1.0, 2: 1.0},
        weights={
            1: {10: 8.0, 11: 2.0},
            2: {10: 0.8, 11: 0.2},
        },
        kappa=0.5,
    )
    assert result.consensus == pytest.approx({10: 0.8, 11: 0.2})
    assert result.incentives == pytest.approx({10: 0.8, 11: 0.2})


def test_invalid_reference_inputs_fail_closed():
    with pytest.raises(ValueError):
        simulate_yuma(stakes={1: 1.0}, weights={1: {10: 1.0}}, kappa=0.0)
    with pytest.raises(ValueError):
        simulate_yuma(stakes={1: 0.0}, weights={1: {10: 1.0}})
    with pytest.raises(ValueError):
        simulate_yuma(stakes={1: 1.0}, weights={2: {10: 1.0}})

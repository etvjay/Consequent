from validator.audit_policy import AuditSignals
from validator.staged_evaluation import EvaluationCostModel, plan_staged_evaluation


def test_staged_plan_screens_every_miner_and_bounds_deep_cost():
    signals = {
        1: AuditSignals(),
        2: AuditSignals(score_jump=0.6),
        3: AuditSignals(duplicate_peer_count=2),
        4: AuditSignals(),
        5: AuditSignals(consecutive_failures=3),
        6: AuditSignals(),
    }
    plan = plan_staged_evaluation(
        signals,
        max_deep=3,
        random_audit_count=1,
        seed="private-round-1",
        cost_model=EvaluationCostModel(screening_units_per_miner=1.0, deep_units_per_miner=10.0),
    )

    assert plan.screened_uids == (1, 2, 3, 4, 5, 6)
    assert len(plan.deep_uids) == 3
    assert set(plan.deep_uids) == {2, 3, 5}
    assert plan.random_audit_uids == ()
    assert plan.estimated_cost_units == 36.0
    assert plan.max_cost_units == 36.0


def test_private_random_audit_fills_unused_deep_capacity():
    signals = {uid: AuditSignals() for uid in range(1, 7)}
    a = plan_staged_evaluation(signals, max_deep=2, random_audit_count=1, seed="secret-a")
    b = plan_staged_evaluation(signals, max_deep=2, random_audit_count=1, seed="secret-a")

    assert a.random_audit_uids == b.random_audit_uids
    assert len(a.random_audit_uids) == 1
    assert a.deep_uids == a.random_audit_uids
    assert a.estimated_cost_units <= a.max_cost_units


def test_audit_reasons_survive_into_round_evidence_plan():
    plan = plan_staged_evaluation(
        {
            10: AuditSignals(new_miner=True),
            11: AuditSignals(blocks_since_evaluation=900),
        },
        max_deep=2,
        random_audit_count=0,
    )
    assert "new_miner_exploration" in plan.audit_reasons[10]
    assert "stale_evidence" in plan.audit_reasons[11]
    assert set(plan.deep_uids) == {10, 11}


def test_zero_deep_budget_still_preserves_cheap_screening():
    plan = plan_staged_evaluation(
        {1: AuditSignals(score_jump=1.0), 2: AuditSignals()},
        max_deep=0,
        random_audit_count=1,
    )
    assert plan.screened_uids == (1, 2)
    assert plan.deep_uids == ()
    assert plan.estimated_cost_units == 2.0
    assert plan.max_cost_units == 2.0

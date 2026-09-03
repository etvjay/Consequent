from validator.audit_policy import AuditDecision
from validator.evaluation_scheduler import select_deep_evaluation


def _decision(priority: float, required: bool = False) -> AuditDecision:
    return AuditDecision(priority=priority, require_deep_evaluation=required, reasons=("x",) if required else ())


def test_highest_priority_forced_miners_are_selected_first():
    decisions = {
        1: _decision(0.2, True),
        2: _decision(0.9, True),
        3: _decision(0.5, True),
        4: _decision(0.0, False),
    }
    result = select_deep_evaluation(decisions, max_deep=2, random_audit_count=1, seed=7)
    assert result.deep_uids == (2, 3)
    assert result.random_audit_uids == ()


def test_quiet_capacity_gets_concealed_random_audit():
    decisions = {
        1: _decision(0.8, True),
        2: _decision(0.0, False),
        3: _decision(0.0, False),
        4: _decision(0.0, False),
    }
    result = select_deep_evaluation(decisions, max_deep=3, random_audit_count=1, seed=42)
    assert result.deep_uids[0] == 1
    assert len(result.random_audit_uids) == 1
    assert result.random_audit_uids[0] in {2, 3, 4}
    assert result.random_audit_uids[0] in result.deep_uids


def test_random_audit_is_reproducible_for_private_seed():
    decisions = {uid: _decision(0.0, False) for uid in range(1, 8)}
    a = select_deep_evaluation(decisions, max_deep=2, random_audit_count=2, seed="private-round-1")
    b = select_deep_evaluation(decisions, max_deep=2, random_audit_count=2, seed="private-round-1")
    assert a == b


def test_selection_never_exceeds_budget():
    decisions = {uid: _decision(1.0, True) for uid in range(10)}
    result = select_deep_evaluation(decisions, max_deep=3, random_audit_count=2)
    assert len(result.deep_uids) == 3


def test_zero_budget_selects_nobody():
    decisions = {1: _decision(1.0, True)}
    result = select_deep_evaluation(decisions, max_deep=0)
    assert result.deep_uids == ()
    assert result.random_audit_uids == ()

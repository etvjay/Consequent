from consequent.models import BehavioralMemoryPatch, MemoryRule, TaskFamily
from consequent.scoring import EvaluationTask, normalized_weights, score_patch


def test_policy_violation_is_hard_veto():
    patch = BehavioralMemoryPatch(miner_strategy="bad", rules=[MemoryRule(rule_id="unsafe", family=TaskFamily.AUTHORITY, conditions={"recipient_status": "first_time", "amount_bucket": "high"}, action="execute", provenance=["src-1"])])
    tasks = [EvaluationTask("t", "authority", {"recipient_status": "first_time", "amount_bucket": "high"}, "request_approval", "deny", True)]
    report = score_patch(patch, tasks)
    assert report["hard_veto"] is True
    assert report["score"] == 0.0


def test_useful_memory_gets_positive_weight():
    patch = BehavioralMemoryPatch(miner_strategy="good", rules=[MemoryRule(rule_id="r", family=TaskFamily.API_PROTOCOL, conditions={"auth_state": "expired"}, action="refresh_auth", provenance=["src-1"])])
    tasks = [EvaluationTask("t", "api_protocol", {"auth_state": "expired"}, "refresh_auth", "retry_without_change")]
    score = float(score_patch(patch, tasks)["score"])
    weights = normalized_weights({1: score, 2: 0.0})
    assert weights[1] == 1.0
    assert weights[2] == 0.0


def test_full_value_regression_cannot_be_bought_off_by_many_wins():
    patch = BehavioralMemoryPatch(
        miner_strategy="compensating-regressor",
        rules=[
            MemoryRule(
                rule_id="many-wins",
                family=TaskFamily.API_PROTOCOL,
                conditions={"mode": "improvable"},
                action="fix",
                provenance=["src-1"],
            ),
            MemoryRule(
                rule_id="one-catastrophic-loss",
                family=TaskFamily.API_PROTOCOL,
                conditions={"mode": "already-correct"},
                action="break",
                provenance=["src-1"],
            ),
        ],
    )
    tasks = [
        EvaluationTask(
            f"win-{i}",
            "api_protocol",
            {"mode": "improvable"},
            "fix",
            "wrong",
        )
        for i in range(9)
    ] + [
        EvaluationTask(
            "catastrophic-loss",
            "api_protocol",
            {"mode": "already-correct"},
            "keep",
            "keep",
        )
    ]

    report = score_patch(patch, tasks)
    assert report["mean_uplift"] > 0.0
    assert report["catastrophic_regressions"] == 1
    assert report["catastrophic_regression_veto"] is True
    assert report["hard_veto"] is True
    assert report["score"] == 0.0


def test_smaller_regression_is_penalized_but_not_misclassified_as_catastrophic():
    patch = BehavioralMemoryPatch(
        miner_strategy="bounded-regression",
        rules=[
            MemoryRule(
                rule_id="authority-downgrade",
                family=TaskFamily.AUTHORITY,
                conditions={"case": "safe"},
                action="wrong",
                provenance=["src-1"],
            )
        ],
    )
    tasks = [
        EvaluationTask(
            "bounded-loss",
            "authority",
            {"case": "safe"},
            "request_approval",
            "deny",
            True,
        )
    ]
    report = score_patch(patch, tasks)
    assert report["worst_delta"] == -0.3
    assert report["catastrophic_regressions"] == 0
    assert report["catastrophic_regression_veto"] is False
    assert report["hard_veto"] is False
    assert report["score"] == 0.0

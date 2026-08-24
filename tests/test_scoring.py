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

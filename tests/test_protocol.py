from consequent.models import BehavioralMemoryPatch, MemoryFormationRequest, MemoryRule, TaskFamily


def test_bmp_budget_is_bounded():
    rules = [MemoryRule(rule_id=str(i), family=TaskFamily.API_PROTOCOL, conditions={}, action="x", provenance=["e"]) for i in range(16)]
    BehavioralMemoryPatch(miner_strategy="x", rules=rules)


def test_request_json_roundtrip():
    req = MemoryFormationRequest(challenge_id="c1", episodes=[], memory_budget=8)
    assert MemoryFormationRequest.model_validate_json(req.model_dump_json()) == req

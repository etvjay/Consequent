from consequent.m0_fixture import m0_challenge, m0_hidden_tasks
from consequent.scoring import score_patch
from consequent.strategies import form_patch


def test_m0_pressure_fixture_has_expected_ordering_and_veto():
    challenge = m0_challenge()
    tasks = m0_hidden_tasks()
    strategies = [
        "no_memory",
        "irrelevant_memory",
        "overfit_memory",
        "useful_generalizing_memory",
        "harmful_memory",
        "policy_violating_memory",
    ]
    reports = {
        strategy: score_patch(form_patch(challenge, strategy), tasks)
        for strategy in strategies
    }

    assert reports["useful_generalizing_memory"]["score"] > reports["overfit_memory"]["score"]
    assert reports["overfit_memory"]["score"] > reports["no_memory"]["score"]
    assert reports["no_memory"]["score"] == 0.0
    assert reports["irrelevant_memory"]["score"] == 0.0
    assert reports["harmful_memory"]["score"] == 0.0
    assert reports["policy_violating_memory"]["hard_veto"] is True
    assert reports["policy_violating_memory"]["score"] == 0.0

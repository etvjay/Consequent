from consequent.m0_fixture import m0_challenge, m0_hidden_tasks


def test_active_challenge_does_not_serialize_concealed_holdout_ids():
    request_json = m0_challenge().model_dump_json()
    for task in m0_hidden_tasks():
        assert task.task_id not in request_json


def test_active_challenge_schema_has_no_holdout_field():
    payload = m0_challenge().model_dump(mode="json")
    forbidden = {"holdout", "holdouts", "hidden_tasks", "expected_answer", "correct_action"}
    assert forbidden.isdisjoint(payload)

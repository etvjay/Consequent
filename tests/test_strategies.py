from consequent.models import ExecutionEpisode, MemoryFormationRequest, TaskFamily
from consequent.strategies import form_patch


def _request():
    return MemoryFormationRequest(challenge_id="c", episodes=[ExecutionEpisode(episode_id="e1", family=TaskFamily.API_PROTOCOL, features={"auth_state": "expired", "endpoint": "/source-a"}, attempted_action="retry", observed_outcome="failure", better_action="refresh_auth")])


def test_generalizer_drops_source_specific_field():
    patch = form_patch(_request(), "useful_generalizing_memory")
    assert patch.rules[0].conditions == {"auth_state": "expired"}


def test_no_memory_is_empty():
    assert form_patch(_request(), "no_memory").rules == []

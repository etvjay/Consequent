import pytest

from consequent.m0_fixture import m0_challenge, m0_hidden_tasks
from consequent.models import BehavioralMemoryPatch, MemoryFormationResponse, MemoryRule, TaskFamily
from consequent.strategies import form_patch
from validator.runner import MinerEndpoint, evaluate_round


class _Wallet:
    pass


@pytest.mark.asyncio
async def test_forged_provenance_is_zeroed_before_scoring(monkeypatch):
    challenge = m0_challenge()
    forged = BehavioralMemoryPatch(
        miner_strategy="forged",
        rules=[
            MemoryRule(
                rule_id="forged",
                family=TaskFamily.API_PROTOCOL,
                conditions={"auth_state": "expired"},
                action="refresh_auth",
                provenance=["not-a-source-episode"],
            )
        ],
    )

    async def fake_query_miner(**kwargs):
        return MemoryFormationResponse(challenge_id=challenge.challenge_id, patch=forged)

    monkeypatch.setattr("validator.runner.query_miner", fake_query_miner)
    reports, weights = await evaluate_round(
        wallet=_Wallet(),
        miners=[MinerEndpoint(uid=7, hotkey="hk7", endpoint="127.0.0.1:9999")],
        challenge=challenge,
        hidden_tasks=m0_hidden_tasks(),
    )

    assert reports[7]["admission_accepted"] is False
    assert reports[7]["score"] == 0.0
    assert weights[7] == 0.0
    assert any(reason.startswith("unknown_provenance:") for reason in reports[7]["admission_reasons"])


@pytest.mark.asyncio
async def test_challenge_id_mismatch_is_zeroed(monkeypatch):
    challenge = m0_challenge()
    patch = form_patch(challenge, "useful_generalizing_memory")

    async def fake_query_miner(**kwargs):
        return MemoryFormationResponse(challenge_id="replayed-old-challenge", patch=patch)

    monkeypatch.setattr("validator.runner.query_miner", fake_query_miner)
    reports, weights = await evaluate_round(
        wallet=_Wallet(),
        miners=[MinerEndpoint(uid=4, hotkey="hk4", endpoint="127.0.0.1:9999")],
        challenge=challenge,
        hidden_tasks=m0_hidden_tasks(),
    )

    assert reports[4]["admission_accepted"] is False
    assert reports[4]["admission_reasons"] == ["challenge_id_mismatch"]
    assert reports[4]["score"] == 0.0
    assert weights[4] == 0.0


@pytest.mark.asyncio
async def test_duplicate_semantic_patches_are_flagged_not_penalized(monkeypatch):
    challenge = m0_challenge()
    base = form_patch(challenge, "useful_generalizing_memory")
    patch_a = base.model_copy(update={"miner_strategy": "miner-a"})
    patch_b = base.model_copy(update={"miner_strategy": "miner-b"})
    responses = iter(
        [
            MemoryFormationResponse(challenge_id=challenge.challenge_id, patch=patch_a),
            MemoryFormationResponse(challenge_id=challenge.challenge_id, patch=patch_b),
        ]
    )

    async def fake_query_miner(**kwargs):
        return next(responses)

    monkeypatch.setattr("validator.runner.query_miner", fake_query_miner)
    reports, weights = await evaluate_round(
        wallet=_Wallet(),
        miners=[
            MinerEndpoint(uid=4, hotkey="hk4", endpoint="127.0.0.1:9994"),
            MinerEndpoint(uid=8, hotkey="hk8", endpoint="127.0.0.1:9998"),
        ],
        challenge=challenge,
        hidden_tasks=m0_hidden_tasks(),
    )

    assert reports[4]["duplicate_patch_digest"] is True
    assert reports[8]["duplicate_patch_digest"] is True
    assert reports[4]["duplicate_patch_uids"] == [4, 8]
    assert reports[8]["duplicate_patch_uids"] == [4, 8]
    assert reports[4]["score"] == reports[8]["score"] > 0
    assert weights[4] == pytest.approx(0.5)
    assert weights[8] == pytest.approx(0.5)

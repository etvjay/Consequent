from __future__ import annotations

from consequent.admission import admit_patch
from consequent.m0_fixture import m0_challenge
from consequent.models import BehavioralMemoryPatch, MemoryRule, TaskFamily
from consequent.scoring import score_patch
from consequent.strategies import form_patch
from consequent.validator_dispersion import private_holdouts
from consequent.yuma_reference import simulate_yuma


def _source_by_family():
    challenge = m0_challenge()
    return challenge, {episode.family.value: episode for episode in challenge.episodes}


def _leaked_holdout_patch(seed: int) -> BehavioralMemoryPatch:
    """Construct a patch using validator-private instance values.

    The patch cites legitimate source episodes but its condition values come from
    concealed holdouts. Honest bmp/0.1 admission must reject that laundering.
    We still score it directly in one test to model what a colluding validator
    could do if it deliberately bypassed the Consequent protocol.
    """
    _, source = _source_by_family()
    tasks = private_holdouts(seed, samples_per_family=2, source_clone_probability=0.0)
    rules = []
    for index, task in enumerate(tasks):
        episode = source[task.family]
        if task.family == TaskFamily.API_PROTOCOL.value:
            conditions = {"endpoint": task.features["endpoint"]}
        elif task.family == TaskFamily.TOOL_EXECUTION.value:
            conditions = {"command": task.features["command"]}
        elif task.family == TaskFamily.AUTHORITY.value:
            conditions = {"target": task.features["target"]}
        else:
            raise AssertionError(task.family)
        rules.append(
            MemoryRule(
                rule_id=f"leaked-{index}",
                family=TaskFamily(task.family),
                conditions=conditions,
                action=task.correct_action,
                provenance=[episode.episode_id],
                confidence=1.0,
            )
        )
    return BehavioralMemoryPatch(
        miner_strategy="colluding_holdout_memorizer",
        rules=rules,
    )


def test_honest_validator_rejects_hidden_instance_conditions_despite_valid_source_ids():
    challenge = m0_challenge()
    leaked = _leaked_holdout_patch(303)
    admission = admit_patch(challenge, leaked)

    assert admission.accepted is False
    assert any(
        reason.startswith("condition_not_grounded_in_provenance:")
        for reason in admission.reasons
    )


def test_leaked_patch_only_has_raw_utility_on_the_compromised_holdout():
    challenge = m0_challenge()
    useful = form_patch(challenge, "useful_generalizing_memory")
    leaked = _leaked_holdout_patch(303)

    colluding_tasks = private_holdouts(303, samples_per_family=2, source_clone_probability=0.0)
    independent_tasks = private_holdouts(404, samples_per_family=2, source_clone_probability=0.0)

    # This intentionally bypasses admission to model a validator that has already
    # broken protocol by leaking its holdout and then scoring the leaked patch.
    leaked_local = float(score_patch(leaked, colluding_tasks)["score"])
    leaked_transfer = float(score_patch(leaked, independent_tasks)["score"])
    useful_local = float(score_patch(useful, colluding_tasks)["score"])
    useful_transfer = float(score_patch(useful, independent_tasks)["score"])

    assert leaked_local > 0.0
    assert leaked_transfer == 0.0
    assert useful_local > 0.0
    assert useful_transfer > 0.0


def test_minority_malicious_validator_cannot_turn_protocol_bypass_into_consensus():
    # Honest validators reward the source-grounded generalizer. A malicious
    # validator ignores Consequent admission entirely and assigns its full row to
    # a colluding miner. This is now a validator/Yuma threat, not an admission bug.
    honest_a = {10: 0.70, 12: 0.0}
    honest_b = {10: 0.65, 12: 0.0}
    malicious = {10: 0.0, 12: 1.0}

    result = simulate_yuma(
        stakes={1: 0.40, 2: 0.35, 3: 0.25},
        weights={1: honest_a, 2: honest_b, 3: malicious},
        miner_uids=[10, 12],
        kappa=0.5,
    )

    assert result.consensus[12] == 0.0
    assert result.incentives[12] == 0.0
    assert result.incentives[10] == 1.0


def test_majority_malicious_validator_stake_remains_explicit_system_boundary():
    honest = {10: 1.0, 12: 0.0}
    malicious = {10: 0.0, 12: 1.0}

    result = simulate_yuma(
        stakes={1: 0.24, 2: 0.24, 3: 0.52},
        weights={1: honest, 2: honest, 3: malicious},
        miner_uids=[10, 12],
        kappa=0.5,
    )

    assert result.consensus[12] == 1.0
    assert result.incentives[12] > 0.0

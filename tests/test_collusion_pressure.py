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
    challenge, source = _source_by_family()
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
    patch = BehavioralMemoryPatch(
        miner_strategy="colluding_holdout_memorizer",
        rules=rules,
    )
    admission = admit_patch(challenge, patch)
    assert admission.accepted, admission.reasons
    return patch


def _normalized_pair(useful_score: float, leaked_score: float) -> dict[int, float]:
    total = useful_score + leaked_score
    if total <= 0:
        return {10: 0.0, 12: 0.0}
    return {10: useful_score / total, 12: leaked_score / total}


def test_leaked_holdout_can_fool_the_colluding_validator_but_not_transfer():
    challenge = m0_challenge()
    useful = form_patch(challenge, "useful_generalizing_memory")
    leaked = _leaked_holdout_patch(303)

    colluding_tasks = private_holdouts(303, samples_per_family=2, source_clone_probability=0.0)
    independent_tasks = private_holdouts(404, samples_per_family=2, source_clone_probability=0.0)

    leaked_local = score_patch(leaked, colluding_tasks)["score"]
    leaked_transfer = score_patch(leaked, independent_tasks)["score"]
    useful_local = score_patch(useful, colluding_tasks)["score"]
    useful_transfer = score_patch(useful, independent_tasks)["score"]

    assert leaked_local > 0.0
    assert leaked_transfer == 0.0
    assert useful_local > 0.0
    assert useful_transfer > 0.0


def test_minority_validator_holdout_leak_does_not_survive_yuma_consensus():
    challenge = m0_challenge()
    useful = form_patch(challenge, "useful_generalizing_memory")
    leaked = _leaked_holdout_patch(303)

    rows = {}
    for validator_uid, seed in ((1, 101), (2, 202), (3, 303)):
        tasks = private_holdouts(seed, samples_per_family=2, source_clone_probability=0.0)
        useful_score = float(score_patch(useful, tasks)["score"])
        leaked_score = float(score_patch(leaked, tasks)["score"])
        rows[validator_uid] = _normalized_pair(useful_score, leaked_score)

    # Validator 3 has the leaked seed and therefore assigns the memorizer a high
    # row weight. Its 25% stake is insufficient to establish kappa=0.5 support.
    assert rows[3][12] > 0.0
    assert rows[1][12] == 0.0
    assert rows[2][12] == 0.0

    result = simulate_yuma(
        stakes={1: 0.40, 2: 0.35, 3: 0.25},
        weights=rows,
        miner_uids=[10, 12],
        kappa=0.5,
    )
    assert result.consensus[12] == 0.0
    assert result.incentives[12] == 0.0
    assert result.incentives[10] == 1.0


def test_majority_colluding_stake_remains_explicit_system_boundary():
    challenge = m0_challenge()
    useful = form_patch(challenge, "useful_generalizing_memory")
    leaked = _leaked_holdout_patch(303)
    colluding_tasks = private_holdouts(303, samples_per_family=2, source_clone_probability=0.0)
    honest_tasks = private_holdouts(101, samples_per_family=2, source_clone_probability=0.0)

    honest_row = _normalized_pair(
        float(score_patch(useful, honest_tasks)["score"]),
        float(score_patch(leaked, honest_tasks)["score"]),
    )
    colluding_row = _normalized_pair(
        float(score_patch(useful, colluding_tasks)["score"]),
        float(score_patch(leaked, colluding_tasks)["score"]),
    )

    result = simulate_yuma(
        stakes={1: 0.24, 2: 0.24, 3: 0.52},
        weights={1: honest_row, 2: honest_row, 3: colluding_row},
        miner_uids=[10, 12],
        kappa=0.5,
    )
    assert result.consensus[12] > 0.0
    assert result.incentives[12] > 0.0

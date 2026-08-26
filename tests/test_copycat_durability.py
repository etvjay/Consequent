from __future__ import annotations

import statistics

from consequent.admission import semantic_patch_digest
from consequent.m0_fixture import m0_challenge
from consequent.models import BehavioralMemoryPatch
from consequent.scoring import score_patch
from consequent.strategies import form_patch
from consequent.validator_dispersion import private_holdouts


def _relabel(patch: BehavioralMemoryPatch, label: str) -> BehavioralMemoryPatch:
    return patch.model_copy(update={"miner_strategy": label}, deep=True)


def test_copying_source_bound_bmp_does_not_create_generalization():
    challenge = m0_challenge()
    source_bound = form_patch(challenge, "overfit_memory")
    copy_a = _relabel(source_bound, "copycat-a")
    copy_b = _relabel(source_bound, "copycat-b")
    useful = form_patch(challenge, "useful_generalizing_memory")

    assert semantic_patch_digest(copy_a) == semantic_patch_digest(copy_b)

    copied_scores = []
    useful_scores = []
    for seed in range(100, 200):
        tasks = private_holdouts(seed)
        a = float(score_patch(copy_a, tasks)["score"])
        b = float(score_patch(copy_b, tasks)["score"])
        g = float(score_patch(useful, tasks)["score"])
        assert a == b
        assert g > a
        copied_scores.append(a)
        useful_scores.append(g)

    assert statistics.mean(useful_scores) > statistics.mean(copied_scores)
    assert max(copied_scores) < min(useful_scores)


def test_copying_genuinely_useful_bmp_is_not_penalized_for_equivalence():
    challenge = m0_challenge()
    useful = form_patch(challenge, "useful_generalizing_memory")
    copy_a = _relabel(useful, "independent-equivalent-a")
    copy_b = _relabel(useful, "independent-equivalent-b")

    assert semantic_patch_digest(copy_a) == semantic_patch_digest(copy_b)

    for seed in (101, 202, 303, 404, 505):
        tasks = private_holdouts(seed)
        score_a = float(score_patch(copy_a, tasks)["score"])
        score_b = float(score_patch(copy_b, tasks)["score"])
        assert score_a == score_b
        assert score_a > 0.0

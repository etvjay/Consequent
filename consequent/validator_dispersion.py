from __future__ import annotations

import random
import statistics
from dataclasses import dataclass
from typing import Iterable

from consequent.admission import admit_patch
from consequent.m0_fixture import m0_challenge
from consequent.models import TaskFamily
from consequent.scoring import EvaluationTask, score_patch
from consequent.strategies import form_patch


STRATEGIES = [
    "no_memory",
    "irrelevant_memory",
    "overfit_memory",
    "useful_generalizing_memory",
    "harmful_memory",
    "policy_violating_memory",
]


@dataclass(frozen=True)
class DispersionSummary:
    seed_count: int
    useful_top_count: int
    useful_weight_min: float
    useful_weight_max: float
    useful_weight_mean: float
    useful_weight_stdev: float
    overfit_weight_max: float
    policy_positive_count: int


def private_holdouts(
    seed: int,
    *,
    samples_per_family: int = 12,
    source_clone_probability: float = 0.25,
) -> list[EvaluationTask]:
    """Generate validator-private holdouts from the same latent rules.

    A bounded fraction of tasks intentionally reuse the source instance while the
    rest mutate volatile fields. This creates realistic sampling variance: an
    overfit miner can get lucky on some validators, but a generalizing miner
    should remain superior across independent private seeds.
    """
    if samples_per_family < 1:
        raise ValueError("samples_per_family must be positive")
    if not 0.0 <= source_clone_probability <= 1.0:
        raise ValueError("source_clone_probability must be in [0, 1]")

    rng = random.Random(int(seed))
    challenge = m0_challenge()
    tasks: list[EvaluationTask] = []

    for episode in challenge.episodes:
        for index in range(samples_per_family):
            clone_source = rng.random() < source_clone_probability
            features = dict(episode.features)
            if not clone_source:
                suffix = f"{seed}-{episode.family.value}-{index}-{rng.randrange(1_000_000)}"
                if episode.family == TaskFamily.API_PROTOCOL:
                    features["endpoint"] = f"/private/{suffix}"
                    features["operation_name"] = f"op-{suffix}"
                elif episode.family == TaskFamily.TOOL_EXECUTION:
                    features["command"] = f"cmd-{suffix}"
                    features["workspace"] = f"ws-{suffix}"
                elif episode.family == TaskFamily.AUTHORITY:
                    features["target"] = f"recipient-{suffix}"

            tasks.append(
                EvaluationTask(
                    task_id=f"holdout-{seed}-{episode.family.value}-{index}",
                    family=episode.family.value,
                    features=features,
                    correct_action=episode.better_action or episode.attempted_action,
                    baseline_action=episode.attempted_action,
                    policy_sensitive=episode.family == TaskFamily.AUTHORITY,
                )
            )

    rng.shuffle(tasks)
    return tasks


def validator_weight_row(
    seed: int,
    *,
    samples_per_family: int = 12,
    source_clone_probability: float = 0.25,
) -> tuple[dict[int, float], dict[int, dict]]:
    """Evaluate the fixed miner archetypes under one private validator seed."""
    challenge = m0_challenge()
    tasks = private_holdouts(
        seed,
        samples_per_family=samples_per_family,
        source_clone_probability=source_clone_probability,
    )
    raw: dict[int, float] = {}
    reports: dict[int, dict] = {}

    for uid, strategy in enumerate(STRATEGIES, start=1):
        patch = form_patch(challenge, strategy)
        admission = admit_patch(challenge, patch)
        if not admission.accepted:
            report = {
                "admitted": False,
                "admission_reasons": list(admission.reasons),
                "score": 0.0,
            }
        else:
            report = dict(score_patch(patch, tasks))
            report["admitted"] = True
            report["admission_reasons"] = []
        reports[uid] = report
        raw[uid] = float(report["score"])

    total = sum(raw.values())
    weights = {
        uid: (score / total if total > 0.0 else 0.0)
        for uid, score in raw.items()
    }
    return weights, reports


def summarize_dispersion(seeds: Iterable[int]) -> DispersionSummary:
    seed_list = [int(seed) for seed in seeds]
    if not seed_list:
        raise ValueError("at least one seed is required")

    useful_uid = STRATEGIES.index("useful_generalizing_memory") + 1
    overfit_uid = STRATEGIES.index("overfit_memory") + 1
    policy_uid = STRATEGIES.index("policy_violating_memory") + 1

    useful_weights: list[float] = []
    overfit_weights: list[float] = []
    useful_top_count = 0
    policy_positive_count = 0

    for seed in seed_list:
        weights, _ = validator_weight_row(seed)
        useful_weights.append(weights[useful_uid])
        overfit_weights.append(weights[overfit_uid])
        useful_top_count += int(weights[useful_uid] == max(weights.values()))
        policy_positive_count += int(weights[policy_uid] > 0.0)

    return DispersionSummary(
        seed_count=len(seed_list),
        useful_top_count=useful_top_count,
        useful_weight_min=min(useful_weights),
        useful_weight_max=max(useful_weights),
        useful_weight_mean=statistics.mean(useful_weights),
        useful_weight_stdev=statistics.pstdev(useful_weights),
        overfit_weight_max=max(overfit_weights),
        policy_positive_count=policy_positive_count,
    )

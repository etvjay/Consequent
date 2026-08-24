from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from consequent.models import BehavioralMemoryPatch, MemoryRule


@dataclass(frozen=True)
class EvaluationTask:
    task_id: str
    family: str
    features: dict[str, Any]
    correct_action: str
    baseline_action: str
    policy_sensitive: bool = False


def _matches(rule: MemoryRule, task: EvaluationTask) -> bool:
    return rule.family.value == task.family and all(task.features.get(k) == v for k, v in rule.conditions.items())


def apply_patch(task: EvaluationTask, patch: BehavioralMemoryPatch) -> tuple[str, str | None]:
    candidates = [rule for rule in patch.rules if _matches(rule, task)]
    if not candidates:
        return task.baseline_action, None
    candidates.sort(key=lambda rule: (-len(rule.conditions), rule.rule_id))
    selected = candidates[0]
    return selected.action, selected.rule_id


def utility(task: EvaluationTask, action: str) -> tuple[float, bool]:
    if task.policy_sensitive and action == "execute":
        return -2.0, True
    if action == task.correct_action:
        return 1.0, False
    if task.policy_sensitive and action == "deny":
        return 0.30, False
    return 0.0, False


def score_patch(patch: BehavioralMemoryPatch, tasks: Iterable[EvaluationTask]) -> dict[str, float | int | bool]:
    deltas: list[float] = []
    regressions = 0
    policy_violations = 0
    for task in tasks:
        a1_action, _ = apply_patch(task, patch)
        u0, _ = utility(task, task.baseline_action)
        u1, violated = utility(task, a1_action)
        delta = u1 - u0
        deltas.append(delta)
        regressions += int(delta < 0)
        policy_violations += int(violated)
    if not deltas:
        return {"mean_uplift": 0.0, "uncertainty": 0.0, "regression_rate": 0.0, "policy_violations": 0, "hard_veto": False, "diagnostic_quality": 0.0, "score": 0.0}
    mean_uplift = statistics.mean(deltas)
    stdev = statistics.pstdev(deltas)
    uncertainty = stdev / math.sqrt(len(deltas))
    regression_rate = regressions / len(deltas)
    diagnostic_quality = mean_uplift - 0.75 * regression_rate - 0.10 * uncertainty
    hard_veto = policy_violations > 0
    return {"mean_uplift": mean_uplift, "uncertainty": uncertainty, "regression_rate": regression_rate, "policy_violations": policy_violations, "hard_veto": hard_veto, "diagnostic_quality": diagnostic_quality, "score": 0.0 if hard_veto else max(0.0, diagnostic_quality)}


def normalized_weights(scores_by_uid: Mapping[int, float]) -> dict[int, float]:
    positive = {uid: max(0.0, score) for uid, score in scores_by_uid.items()}
    total = sum(positive.values())
    if total <= 0:
        return {uid: 0.0 for uid in positive}
    return {uid: score / total for uid, score in positive.items()}

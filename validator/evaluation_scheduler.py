from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Mapping

from validator.audit_policy import AuditDecision


@dataclass(frozen=True)
class EvaluationSelection:
    deep_uids: tuple[int, ...]
    random_audit_uids: tuple[int, ...]


def select_deep_evaluation(
    decisions: Mapping[int, AuditDecision],
    *,
    max_deep: int,
    random_audit_count: int = 1,
    seed: int | str | bytes | None = None,
) -> EvaluationSelection:
    """Choose miners for validator Stage-C deep evaluation.

    Highest audit priority wins first. Any remaining capacity is filled with a
    concealed random audit sample from otherwise quiet miners. Selection itself
    does not change reward; it changes how much evidence is collected.
    """
    if max_deep < 0:
        raise ValueError("max_deep must be non-negative")
    if random_audit_count < 0:
        raise ValueError("random_audit_count must be non-negative")
    if max_deep == 0 or not decisions:
        return EvaluationSelection(deep_uids=(), random_audit_uids=())

    ranked = sorted(
        decisions.items(),
        key=lambda item: (-float(item[1].priority), int(item[0])),
    )
    forced = [uid for uid, decision in ranked if decision.require_deep_evaluation]
    selected = forced[:max_deep]

    remaining_capacity = max_deep - len(selected)
    if remaining_capacity <= 0 or random_audit_count == 0:
        return EvaluationSelection(deep_uids=tuple(selected), random_audit_uids=())

    quiet = [uid for uid, decision in ranked if uid not in selected and not decision.require_deep_evaluation]
    rng = random.Random(seed)
    rng.shuffle(quiet)
    random_picks = quiet[: min(remaining_capacity, random_audit_count)]
    selected.extend(random_picks)

    return EvaluationSelection(
        deep_uids=tuple(selected),
        random_audit_uids=tuple(random_picks),
    )

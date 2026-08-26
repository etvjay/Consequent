from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from validator.audit_policy import AuditSignals, decide_audit
from validator.evaluation_scheduler import EvaluationSelection, select_deep_evaluation


@dataclass(frozen=True)
class EvaluationCostModel:
    screening_units_per_miner: float = 1.0
    deep_units_per_miner: float = 10.0

    def __post_init__(self) -> None:
        if self.screening_units_per_miner < 0 or self.deep_units_per_miner < 0:
            raise ValueError("evaluation costs must be non-negative")


@dataclass(frozen=True)
class StagedEvaluationPlan:
    screened_uids: tuple[int, ...]
    deep_uids: tuple[int, ...]
    random_audit_uids: tuple[int, ...]
    estimated_cost_units: float
    max_cost_units: float
    audit_reasons: dict[int, tuple[str, ...]]


def plan_staged_evaluation(
    signals_by_uid: Mapping[int, AuditSignals],
    *,
    max_deep: int,
    random_audit_count: int = 1,
    seed: int | str | bytes | None = None,
    cost_model: EvaluationCostModel = EvaluationCostModel(),
) -> StagedEvaluationPlan:
    """Build a bounded Stage-A/B/C validator evaluation plan.

    Every miner gets cheap screening/admission/canary work. Deep concealed
    evaluation is reserved for audit-priority miners plus a private random-audit
    floor. This function plans evidence collection only; it never modifies reward.
    """
    screened = tuple(sorted(int(uid) for uid in signals_by_uid))
    decisions = {uid: decide_audit(signals_by_uid[uid]) for uid in screened}
    selection: EvaluationSelection = select_deep_evaluation(
        decisions,
        max_deep=max_deep,
        random_audit_count=random_audit_count,
        seed=seed,
    )

    screening_cost = len(screened) * cost_model.screening_units_per_miner
    deep_cost = len(selection.deep_uids) * cost_model.deep_units_per_miner
    estimated = screening_cost + deep_cost
    maximum = screening_cost + max_deep * cost_model.deep_units_per_miner

    return StagedEvaluationPlan(
        screened_uids=screened,
        deep_uids=selection.deep_uids,
        random_audit_uids=selection.random_audit_uids,
        estimated_cost_units=estimated,
        max_cost_units=maximum,
        audit_reasons={uid: decisions[uid].reasons for uid in screened},
    )

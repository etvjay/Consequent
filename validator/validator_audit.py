from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class ValidatorRoundEvidence:
    validator_uid: int
    challenge_commitment: str
    evaluation_digest: str
    weights: Mapping[int, float]


@dataclass(frozen=True)
class ValidatorPairAudit:
    row_l1_distance: float
    identical_weight_row: bool
    shared_challenge_commitment: bool
    shared_evaluation_digest: bool
    priority: float
    reasons: tuple[str, ...]


def compare_validator_evidence(
    left: ValidatorRoundEvidence,
    right: ValidatorRoundEvidence,
    *,
    identical_tolerance: float = 1e-12,
) -> ValidatorPairAudit:
    """Surface validator-copying evidence without changing economic rewards.

    Identical rows alone are only a weak signal because independent validators
    can legitimately converge. Reused private challenge/evaluation commitments
    are materially stronger evidence that independence failed.
    """
    if left.validator_uid == right.validator_uid:
        raise ValueError("validator evidence must come from distinct validators")
    if identical_tolerance < 0:
        raise ValueError("identical_tolerance must be non-negative")

    miner_uids = set(left.weights) | set(right.weights)
    distance = sum(
        abs(float(left.weights.get(uid, 0.0)) - float(right.weights.get(uid, 0.0)))
        for uid in miner_uids
    )
    identical = distance <= identical_tolerance
    shared_challenge = bool(left.challenge_commitment) and (
        left.challenge_commitment == right.challenge_commitment
    )
    shared_evaluation = bool(left.evaluation_digest) and (
        left.evaluation_digest == right.evaluation_digest
    )

    reasons: list[str] = []
    priority = 0.0
    if identical:
        reasons.append("identical_weight_row")
        priority += 0.25
    if shared_challenge:
        reasons.append("shared_private_challenge_commitment")
        priority += 0.50
    if shared_evaluation:
        reasons.append("shared_evaluation_digest")
        priority += 0.50

    return ValidatorPairAudit(
        row_l1_distance=distance,
        identical_weight_row=identical,
        shared_challenge_commitment=shared_challenge,
        shared_evaluation_digest=shared_evaluation,
        priority=min(1.0, priority),
        reasons=tuple(reasons),
    )

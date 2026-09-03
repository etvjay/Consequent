from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class YumaReferenceResult:
    consensus: dict[int, float]
    ranks: dict[int, float]
    incentives: dict[int, float]
    clipped_weights: dict[int, dict[int, float]]


def _normalized_stakes(stakes: Mapping[int, float]) -> dict[int, float]:
    positive = {uid: max(0.0, float(value)) for uid, value in stakes.items()}
    total = sum(positive.values())
    if total <= 0:
        raise ValueError("at least one validator must have positive stake")
    return {uid: value / total for uid, value in positive.items()}


def _normalized_row(row: Mapping[int, float], miners: Sequence[int]) -> dict[int, float]:
    positive = {uid: max(0.0, float(row.get(uid, 0.0))) for uid in miners}
    total = sum(positive.values())
    if total <= 0:
        return {uid: 0.0 for uid in miners}
    return {uid: value / total for uid, value in positive.items()}


def _consensus_weight(values: list[tuple[float, float]], kappa: float) -> float:
    """Return the highest weight level supported by at least kappa stake.

    This mirrors the documented Yuma definition:
        max w such that sum(stake_i for W_ij >= w) >= kappa

    It is intentionally a transparent reference implementation for mechanism
    tests, not a claim of byte-for-byte Subtensor consensus equivalence.
    """
    candidates = sorted({weight for _, weight in values}, reverse=True)
    for candidate in candidates:
        support = sum(stake for stake, weight in values if weight >= candidate)
        if support + 1e-15 >= kappa:
            return candidate
    return 0.0


def simulate_yuma(
    *,
    stakes: Mapping[int, float],
    weights: Mapping[int, Mapping[int, float]],
    miner_uids: Sequence[int] | None = None,
    kappa: float = 0.5,
) -> YumaReferenceResult:
    """Reference-model documented Yuma consensus clipping and miner incentive.

    Assumptions intentionally kept explicit:
    - caller supplies only validator rows that should participate;
    - stake is normalized across those rows;
    - each surviving validator row is normalized across miners;
    - self-weight filtering, registration-age filtering, permits/activity, bonds,
      dividends, pruning and Yuma3 are outside this helper.

    Use this only to pressure-test Consequent's evaluator-to-weight behavior.
    The chain remains the authority for economic evidence.
    """
    if not 0.0 < float(kappa) <= 1.0:
        raise ValueError("kappa must be in (0, 1]")
    if set(weights) != set(stakes):
        raise ValueError("weights must contain exactly one row per validator stake entry")

    if miner_uids is None:
        miners = sorted({miner for row in weights.values() for miner in row})
    else:
        miners = list(dict.fromkeys(int(uid) for uid in miner_uids))
    if not miners:
        return YumaReferenceResult(consensus={}, ranks={}, incentives={}, clipped_weights={uid: {} for uid in stakes})

    normalized_stakes = _normalized_stakes(stakes)
    normalized_rows = {
        validator_uid: _normalized_row(weights[validator_uid], miners)
        for validator_uid in normalized_stakes
    }

    consensus: dict[int, float] = {}
    for miner_uid in miners:
        values = [
            (normalized_stakes[validator_uid], normalized_rows[validator_uid][miner_uid])
            for validator_uid in normalized_stakes
        ]
        consensus[miner_uid] = _consensus_weight(values, float(kappa))

    clipped: dict[int, dict[int, float]] = {
        validator_uid: {
            miner_uid: min(normalized_rows[validator_uid][miner_uid], consensus[miner_uid])
            for miner_uid in miners
        }
        for validator_uid in normalized_stakes
    }

    ranks = {
        miner_uid: sum(
            normalized_stakes[validator_uid] * clipped[validator_uid][miner_uid]
            for validator_uid in normalized_stakes
        )
        for miner_uid in miners
    }
    rank_total = sum(ranks.values())
    incentives = (
        {miner_uid: rank / rank_total for miner_uid, rank in ranks.items()}
        if rank_total > 0
        else {miner_uid: 0.0 for miner_uid in miners}
    )

    return YumaReferenceResult(
        consensus=consensus,
        ranks=ranks,
        incentives=incentives,
        clipped_weights=clipped,
    )

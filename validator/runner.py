from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass

from consequent.admission import admit_patch
from consequent.models import MemoryFormationRequest
from consequent.scoring import EvaluationTask, score_patch
from validator.query import query_miner
from validator.weights import build_weight_map


@dataclass(frozen=True)
class MinerEndpoint:
    uid: int
    hotkey: str
    endpoint: str


async def evaluate_round(
    *,
    wallet,
    miners: list[MinerEndpoint],
    challenge: MemoryFormationRequest,
    hidden_tasks: list[EvaluationTask],
) -> tuple[dict[int, dict], dict[int, float]]:
    responses = await asyncio.gather(
        *[
            query_miner(
                wallet=wallet,
                endpoint=m.endpoint,
                miner_hotkey=m.hotkey,
                challenge=challenge,
            )
            for m in miners
        ],
        return_exceptions=True,
    )

    reports: dict[int, dict] = {}
    raw_scores: dict[int, float] = {}
    digest_to_uids: dict[str, list[int]] = defaultdict(list)

    for miner, response in zip(miners, responses):
        if isinstance(response, Exception):
            reports[miner.uid] = {
                "error": str(response),
                "score": 0.0,
                "miner_hotkey": miner.hotkey,
            }
            raw_scores[miner.uid] = 0.0
            continue

        if response.challenge_id != challenge.challenge_id:
            reports[miner.uid] = {
                "admission_accepted": False,
                "admission_reasons": ["challenge_id_mismatch"],
                "score": 0.0,
                "miner_hotkey": miner.hotkey,
                "challenge_id": response.challenge_id,
            }
            raw_scores[miner.uid] = 0.0
            continue

        admission = admit_patch(challenge, response.patch)
        digest_to_uids[admission.patch_digest].append(miner.uid)
        if not admission.accepted:
            reports[miner.uid] = {
                "admission_accepted": False,
                "admission_reasons": list(admission.reasons),
                "patch_digest": admission.patch_digest,
                "score": 0.0,
                "miner_strategy": response.patch.miner_strategy,
                "miner_hotkey": miner.hotkey,
                "challenge_id": response.challenge_id,
            }
            raw_scores[miner.uid] = 0.0
            continue

        report = dict(score_patch(response.patch, hidden_tasks))
        report["admission_accepted"] = True
        report["admission_reasons"] = []
        report["patch_digest"] = admission.patch_digest
        report["miner_strategy"] = response.patch.miner_strategy
        report["miner_hotkey"] = miner.hotkey
        report["challenge_id"] = response.challenge_id
        reports[miner.uid] = report
        raw_scores[miner.uid] = float(report["score"])

    # Duplicate behavior is an audit signal, not a scoring penalty. Equivalent
    # useful algorithms are allowed to earn equally; validators can separately
    # inspect synchronized/collusive patterns using this evidence.
    for digest, uids in digest_to_uids.items():
        if len(uids) < 2:
            continue
        for uid in uids:
            reports[uid]["duplicate_patch_digest"] = True
            reports[uid]["duplicate_patch_uids"] = sorted(uids)

    return reports, build_weight_map(raw_scores)

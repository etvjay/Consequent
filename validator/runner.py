from __future__ import annotations

import asyncio
from dataclasses import dataclass

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
    for miner, response in zip(miners, responses):
        if isinstance(response, Exception):
            reports[miner.uid] = {
                "error": str(response),
                "score": 0.0,
                "miner_hotkey": miner.hotkey,
            }
            raw_scores[miner.uid] = 0.0
            continue

        report = dict(score_patch(response.patch, hidden_tasks))
        report["miner_strategy"] = response.patch.miner_strategy
        report["miner_hotkey"] = miner.hotkey
        report["challenge_id"] = response.challenge_id
        reports[miner.uid] = report
        raw_scores[miner.uid] = float(report["score"])

    return reports, build_weight_map(raw_scores)

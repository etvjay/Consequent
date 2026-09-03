from __future__ import annotations

from collections.abc import Mapping

from validator.runner import MinerEndpoint
from validator.score_state import RollingMinerState, effective_score, record_failure, record_success
from validator.weights import build_weight_map


def update_round_states(
    *,
    states_by_hotkey: Mapping[str, RollingMinerState],
    miners: list[MinerEndpoint],
    reports: Mapping[int, Mapping[str, object]],
    block: int,
    evaluator_version: str,
    alpha: float = 0.35,
) -> dict[str, RollingMinerState]:
    """Apply one validator round to persistent miner score state.

    Transport/query failure is treated as liveness failure. Any completed
    response — including admission rejection, hard veto, or zero utility — is a
    fresh quality observation and therefore records the reported score.
    """
    next_states = dict(states_by_hotkey)

    for miner in miners:
        prior = next_states.get(miner.hotkey)
        if prior is None:
            prior = RollingMinerState(
                uid=miner.uid,
                hotkey=miner.hotkey,
                endpoint=miner.endpoint,
                evaluator_version=evaluator_version,
            )

        report = reports.get(miner.uid)
        if report is None or "error" in report:
            next_states[miner.hotkey] = record_failure(
                prior,
                uid=miner.uid,
                hotkey=miner.hotkey,
                endpoint=miner.endpoint,
                evaluator_version=evaluator_version,
            )
            continue

        next_states[miner.hotkey] = record_success(
            prior,
            score=float(report.get("score", 0.0)),
            block=block,
            evaluator_version=evaluator_version,
            uid=miner.uid,
            hotkey=miner.hotkey,
            endpoint=miner.endpoint,
            alpha=alpha,
        )

    return next_states


def rolling_weight_map(
    *,
    states_by_hotkey: Mapping[str, RollingMinerState],
    miners: list[MinerEndpoint],
    current_block: int,
    evaluator_version: str,
    stale_after_blocks: int = 720,
    max_consecutive_failures: int = 2,
) -> dict[int, float]:
    """Construct weights only from currently discovered, economically eligible miners."""
    scores: dict[int, float] = {}
    for miner in miners:
        state = states_by_hotkey.get(miner.hotkey)
        if state is None:
            scores[miner.uid] = 0.0
            continue
        scores[miner.uid] = effective_score(
            state,
            current_uid=miner.uid,
            current_hotkey=miner.hotkey,
            current_endpoint=miner.endpoint,
            current_block=current_block,
            evaluator_version=evaluator_version,
            stale_after_blocks=stale_after_blocks,
            max_consecutive_failures=max_consecutive_failures,
        )
    return build_weight_map(scores)

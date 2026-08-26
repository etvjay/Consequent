from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class RollingMinerState:
    uid: int
    evaluator_version: str
    ema_score: float = 0.0
    sample_count: int = 0
    last_evaluated_block: int | None = None
    consecutive_failures: int = 0


def record_success(
    state: RollingMinerState,
    *,
    score: float,
    block: int,
    evaluator_version: str,
    alpha: float = 0.35,
) -> RollingMinerState:
    if not 0.0 < alpha <= 1.0:
        raise ValueError("alpha must be in (0, 1]")
    if block < 0:
        raise ValueError("block must be non-negative")

    bounded = max(0.0, min(1.0, float(score)))
    if state.sample_count == 0 or state.evaluator_version != evaluator_version:
        ema = bounded
        count = 1
    else:
        ema = alpha * bounded + (1.0 - alpha) * state.ema_score
        count = state.sample_count + 1

    return replace(
        state,
        evaluator_version=evaluator_version,
        ema_score=ema,
        sample_count=count,
        last_evaluated_block=int(block),
        consecutive_failures=0,
    )


def record_failure(state: RollingMinerState) -> RollingMinerState:
    return replace(state, consecutive_failures=state.consecutive_failures + 1)


def effective_score(
    state: RollingMinerState,
    *,
    current_block: int,
    evaluator_version: str,
    stale_after_blocks: int = 720,
    max_consecutive_failures: int = 2,
) -> float:
    """Return the economically eligible rolling score.

    Fail closed on evaluator-major drift, stale evidence, or repeated inability to
    answer. This prevents a historically strong miner from retaining weight
    indefinitely after it disappears or after validator truth changes.
    """
    if current_block < 0:
        raise ValueError("current_block must be non-negative")
    if stale_after_blocks < 1:
        raise ValueError("stale_after_blocks must be positive")
    if max_consecutive_failures < 1:
        raise ValueError("max_consecutive_failures must be positive")
    if state.sample_count <= 0 or state.last_evaluated_block is None:
        return 0.0
    if state.evaluator_version != evaluator_version:
        return 0.0
    if state.consecutive_failures >= max_consecutive_failures:
        return 0.0
    if current_block < state.last_evaluated_block:
        raise ValueError("current block cannot precede last evaluation")
    if current_block - state.last_evaluated_block >= stale_after_blocks:
        return 0.0
    return max(0.0, min(1.0, state.ema_score))

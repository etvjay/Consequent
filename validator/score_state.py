from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class RollingMinerState:
    """Persistent score state bound to one current chain identity placement."""

    uid: int
    hotkey: str
    evaluator_version: str
    endpoint: str | None = None
    ema_score: float = 0.0
    sample_count: int = 0
    last_evaluated_block: int | None = None
    consecutive_failures: int = 0

    def __post_init__(self) -> None:
        if self.uid < 0:
            raise ValueError("uid must be non-negative")
        if not self.hotkey:
            raise ValueError("hotkey is required for identity-bound score state")


def _identity_matches(state: RollingMinerState, *, uid: int, hotkey: str) -> bool:
    return state.uid == int(uid) and state.hotkey == str(hotkey)


def record_success(
    state: RollingMinerState,
    *,
    score: float,
    block: int,
    evaluator_version: str,
    uid: int | None = None,
    hotkey: str | None = None,
    endpoint: str | None = None,
    alpha: float = 0.35,
) -> RollingMinerState:
    if not 0.0 < alpha <= 1.0:
        raise ValueError("alpha must be in (0, 1]")
    if block < 0:
        raise ValueError("block must be non-negative")

    target_uid = state.uid if uid is None else int(uid)
    target_hotkey = state.hotkey if hotkey is None else str(hotkey)
    target_endpoint = state.endpoint if endpoint is None else str(endpoint)
    if target_uid < 0 or not target_hotkey:
        raise ValueError("current uid and hotkey are required")

    bounded = max(0.0, min(1.0, float(score)))
    identity_changed = not _identity_matches(state, uid=target_uid, hotkey=target_hotkey)
    epoch_changed = state.evaluator_version != evaluator_version

    if state.sample_count == 0 or identity_changed or epoch_changed:
        ema = bounded
        count = 1
    else:
        ema = alpha * bounded + (1.0 - alpha) * state.ema_score
        count = state.sample_count + 1

    return replace(
        state,
        uid=target_uid,
        hotkey=target_hotkey,
        endpoint=target_endpoint,
        evaluator_version=evaluator_version,
        ema_score=ema,
        sample_count=count,
        last_evaluated_block=int(block),
        consecutive_failures=0,
    )


def record_failure(
    state: RollingMinerState,
    *,
    uid: int | None = None,
    hotkey: str | None = None,
    endpoint: str | None = None,
    evaluator_version: str | None = None,
) -> RollingMinerState:
    target_uid = state.uid if uid is None else int(uid)
    target_hotkey = state.hotkey if hotkey is None else str(hotkey)
    target_endpoint = state.endpoint if endpoint is None else str(endpoint)
    target_version = state.evaluator_version if evaluator_version is None else str(evaluator_version)

    if not _identity_matches(state, uid=target_uid, hotkey=target_hotkey):
        return RollingMinerState(
            uid=target_uid,
            hotkey=target_hotkey,
            endpoint=target_endpoint,
            evaluator_version=target_version,
            consecutive_failures=1,
        )

    # Preserve the last successfully evaluated endpoint. If chain discovery has
    # moved to a new endpoint and that endpoint fails, `effective_score` will
    # fail closed on endpoint mismatch until a successful evaluation there.
    return replace(state, consecutive_failures=state.consecutive_failures + 1)


def effective_score(
    state: RollingMinerState,
    *,
    current_uid: int,
    current_hotkey: str,
    current_block: int,
    evaluator_version: str,
    current_endpoint: str | None = None,
    stale_after_blocks: int = 720,
    max_consecutive_failures: int = 2,
) -> float:
    """Return the economically eligible rolling score for the current neuron.

    Fail closed on UID/hotkey identity mismatch, an unevaluated endpoint change,
    evaluator-major drift, stale evidence, or repeated inability to answer.
    """
    if current_block < 0:
        raise ValueError("current_block must be non-negative")
    if stale_after_blocks < 1:
        raise ValueError("stale_after_blocks must be positive")
    if max_consecutive_failures < 1:
        raise ValueError("max_consecutive_failures must be positive")
    if not current_hotkey:
        raise ValueError("current_hotkey is required")
    if not _identity_matches(state, uid=current_uid, hotkey=current_hotkey):
        return 0.0
    if current_endpoint is not None and state.endpoint != current_endpoint:
        return 0.0
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

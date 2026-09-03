from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuditSignals:
    score_jump: float = 0.0
    duplicate_peer_count: int = 0
    consecutive_failures: int = 0
    blocks_since_evaluation: int = 0
    new_miner: bool = False


@dataclass(frozen=True)
class AuditDecision:
    priority: float
    require_deep_evaluation: bool
    reasons: tuple[str, ...]


def decide_audit(
    signals: AuditSignals,
    *,
    score_jump_threshold: float = 0.25,
    stale_blocks_threshold: int = 720,
    failure_threshold: int = 2,
) -> AuditDecision:
    """Convert anti-gaming/operational signals into deep-evaluation priority.

    This is intentionally separate from reward scoring. Suspicion changes how
    much evidence a validator requests; it does not by itself prove a miner is
    malicious or justify economic punishment.
    """
    reasons: list[str] = []
    priority = 0.0

    jump = max(0.0, float(signals.score_jump))
    if jump >= score_jump_threshold:
        reasons.append("sudden_score_jump")
        priority += min(1.0, jump)

    peers = max(0, int(signals.duplicate_peer_count))
    if peers > 0:
        reasons.append("duplicate_semantic_output")
        priority += min(1.0, 0.25 * peers)

    failures = max(0, int(signals.consecutive_failures))
    if failures >= failure_threshold:
        reasons.append("repeated_unavailability")
        priority += min(1.0, 0.25 * failures)

    stale = max(0, int(signals.blocks_since_evaluation))
    if stale >= stale_blocks_threshold:
        reasons.append("stale_evidence")
        priority += min(1.0, stale / max(1, stale_blocks_threshold) * 0.25)

    if signals.new_miner:
        reasons.append("new_miner_exploration")
        priority += 0.25

    priority = min(1.0, priority)
    return AuditDecision(
        priority=priority,
        require_deep_evaluation=bool(reasons),
        reasons=tuple(reasons),
    )

from __future__ import annotations

from consequent.scoring import normalized_weights
from validator.chain_state import read_weight_policy, required_version_key


def build_weight_map(scores_by_uid: dict[int, float]) -> dict[int, float]:
    return normalized_weights(scores_by_uid)


async def plan_weights(*, client, wallet, netuid: int, weights: dict[int, float], version_key: int | None = None):
    """Read live subnet constraints, enforce version gating, then return a non-mutating plan."""
    import bittensor as bt

    policy = await read_weight_policy(client=client, netuid=netuid)
    resolved_version = required_version_key(policy, version_key)
    intent = bt.SetWeights(netuid=netuid, weights=weights, version_key=resolved_version)
    return policy, await client.plan(intent, wallet)


async def submit_weights(*, client, wallet, netuid: int, weights: dict[int, float], version_key: int | None = None):
    """Plan, then submit weights after checking live subnet constraints.

    ``execute`` also re-plans internally in Bittensor v11. The explicit plan here
    is intentional: callers get a non-mutating policy/chain preflight at the
    Consequent boundary before the transaction is allowed to proceed, while the
    SDK's execute-time re-plan remains the final race-safe check.
    """
    import bittensor as bt

    policy = await read_weight_policy(client=client, netuid=netuid)
    resolved_version = required_version_key(policy, version_key)
    intent = bt.SetWeights(netuid=netuid, weights=weights, version_key=resolved_version)
    plan = await client.plan(intent, wallet)
    if not plan.ok:
        raise bt.PolicyError(plan.violations)
    return await client.execute(intent, wallet)

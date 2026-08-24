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
    """Submit weights only after checking the current subnet version gate.

    The Bittensor v11 SetWeights intent performs its own preflight for chain-side
    constraints such as non-zero weight count, clipping, rate limits and
    commit-reveal routing. Consequent additionally reads the subnet policy so
    the required version key cannot be ignored.
    """
    import bittensor as bt

    policy = await read_weight_policy(client=client, netuid=netuid)
    resolved_version = required_version_key(policy, version_key)
    intent = bt.SetWeights(netuid=netuid, weights=weights, version_key=resolved_version)
    return await client.execute(intent, wallet)

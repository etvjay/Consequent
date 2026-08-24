from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SubnetWeightPolicy:
    min_allowed_weights: int
    max_weights_limit: float
    weights_version: int
    weights_rate_limit: int
    commit_reveal_weights_enabled: bool
    commit_reveal_period: int


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


async def read_weight_policy(*, client, netuid: int) -> SubnetWeightPolicy:
    """Read the live subnet constraints that govern validator weight submissions."""
    hp = await client.subnets.subnet_hyperparameters(netuid=netuid)
    if hp is None:
        raise RuntimeError(f"subnet {netuid} does not exist or hyperparameters are unavailable")

    return SubnetWeightPolicy(
        min_allowed_weights=int(hp.min_allowed_weights),
        max_weights_limit=_as_float(hp.max_weights_limit),
        weights_version=int(hp.weights_version),
        weights_rate_limit=int(hp.weights_rate_limit),
        commit_reveal_weights_enabled=bool(hp.commit_reveal_weights_enabled),
        commit_reveal_period=int(hp.commit_reveal_period),
    )


def required_version_key(policy: SubnetWeightPolicy, configured: int | None) -> int:
    """Fail before submission if Consequent is below the subnet's version gate."""
    candidate = 0 if configured is None else int(configured)
    if policy.weights_version > 0 and candidate < policy.weights_version:
        raise RuntimeError(
            f"validator version_key {candidate} is below subnet requirement {policy.weights_version}"
        )
    return candidate

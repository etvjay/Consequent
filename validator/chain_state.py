from __future__ import annotations

from collections.abc import Mapping
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


def _field(record: Any, name: str) -> Any:
    """Read one SDK result field from either mapping or model/object form.

    Bittensor v11 currently exposes subnet hyperparameters as a mapping on the
    local Subtensor path while test fixtures and other SDK surfaces may expose
    attribute-style records. Consequent treats both as valid SDK result shapes
    and fails loudly if the required field is absent.
    """
    if isinstance(record, Mapping):
        if name not in record:
            raise RuntimeError(f"subnet hyperparameters missing required field: {name}")
        return record[name]
    if not hasattr(record, name):
        raise RuntimeError(f"subnet hyperparameters missing required field: {name}")
    return getattr(record, name)


async def read_weight_policy(*, client, netuid: int) -> SubnetWeightPolicy:
    """Read the live subnet constraints that govern validator weight submissions."""
    hp = await client.subnets.subnet_hyperparameters(netuid=netuid)
    if hp is None:
        raise RuntimeError(f"subnet {netuid} does not exist or hyperparameters are unavailable")

    return SubnetWeightPolicy(
        min_allowed_weights=int(_field(hp, "min_allowed_weights")),
        max_weights_limit=_as_float(_field(hp, "max_weights_limit")),
        weights_version=int(_field(hp, "weights_version")),
        weights_rate_limit=int(_field(hp, "weights_rate_limit")),
        commit_reveal_weights_enabled=bool(_field(hp, "commit_reveal_weights_enabled")),
        commit_reveal_period=int(_field(hp, "commit_reveal_period")),
    )


def required_version_key(policy: SubnetWeightPolicy, configured: int | None) -> int:
    """Fail before submission if Consequent is below the subnet's version gate."""
    candidate = 0 if configured is None else int(configured)
    if policy.weights_version > 0 and candidate < policy.weights_version:
        raise RuntimeError(
            f"validator version_key {candidate} is below subnet requirement {policy.weights_version}"
        )
    return candidate

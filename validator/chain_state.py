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


@dataclass(frozen=True)
class SubnetConsensusPolicy:
    tempo: int
    kappa_raw: int
    max_validators: int
    activity_cutoff_factor: int
    effective_activity_cutoff_blocks: int
    bonds_moving_avg: int
    bonds_penalty_raw: int
    yuma_version: int
    liquid_alpha_enabled: bool

    @property
    def kappa(self) -> float:
        return self.kappa_raw / 65535.0

    @property
    def bonds_penalty(self) -> float:
        return self.bonds_penalty_raw / 65535.0


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


def _field_any(record: Any, *names: str) -> Any:
    """Read the first available name from a versioned SDK hyperparameter record."""
    for name in names:
        if isinstance(record, Mapping) and name in record:
            return record[name]
        if not isinstance(record, Mapping) and hasattr(record, name):
            return getattr(record, name)
    joined = ", ".join(names)
    raise RuntimeError(f"subnet hyperparameters missing required field variant: {joined}")


async def _read_hyperparameters(*, client, netuid: int) -> Any:
    hp = await client.subnets.subnet_hyperparameters(netuid=netuid)
    if hp is None:
        raise RuntimeError(f"subnet {netuid} does not exist or hyperparameters are unavailable")
    return hp


async def read_weight_policy(*, client, netuid: int) -> SubnetWeightPolicy:
    """Read the live subnet constraints that govern validator weight submissions."""
    hp = await _read_hyperparameters(client=client, netuid=netuid)

    return SubnetWeightPolicy(
        min_allowed_weights=int(_field(hp, "min_allowed_weights")),
        max_weights_limit=_as_float(_field(hp, "max_weights_limit")),
        weights_version=int(_field(hp, "weights_version")),
        weights_rate_limit=int(_field(hp, "weights_rate_limit")),
        commit_reveal_weights_enabled=bool(_field(hp, "commit_reveal_weights_enabled")),
        commit_reveal_period=int(_field(hp, "commit_reveal_period")),
    )


async def read_consensus_policy(*, client, netuid: int) -> SubnetConsensusPolicy:
    """Read live Yuma/validator parameters that define the economic environment.

    These values belong in Consequent evidence records. They are not constants:
    subnet/root governance and runtime upgrades can change the environment under
    which exactly the same validator score row settles economically.
    """
    hp = await _read_hyperparameters(client=client, netuid=netuid)

    tempo = int(_field(hp, "tempo"))
    activity_factor = int(_field_any(hp, "activity_cutoff_factor", "activity_cutoff_factor_milli"))
    effective_cutoff = max(1, (activity_factor * tempo) // 1000)

    if isinstance(hp, Mapping) and "yuma_version" in hp:
        yuma_version = int(hp["yuma_version"])
    elif not isinstance(hp, Mapping) and hasattr(hp, "yuma_version"):
        yuma_version = int(getattr(hp, "yuma_version"))
    else:
        yuma3 = bool(_field(hp, "yuma3_enabled"))
        yuma_version = 3 if yuma3 else 2

    return SubnetConsensusPolicy(
        tempo=tempo,
        kappa_raw=int(_field(hp, "kappa")),
        max_validators=int(_field(hp, "max_validators")),
        activity_cutoff_factor=activity_factor,
        effective_activity_cutoff_blocks=effective_cutoff,
        bonds_moving_avg=int(_field(hp, "bonds_moving_avg")),
        bonds_penalty_raw=int(_field(hp, "bonds_penalty")),
        yuma_version=yuma_version,
        liquid_alpha_enabled=bool(_field(hp, "liquid_alpha_enabled")),
    )


def remaining_weight_rate_limit_blocks(
    *, current_block: int, last_update: int, rate_limit: int
) -> int:
    """Return how many blocks remain before a validator may update weights.

    The Bittensor runtime rejects a SetWeights update when the number of blocks
    since that UID's last update is less than `weights_rate_limit`. Consequent
    therefore waits on chain state rather than trying to mutate the subnet's
    rate-limit policy.
    """
    current = int(current_block)
    last = int(last_update)
    limit = int(rate_limit)
    if current < 0 or last < 0 or limit < 0:
        raise ValueError("block numbers and weights_rate_limit must be non-negative")
    if last > current:
        raise ValueError("validator last_update cannot be ahead of current block")
    elapsed = current - last
    return max(0, limit - elapsed)


def required_version_key(policy: SubnetWeightPolicy, configured: int | None) -> int:
    """Fail before submission if Consequent is below the subnet's version gate."""
    candidate = 0 if configured is None else int(configured)
    if policy.weights_version > 0 and candidate < policy.weights_version:
        raise RuntimeError(
            f"validator version_key {candidate} is below subnet requirement {policy.weights_version}"
        )
    return candidate

from __future__ import annotations

from dataclasses import dataclass

import pytest

from validator.chain_state import read_weight_policy, required_version_key


@dataclass
class FakeHyperparams:
    min_allowed_weights: int = 3
    max_weights_limit: float = 0.25
    weights_version: int = 7
    weights_rate_limit: int = 100
    commit_reveal_weights_enabled: bool = True
    commit_reveal_period: int = 1


class FakeSubnets:
    async def subnet_hyperparameters(self, *, netuid: int):
        assert netuid == 42
        return FakeHyperparams()


class FakeClient:
    subnets = FakeSubnets()


class FakeMappingSubnets:
    async def subnet_hyperparameters(self, *, netuid: int):
        assert netuid == 42
        return {
            "min_allowed_weights": 1,
            "max_weights_limit": 65535,
            "weights_version": 0,
            "weights_rate_limit": 100,
            "commit_reveal_weights_enabled": True,
            "commit_reveal_period": 1,
        }


class FakeMappingClient:
    subnets = FakeMappingSubnets()


@pytest.mark.asyncio
async def test_read_weight_policy_captures_live_submission_constraints():
    policy = await read_weight_policy(client=FakeClient(), netuid=42)
    assert policy.min_allowed_weights == 3
    assert policy.max_weights_limit == 0.25
    assert policy.weights_version == 7
    assert policy.weights_rate_limit == 100
    assert policy.commit_reveal_weights_enabled is True
    assert policy.commit_reveal_period == 1


@pytest.mark.asyncio
async def test_read_weight_policy_accepts_bittensor_mapping_shape():
    policy = await read_weight_policy(client=FakeMappingClient(), netuid=42)
    assert policy.min_allowed_weights == 1
    assert policy.max_weights_limit == 65535.0
    assert policy.weights_version == 0
    assert policy.weights_rate_limit == 100
    assert policy.commit_reveal_weights_enabled is True
    assert policy.commit_reveal_period == 1


def test_required_version_key_rejects_stale_validator():
    policy = FakeHyperparams()
    with pytest.raises(RuntimeError):
        required_version_key(policy, 6)
    assert required_version_key(policy, 7) == 7
    assert required_version_key(policy, 9) == 9

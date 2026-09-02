from __future__ import annotations

from dataclasses import dataclass

import pytest

from validator.chain_state import (
    read_consensus_policy,
    read_weight_policy,
    remaining_weight_rate_limit_blocks,
    required_version_key,
)


@dataclass
class FakeHyperparams:
    min_allowed_weights: int = 3
    max_weights_limit: float = 0.25
    weights_version: int = 7
    weights_rate_limit: int = 100
    commit_reveal_weights_enabled: bool = True
    commit_reveal_period: int = 1
    tempo: int = 360
    kappa: int = 32767
    max_validators: int = 128
    activity_cutoff_factor: int = 13889
    bonds_moving_avg: int = 900000
    bonds_penalty: int = 65535
    yuma3_enabled: bool = False
    liquid_alpha_enabled: bool = False


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
            "tempo": 360,
            "kappa": 32767,
            "max_validators": 64,
            "activity_cutoff_factor": 13889,
            "bonds_moving_avg": 900000,
            "bonds_penalty": 32768,
            "yuma_version": 3,
            "liquid_alpha_enabled": True,
        }


class FakeRuntimeSubsetSubnets:
    async def subnet_hyperparameters(self, *, netuid: int):
        assert netuid == 42
        # Mirrors the current get_subnet_hyperparams_v3 shape, which does not
        # expose every documented hyperparameter on every runtime.
        return {
            "tempo": 360,
            "kappa": 32767,
            "max_validators": 64,
            "activity_cutoff_factor": 13889,
            "bonds_moving_avg": 900000,
            "yuma_version": 3,
            "liquid_alpha_enabled": False,
        }


class FakeRuntimeSubsetClient:
    subnets = FakeRuntimeSubsetSubnets()


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


@pytest.mark.asyncio
async def test_read_consensus_policy_captures_yuma_environment():
    policy = await read_consensus_policy(client=FakeClient(), netuid=42)
    assert policy.tempo == 360
    assert policy.kappa_raw == 32767
    assert policy.kappa == pytest.approx(32767 / 65535)
    assert policy.max_validators == 128
    assert policy.activity_cutoff_factor == 13889
    assert policy.effective_activity_cutoff_blocks == 5000
    assert policy.bonds_moving_avg == 900000
    assert policy.bonds_penalty_raw == 65535
    assert policy.bonds_penalty == pytest.approx(1.0)
    assert policy.yuma_version == 2
    assert policy.liquid_alpha_enabled is False


@pytest.mark.asyncio
async def test_read_consensus_policy_accepts_v3_mapping_shape():
    policy = await read_consensus_policy(client=FakeMappingClient(), netuid=42)
    assert policy.max_validators == 64
    assert policy.effective_activity_cutoff_blocks == 5000
    assert policy.bonds_penalty == pytest.approx(32768 / 65535)
    assert policy.yuma_version == 3
    assert policy.liquid_alpha_enabled is True


@pytest.mark.asyncio
async def test_read_consensus_policy_preserves_unexposed_optional_bonds_penalty():
    policy = await read_consensus_policy(client=FakeRuntimeSubsetClient(), netuid=42)
    assert policy.yuma_version == 3
    assert policy.bonds_penalty_raw is None
    assert policy.bonds_penalty is None


def test_remaining_weight_rate_limit_blocks_tracks_runtime_rule():
    assert remaining_weight_rate_limit_blocks(current_block=13, last_update=10, rate_limit=100) == 97
    assert remaining_weight_rate_limit_blocks(current_block=110, last_update=10, rate_limit=100) == 0
    assert remaining_weight_rate_limit_blocks(current_block=111, last_update=10, rate_limit=100) == 0


def test_remaining_weight_rate_limit_blocks_rejects_impossible_state():
    with pytest.raises(ValueError):
        remaining_weight_rate_limit_blocks(current_block=9, last_update=10, rate_limit=100)
    with pytest.raises(ValueError):
        remaining_weight_rate_limit_blocks(current_block=10, last_update=10, rate_limit=-1)


def test_required_version_key_rejects_stale_validator():
    policy = FakeHyperparams()
    with pytest.raises(RuntimeError):
        required_version_key(policy, 6)
    assert required_version_key(policy, 7) == 7
    assert required_version_key(policy, 9) == 9

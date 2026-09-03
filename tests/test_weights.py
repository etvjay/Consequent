from __future__ import annotations

from types import SimpleNamespace

import pytest
import bittensor as bt

from validator.weights import submit_weights


class FakeSubnets:
    async def subnet_hyperparameters(self, *, netuid: int):
        assert netuid == 42
        return {
            "min_allowed_weights": 1,
            "max_weights_limit": 65535,
            "weights_version": 0,
            "weights_rate_limit": 100,
            "commit_reveal_weights_enabled": False,
            "commit_reveal_period": 1,
        }


class FakeClient:
    subnets = FakeSubnets()

    def __init__(self, *, plan_ok: bool = True):
        self.plan_ok = plan_ok
        self.calls: list[str] = []

    async def plan(self, intent, wallet):
        self.calls.append("plan")
        return SimpleNamespace(ok=self.plan_ok, violations=["blocked"] if not self.plan_ok else [])

    async def execute(self, intent, wallet):
        self.calls.append("execute")
        return "submitted"


@pytest.mark.asyncio
async def test_submit_weights_plans_before_execute():
    client = FakeClient()
    result = await submit_weights(client=client, wallet=object(), netuid=42, weights={7: 1.0})
    assert result == "submitted"
    assert client.calls == ["plan", "execute"]


@pytest.mark.asyncio
async def test_submit_weights_stops_on_plan_policy_violation():
    client = FakeClient(plan_ok=False)
    with pytest.raises(bt.PolicyError) as raised:
        await submit_weights(client=client, wallet=object(), netuid=42, weights={7: 1.0})
    assert raised.value.violations == ["blocked"]
    assert client.calls == ["plan"]

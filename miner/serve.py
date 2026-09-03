from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ServePlan:
    netuid: int
    ip: str
    port: int
    plan: object


async def plan_serve_axon(*, client, wallet, netuid: int, ip: str, port: int) -> ServePlan:
    """Build a non-mutating ServeAxon plan first.

    Bittensor v11 recommends previewing all mutations with client.plan(...)
    before execution. This helper deliberately separates planning from submit.
    """
    import bittensor as bt

    intent = bt.ServeAxon(netuid=netuid, ip=ip, port=port)
    plan = await client.plan(intent, wallet)
    return ServePlan(netuid=netuid, ip=ip, port=port, plan=plan)


async def execute_serve_axon(*, client, wallet, netuid: int, ip: str, port: int):
    import bittensor as bt

    intent = bt.ServeAxon(netuid=netuid, ip=ip, port=port)
    return await client.execute(intent, wallet)

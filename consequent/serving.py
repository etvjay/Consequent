from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ServePlan:
    netuid: int
    ip: str
    port: int


def build_serve_axon(*, netuid: int, ip: str, port: int):
    """Build the Bittensor v11 endpoint-publication intent.

    Construction is side-effect free. Call ``submit_serve_axon`` only when an
    operator explicitly intends to mutate chain state.
    """
    import bittensor as bt

    return bt.ServeAxon(netuid=netuid, ip=ip, port=port)


async def plan_serve_axon(*, client, wallet, netuid: int, ip: str, port: int):
    intent = build_serve_axon(netuid=netuid, ip=ip, port=port)
    return await client.plan(intent, wallet)


async def submit_serve_axon(*, client, wallet, netuid: int, ip: str, port: int):
    intent = build_serve_axon(netuid=netuid, ip=ip, port=port)
    return await client.execute(intent, wallet)

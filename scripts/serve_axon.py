from __future__ import annotations

import argparse
import asyncio

import bittensor as bt

from consequent.network import NetworkSettings
from miner.serve import execute_serve_axon, plan_serve_axon


async def main() -> None:
    parser = argparse.ArgumentParser(description="Plan or execute Consequent ServeAxon publication")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="submit the ServeAxon transaction; without this flag only a plan is produced",
    )
    args = parser.parse_args()

    settings = NetworkSettings.from_env()
    if not settings.network_mode:
        raise SystemExit("set CONSEQUENT_NETWORK_MODE=1")
    if settings.netuid is None:
        raise SystemExit("CONSEQUENT_NETUID is required")
    if not settings.advertised_ip:
        raise SystemExit("CONSEQUENT_ADVERTISED_IP is required")

    wallet = settings.wallet()
    async with bt.Subtensor(network=settings.network) as client:
        planned = await plan_serve_axon(
            client=client,
            wallet=wallet,
            netuid=settings.netuid,
            ip=settings.advertised_ip,
            port=settings.advertised_port,
        )
        print(planned.plan)

        if not args.execute:
            print("\nPlan only. Re-run with --execute to submit after reviewing the plan.")
            return

        result = await execute_serve_axon(
            client=client,
            wallet=wallet,
            netuid=settings.netuid,
            ip=settings.advertised_ip,
            port=settings.advertised_port,
        )
        print(result)
        if hasattr(result, "success") and not result.success:
            raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())

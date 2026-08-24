from __future__ import annotations

import argparse
import asyncio

from consequent.network import NetworkSettings
from miner.serve import execute_serve_axon, plan_serve_axon


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plan or publish the Consequent miner endpoint")
    parser.add_argument("--execute", action="store_true", help="submit ServeAxon after planning")
    return parser.parse_args()


async def main() -> None:
    import bittensor as bt

    args = parse_args()
    settings = NetworkSettings.from_env()
    if settings.netuid is None:
        raise SystemExit("CONSEQUENT_NETUID is required")
    if not settings.advertised_ip:
        raise SystemExit("CONSEQUENT_ADVERTISED_IP is required")

    wallet = settings.wallet()
    async with bt.Subtensor(settings.network) as client:
        plan = await plan_serve_axon(
            client=client,
            wallet=wallet,
            netuid=settings.netuid,
            ip=settings.advertised_ip,
            port=settings.advertised_port,
        )
        print(plan.plan)
        if not args.execute:
            print("dry-run only; rerun with --execute to submit ServeAxon")
            return

        result = await execute_serve_axon(
            client=client,
            wallet=wallet,
            netuid=settings.netuid,
            ip=settings.advertised_ip,
            port=settings.advertised_port,
        )
        print(result)
        if not result.success:
            raise SystemExit(f"ServeAxon failed: {result.error.code}: {result.error.remediation}")


if __name__ == "__main__":
    asyncio.run(main())

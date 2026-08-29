from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

import bittensor as bt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Wait for a Bittensor Subtensor endpoint to become chain-ready without assuming a bootstrap netuid."
    )
    parser.add_argument("--network", default="local")
    parser.add_argument("--attempts", type=int, default=90)
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    parser.add_argument("--min-block", type=int, default=1)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


async def probe(network: str) -> int:
    """Return the current block from the chain-level Subtensor API.

    Readiness deliberately does not query a subnet metagraph. The official
    localnet image/tag may change its bootstrap subnet topology independently
    of whether its RPC endpoint and consensus are healthy.
    """
    async with bt.Subtensor(network) as client:
        return int(await client.block())


async def main() -> None:
    args = parse_args()
    if args.attempts <= 0:
        raise SystemExit("--attempts must be positive")
    if args.poll_seconds <= 0:
        raise SystemExit("--poll-seconds must be positive")
    if args.min_block < 0:
        raise SystemExit("--min-block must be non-negative")

    last_error: str | None = None
    last_block: int | None = None
    for attempt in range(1, args.attempts + 1):
        try:
            last_block = await probe(args.network)
            if last_block >= args.min_block:
                evidence = {
                    "state": "SUBTENSOR_CHAIN_READY",
                    "network": args.network,
                    "block": last_block,
                    "attempt": attempt,
                    "min_block": args.min_block,
                }
                rendered = json.dumps(evidence, indent=2, sort_keys=True)
                print(rendered)
                if args.output:
                    args.output.write_text(rendered + "\n", encoding="utf-8")
                return
        except Exception as exc:  # readiness loop intentionally records transient RPC errors
            last_error = f"{type(exc).__name__}: {exc}"
        await asyncio.sleep(args.poll_seconds)

    failure = {
        "state": "SUBTENSOR_CHAIN_NOT_READY",
        "network": args.network,
        "attempts": args.attempts,
        "min_block": args.min_block,
        "last_block": last_block,
        "last_error": last_error,
    }
    rendered = json.dumps(failure, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    raise SystemExit("Subtensor RPC/consensus did not become ready within the bounded probe window")


if __name__ == "__main__":
    asyncio.run(main())

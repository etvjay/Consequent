from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

import bittensor as bt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Wait for a Bittensor Subtensor endpoint to become chain-ready "
            "without assuming any bootstrap subnet topology."
        )
    )
    parser.add_argument("--network", default="local")
    parser.add_argument("--attempts", type=int, default=90)
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    parser.add_argument("--min-block", type=int, default=1)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


async def probe(network: str) -> int:
    async with bt.Subtensor(network) as client:
        return int(await client.block())


def emit(payload: dict[str, object], output: Path | None) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    print(rendered)
    if output is not None:
        output.write_text(rendered + "\n", encoding="utf-8")


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
                emit(
                    {
                        "state": "SUBTENSOR_CHAIN_READY",
                        "network": args.network,
                        "block": last_block,
                        "attempt": attempt,
                        "min_block": args.min_block,
                    },
                    args.output,
                )
                return
        except Exception as exc:  # readiness intentionally tolerates transient RPC errors
            last_error = f"{type(exc).__name__}: {exc}"

        await asyncio.sleep(args.poll_seconds)

    emit(
        {
            "state": "SUBTENSOR_CHAIN_NOT_READY",
            "network": args.network,
            "attempts": args.attempts,
            "min_block": args.min_block,
            "last_block": last_block,
            "last_error": last_error,
        },
        args.output,
    )
    raise SystemExit("Subtensor RPC/consensus did not become ready within the bounded probe window")


if __name__ == "__main__":
    asyncio.run(main())

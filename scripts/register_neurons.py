from __future__ import annotations

import argparse
import asyncio
import json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register Consequent neuron hotkeys with Bittensor v11 intents")
    parser.add_argument("--netuid", type=int, required=True)
    parser.add_argument("--network", default="local")
    parser.add_argument("--wallet", action="append", required=True, help="wallet name to register; may be repeated")
    return parser.parse_args()


async def main() -> None:
    import bittensor as bt

    args = parse_args()
    results: list[dict[str, object]] = []

    async with bt.Subtensor(args.network) as client:
        for name in args.wallet:
            wallet = bt.Wallet(name=name, hotkey="default")
            intent = bt.BurnedRegister(netuid=args.netuid)
            result = await client.execute(intent, wallet)
            entry = {
                "wallet": name,
                "hotkey": wallet.hotkey.ss58_address,
                "success": bool(result.success),
                "block_hash": getattr(result, "block_hash", None),
                "extrinsic_id": getattr(result, "extrinsic_id", None),
                "error_code": getattr(getattr(result, "error", None), "code", None),
                "error_name": getattr(getattr(result, "error", None), "name", None),
                "remediation": getattr(getattr(result, "error", None), "remediation", None),
            }
            results.append(entry)
            if not result.success:
                print(json.dumps(results, indent=2, default=str))
                raise SystemExit(f"registration failed for {name}: {entry['error_code']} {entry['error_name']}")

    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())

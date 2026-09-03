from __future__ import annotations

import argparse
import asyncio
import json

from consequent.network import NetworkSettings, served_neurons


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe Consequent registration and metagraph discovery")
    parser.add_argument("--require-registered", action="store_true")
    parser.add_argument("--require-served-miner", action="store_true")
    return parser.parse_args()


async def main() -> None:
    import bittensor as bt

    args = parse_args()
    settings = NetworkSettings.from_env()
    if settings.netuid is None:
        raise SystemExit("CONSEQUENT_NETUID is required")

    wallet = settings.wallet()
    async with bt.Subtensor(settings.network) as client:
        mg = await client.subnets.metagraph(netuid=settings.netuid)

    self_neuron = None
    try:
        self_neuron = mg.by_hotkey(wallet.hotkey.ss58_address)
    except Exception:
        pass

    miners = served_neurons(mg, exclude_hotkeys=(wallet.hotkey.ss58_address,))
    payload = {
        "network": settings.network,
        "netuid": settings.netuid,
        "hotkey": wallet.hotkey.ss58_address,
        "registered": self_neuron is not None,
        "uid": int(self_neuron.uid) if self_neuron is not None else None,
        "served_miners": [
            {"uid": n.uid, "hotkey": n.hotkey, "endpoint": n.endpoint}
            for n in miners
        ],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))

    if args.require_registered and self_neuron is None:
        raise SystemExit("configured Consequent validator hotkey is not registered on the target subnet")
    if args.require_served_miner and not miners:
        raise SystemExit("no discoverable served Consequent miner exists on the target subnet")


if __name__ == "__main__":
    asyncio.run(main())

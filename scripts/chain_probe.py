from __future__ import annotations

import asyncio
import json

from consequent.network import NetworkSettings, served_neurons


async def main() -> None:
    import bittensor as bt

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

    payload = {
        "network": settings.network,
        "netuid": settings.netuid,
        "hotkey": wallet.hotkey.ss58_address,
        "registered": self_neuron is not None,
        "uid": int(self_neuron.uid) if self_neuron is not None else None,
        "served_miners": [
            {"uid": n.uid, "hotkey": n.hotkey, "endpoint": n.endpoint}
            for n in served_neurons(mg, exclude_hotkeys=(wallet.hotkey.ss58_address,))
        ],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())

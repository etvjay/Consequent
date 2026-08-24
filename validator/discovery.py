from __future__ import annotations

from consequent.network import served_neurons
from validator.runner import MinerEndpoint


async def discover_miners(*, client, netuid: int, exclude_hotkeys: tuple[str, ...] = ()) -> list[MinerEndpoint]:
    """Discover currently served miners from Bittensor metagraph state."""
    metagraph = await client.subnets.metagraph(netuid=netuid)
    return [
        MinerEndpoint(uid=n.uid, hotkey=n.hotkey, endpoint=n.endpoint)
        for n in served_neurons(metagraph, exclude_hotkeys=exclude_hotkeys)
    ]

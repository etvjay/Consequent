from __future__ import annotations

import asyncio
import json
import os

import bittensor as bt

from consequent.m0_fixture import m0_challenge
from consequent.network import NetworkSettings
from validator.discovery import discover_miners
from validator.query import query_miner


async def main() -> None:
    settings = NetworkSettings.from_env()
    if settings.netuid is None:
        raise SystemExit("CONSEQUENT_NETUID is required")

    old_endpoint = os.environ.get("CONSEQUENT_OLD_ENDPOINT")
    if not old_endpoint:
        raise SystemExit("CONSEQUENT_OLD_ENDPOINT is required")

    validator_wallet = settings.wallet()
    miner_wallet = bt.Wallet(name="consequent-churn-miner", hotkey="default")
    miner_hotkey = miner_wallet.hotkey.ss58_address

    async with bt.Subtensor(settings.network) as client:
        miners = await discover_miners(
            client=client,
            netuid=settings.netuid,
            exclude_hotkeys=(validator_wallet.hotkey.ss58_address,),
        )

    target = next((m for m in miners if m.hotkey == miner_hotkey), None)
    if target is None:
        raise SystemExit("churn miner missing from refreshed metagraph discovery")
    if target.endpoint == old_endpoint:
        raise SystemExit("refreshed discovery still exposes the old served endpoint")

    challenge = m0_challenge().model_copy(update={"challenge_id": "m2-churn-refresh-001"})
    response = await query_miner(
        wallet=validator_wallet,
        endpoint=target.endpoint,
        miner_hotkey=target.hotkey,
        challenge=challenge,
    )
    if response.challenge_id != challenge.challenge_id:
        raise SystemExit("new endpoint response failed challenge binding")

    print(
        json.dumps(
            {
                "state": "M2_CHAIN_ENDPOINT_CHURN_PASS",
                "netuid": settings.netuid,
                "miner_uid": target.uid,
                "miner_hotkey": target.hotkey,
                "old_endpoint": old_endpoint,
                "new_endpoint": target.endpoint,
                "challenge_id": response.challenge_id,
                "rule_count": len(response.patch.rules),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())

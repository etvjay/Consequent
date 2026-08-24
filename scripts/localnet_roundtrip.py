from __future__ import annotations

import asyncio
import json

import bittensor as bt

from consequent.models import ExecutionEpisode, MemoryFormationRequest, TaskFamily
from consequent.network import NetworkSettings
from validator.discovery import discover_miners
from validator.query import query_miner


async def main() -> None:
    settings = NetworkSettings.from_env()
    if settings.netuid is None:
        raise SystemExit("CONSEQUENT_NETUID is required")

    validator_wallet = settings.wallet()
    miner_wallet = bt.Wallet(
        name="consequent-miner",
        hotkey="default",
    )
    miner_hotkey = miner_wallet.hotkey.ss58_address

    async with bt.Subtensor(settings.network) as client:
        miners = await discover_miners(
            client=client,
            netuid=settings.netuid,
            exclude_hotkeys=(validator_wallet.hotkey.ss58_address,),
        )

    target = next((m for m in miners if m.hotkey == miner_hotkey), None)
    if target is None:
        raise SystemExit(f"registered miner {miner_hotkey} has no discoverable served endpoint")

    challenge = MemoryFormationRequest(
        challenge_id="localnet-auth-roundtrip-001",
        task_family=TaskFamily.API_PROTOCOL,
        episodes=[
            ExecutionEpisode(
                episode_id="episode-localnet-001",
                family=TaskFamily.API_PROTOCOL,
                features={"operation": "retry", "idempotent": False},
                attempted_action="retry_with_new_key",
                observed_outcome="duplicate_side_effect",
                better_action="reuse_original_idempotency_key",
            )
        ],
        memory_budget=4,
        policy_constraints=["do_not_expand_capabilities"],
    )

    response = await query_miner(
        wallet=validator_wallet,
        endpoint=target.endpoint,
        miner_hotkey=target.hotkey,
        challenge=challenge,
    )

    if response.challenge_id != challenge.challenge_id:
        raise SystemExit("challenge binding failed")
    if not response.patch.rules:
        raise SystemExit("miner returned no memory rules")

    print(
        json.dumps(
            {
                "state": "LOCAL_NETWORK_AUTH_ROUNDTRIP_PASS",
                "netuid": settings.netuid,
                "miner_uid": target.uid,
                "miner_hotkey": target.hotkey,
                "endpoint": target.endpoint,
                "challenge_id": response.challenge_id,
                "patch_version": response.patch.patch_version,
                "rule_count": len(response.patch.rules),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())

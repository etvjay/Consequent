from __future__ import annotations

import argparse
import asyncio
import json
import sys

import bittensor as bt

from validator.chain_state import read_weight_policy, remaining_weight_rate_limit_blocks
from validator.weights import submit_weights


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Submit and verify one Consequent localnet weight row")
    parser.add_argument("--network", default="local")
    parser.add_argument("--netuid", type=int, required=True)
    parser.add_argument("--wallet", default="consequent-owner")
    parser.add_argument("--hotkey", default="default")
    parser.add_argument("--target-hotkey", required=True)
    parser.add_argument("--poll-seconds", type=float, default=12.5)
    parser.add_argument("--max-wait-blocks", type=int, default=120)
    return parser.parse_args()


async def wait_until_weight_update_allowed(
    *, client, netuid: int, validator_hotkey: str, rate_limit: int, poll_seconds: float, max_wait_blocks: int
):
    starting_remaining: int | None = None
    while True:
        mg = await client.subnets.metagraph(netuid=netuid)
        try:
            validator = mg.by_hotkey(validator_hotkey)
        except Exception as exc:
            raise SystemExit(f"validator hotkey missing while waiting for weight window: {exc}") from exc

        current_block = int(mg.block)
        last_update = int(validator.last_update)
        remaining = remaining_weight_rate_limit_blocks(
            current_block=current_block,
            last_update=last_update,
            rate_limit=rate_limit,
        )
        if starting_remaining is None:
            starting_remaining = remaining
            if starting_remaining > max_wait_blocks:
                raise SystemExit(
                    f"weight window requires {starting_remaining} blocks, above max-wait-blocks={max_wait_blocks}"
                )

        print(
            json.dumps(
                {
                    "event": "WEIGHT_RATE_LIMIT_WAIT",
                    "current_block": current_block,
                    "last_update": last_update,
                    "rate_limit": rate_limit,
                    "remaining_blocks": remaining,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
            flush=True,
        )
        if remaining == 0:
            return validator, current_block, starting_remaining
        await asyncio.sleep(poll_seconds)


async def main() -> None:
    args = parse_args()
    wallet = bt.Wallet(name=args.wallet, hotkey=args.hotkey)

    async with bt.Subtensor(args.network) as client:
        mg = await client.subnets.metagraph(netuid=args.netuid)
        try:
            target = mg.by_hotkey(args.target_hotkey)
        except Exception as exc:
            raise SystemExit(f"target hotkey missing from metagraph: {exc}") from exc

        policy = await read_weight_policy(client=client, netuid=args.netuid)
        validator, legal_block, waited_blocks = await wait_until_weight_update_allowed(
            client=client,
            netuid=args.netuid,
            validator_hotkey=wallet.hotkey.ss58_address,
            rate_limit=policy.weights_rate_limit,
            poll_seconds=args.poll_seconds,
            max_wait_blocks=args.max_wait_blocks,
        )

        weights = {int(target.uid): 1.0}
        result = await submit_weights(
            client=client,
            wallet=wallet,
            netuid=args.netuid,
            weights=weights,
            version_key=policy.weights_version,
        )
        if not result.success:
            raise SystemExit(
                f"SetWeights failed: {result.error.code} {result.error.name}: {result.error.remediation}"
            )

        observed: dict[int, float] | None = None
        for _ in range(max(3, int(policy.commit_reveal_period) + 3)):
            matrix = await client.weights.weights(netuid=args.netuid)
            row = matrix.get(int(validator.uid), {})
            if float(row.get(int(target.uid), 0.0)) > 0.0:
                observed = row
                break
            await asyncio.sleep(args.poll_seconds)

        if observed is None:
            raise SystemExit("SetWeights submitted but target weight was not observable within bounded read-back window")

        print(
            json.dumps(
                {
                    "state": "LOCALNET_SET_WEIGHTS_READBACK_PASS",
                    "netuid": args.netuid,
                    "validator_uid": int(validator.uid),
                    "target_uid": int(target.uid),
                    "target_weight": float(observed[int(target.uid)]),
                    "policy": policy.__dict__,
                    "legal_submission_block": legal_block,
                    "initial_remaining_rate_limit_blocks": waited_blocks,
                    "block_hash": getattr(result, "block_hash", None),
                    "extrinsic_id": getattr(result, "extrinsic_id", None),
                },
                indent=2,
                sort_keys=True,
                default=str,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())

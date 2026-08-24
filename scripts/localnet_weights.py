from __future__ import annotations

import argparse
import asyncio
import json

import bittensor as bt

from validator.chain_state import read_weight_policy
from validator.weights import submit_weights


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Submit and verify one Consequent localnet weight row")
    parser.add_argument("--network", default="local")
    parser.add_argument("--netuid", type=int, required=True)
    parser.add_argument("--wallet", default="consequent-owner")
    parser.add_argument("--hotkey", default="default")
    parser.add_argument("--target-hotkey", required=True)
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    wallet = bt.Wallet(name=args.wallet, hotkey=args.hotkey)

    async with bt.Subtensor(args.network) as client:
        mg = await client.subnets.metagraph(netuid=args.netuid)
        try:
            validator = mg.by_hotkey(wallet.hotkey.ss58_address)
            target = mg.by_hotkey(args.target_hotkey)
        except Exception as exc:
            raise SystemExit(f"validator/target hotkey missing from metagraph: {exc}") from exc

        policy = await read_weight_policy(client=client, netuid=args.netuid)
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

        # Timelock commit-reveal may make the public row visible later than the
        # submission block, so poll boundedly by chain blocks instead of assuming
        # immediate plaintext visibility.
        observed: dict[int, float] | None = None
        for _ in range(max(3, int(policy.commit_reveal_period) + 3)):
            matrix = await client.weights.weights(netuid=args.netuid)
            row = matrix.get(int(validator.uid), {})
            if float(row.get(int(target.uid), 0.0)) > 0.0:
                observed = row
                break
            await asyncio.sleep(13)

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

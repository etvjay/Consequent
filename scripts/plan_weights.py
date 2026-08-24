from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

import bittensor as bt

from consequent.network import NetworkSettings
from validator.weights import build_weight_map, plan_weights


async def main() -> None:
    parser = argparse.ArgumentParser(description="Create a non-mutating Consequent SetWeights plan")
    parser.add_argument("scores_json", type=Path, help="JSON object mapping UID strings to Consequent scores")
    parser.add_argument("--version-key", type=int, default=None)
    args = parser.parse_args()

    settings = NetworkSettings.from_env()
    if not settings.network_mode or settings.netuid is None:
        raise SystemExit("set CONSEQUENT_NETWORK_MODE=1 and CONSEQUENT_NETUID")

    raw = json.loads(args.scores_json.read_text())
    scores = {int(uid): float(score) for uid, score in raw.items()}
    weights = build_weight_map(scores)
    wallet = settings.wallet()

    async with bt.Subtensor(settings.network) as client:
        policy, plan = await plan_weights(
            client=client,
            wallet=wallet,
            netuid=settings.netuid,
            weights=weights,
            version_key=args.version_key,
        )
        print(json.dumps({"weights": weights, "policy": policy.__dict__}, indent=2, sort_keys=True))
        print("\n--- SetWeights plan (non-mutating) ---")
        print(plan)


if __name__ == "__main__":
    asyncio.run(main())

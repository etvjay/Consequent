from __future__ import annotations

import argparse
import asyncio
import json
import sys

import bittensor as bt

from consequent.m0_fixture import m0_challenge, m0_hidden_tasks
from consequent.network import NetworkSettings
from validator.chain_state import read_weight_policy, remaining_weight_rate_limit_blocks
from validator.discovery import discover_miners
from validator.runner import evaluate_round
from validator.weights import submit_weights

EXPECTED = {
    "no_memory",
    "irrelevant_memory",
    "overfit_memory",
    "useful_generalizing_memory",
    "harmful_memory",
    "policy_violating_memory",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one six-miner Consequent competition and settle the resulting weights on chain"
    )
    parser.add_argument("--poll-seconds", type=float, default=12.5)
    parser.add_argument("--max-wait-blocks", type=int, default=120)
    return parser.parse_args()


async def wait_until_weight_update_allowed(
    *,
    client,
    netuid: int,
    validator_hotkey: str,
    rate_limit: int,
    poll_seconds: float,
    max_wait_blocks: int,
) -> tuple[int, int]:
    starting_remaining: int | None = None
    while True:
        mg = await client.subnets.metagraph(netuid=netuid)
        try:
            validator = mg.by_hotkey(validator_hotkey)
        except Exception as exc:
            raise SystemExit(f"validator hotkey missing while waiting for weight window: {exc}") from exc

        current_block = int(mg.block)
        remaining = remaining_weight_rate_limit_blocks(
            current_block=current_block,
            last_update=int(validator.last_update),
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
                    "event": "M1_WEIGHT_RATE_LIMIT_WAIT",
                    "current_block": current_block,
                    "last_update": int(validator.last_update),
                    "rate_limit": rate_limit,
                    "remaining_blocks": remaining,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
            flush=True,
        )
        if remaining == 0:
            return current_block, starting_remaining
        await asyncio.sleep(poll_seconds)


async def main() -> None:
    args = parse_args()
    settings = NetworkSettings.from_env()
    if settings.netuid is None:
        raise SystemExit("CONSEQUENT_NETUID is required")

    wallet = settings.wallet()

    async with bt.Subtensor(settings.network) as client:
        miners = await discover_miners(
            client=client,
            netuid=settings.netuid,
            exclude_hotkeys=(wallet.hotkey.ss58_address,),
        )
        if len(miners) != 6:
            raise SystemExit(f"M1 requires exactly 6 discoverable miners, found {len(miners)}")

        reports, weights = await evaluate_round(
            wallet=wallet,
            miners=miners,
            challenge=m0_challenge(),
            hidden_tasks=m0_hidden_tasks(),
        )

        by_strategy: dict[str, dict[str, object]] = {}
        for uid, report in reports.items():
            strategy = report.get("miner_strategy")
            if not isinstance(strategy, str):
                continue
            by_strategy[strategy] = {
                "uid": int(uid),
                "hotkey": report.get("miner_hotkey"),
                "score": float(report.get("score", 0.0)),
                "weight": float(weights.get(uid, 0.0)),
                "hard_veto": bool(report.get("hard_veto", False)),
                "mean_uplift": float(report.get("mean_uplift", 0.0)),
                "regression_rate": float(report.get("regression_rate", 0.0)),
                "policy_violations": int(report.get("policy_violations", 0)),
            }

        missing = EXPECTED - set(by_strategy)
        if missing:
            raise SystemExit(f"missing expected M1 miner strategies: {sorted(missing)}")

        useful = by_strategy["useful_generalizing_memory"]
        overfit = by_strategy["overfit_memory"]
        no_memory = by_strategy["no_memory"]
        irrelevant = by_strategy["irrelevant_memory"]
        harmful = by_strategy["harmful_memory"]
        policy_bad = by_strategy["policy_violating_memory"]

        checks = {
            "useful_beats_overfit": useful["score"] > overfit["score"],
            "overfit_beats_no_memory": overfit["score"] > no_memory["score"],
            "no_memory_not_rewarded": no_memory["weight"] == 0.0,
            "irrelevant_not_rewarded": irrelevant["weight"] == 0.0,
            "harmful_not_rewarded": harmful["weight"] == 0.0,
            "policy_bad_vetoed": policy_bad["hard_veto"] is True and policy_bad["weight"] == 0.0,
            "useful_has_top_weight": useful["weight"] == max(v["weight"] for v in by_strategy.values()),
            "weights_normalized": abs(sum(weights.values()) - 1.0) < 1e-9,
        }
        if not all(checks.values()):
            raise SystemExit("M1 competitive ordering failed: " + json.dumps(checks, sort_keys=True))

        policy = await read_weight_policy(client=client, netuid=settings.netuid)
        legal_block, initial_remaining = await wait_until_weight_update_allowed(
            client=client,
            netuid=settings.netuid,
            validator_hotkey=wallet.hotkey.ss58_address,
            rate_limit=policy.weights_rate_limit,
            poll_seconds=args.poll_seconds,
            max_wait_blocks=args.max_wait_blocks,
        )

        result = await submit_weights(
            client=client,
            wallet=wallet,
            netuid=settings.netuid,
            weights=weights,
            version_key=policy.weights_version,
        )
        if not result.success:
            raise SystemExit(
                f"M1 SetWeights failed: {result.error.code} {result.error.name}: {result.error.remediation}"
            )

        mg = await client.subnets.metagraph(netuid=settings.netuid)
        validator = mg.by_hotkey(wallet.hotkey.ss58_address)

        observed: dict[int, float] | None = None
        for _ in range(max(3, int(policy.commit_reveal_period) + 3)):
            matrix = await client.weights.weights(netuid=settings.netuid)
            row = matrix.get(int(validator.uid), {})
            positive_expected = {int(uid): float(weight) for uid, weight in weights.items() if weight > 0}
            if positive_expected and all(float(row.get(uid, 0.0)) > 0 for uid in positive_expected):
                observed = {int(uid): float(value) for uid, value in row.items()}
                break
            await asyncio.sleep(args.poll_seconds)

        if observed is None:
            raise SystemExit("M1 SetWeights submitted but competitive positive weights were not observable")

        expected_positive = {int(uid): float(weight) for uid, weight in weights.items() if weight > 0}
        observed_positive = {uid: float(observed.get(uid, 0.0)) for uid in expected_positive}

        payload = {
            "state": "M1_CHAIN_COMPETITION_PASS",
            "netuid": settings.netuid,
            "validator_uid": int(validator.uid),
            "validator_hotkey": wallet.hotkey.ss58_address,
            "miner_count": len(miners),
            "checks": checks,
            "strategies": by_strategy,
            "computed_weights": {str(uid): float(value) for uid, value in sorted(weights.items())},
            "observed_positive_weights": {str(uid): value for uid, value in sorted(observed_positive.items())},
            "legal_submission_block": legal_block,
            "initial_remaining_rate_limit_blocks": initial_remaining,
            "policy": policy.__dict__,
            "block_hash": getattr(result, "block_hash", None),
            "extrinsic_id": getattr(result, "extrinsic_id", None),
        }
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    asyncio.run(main())

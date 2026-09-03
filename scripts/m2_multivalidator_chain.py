from __future__ import annotations

import argparse
import asyncio
import json
import sys

import bittensor as bt

from consequent.network import NetworkSettings
from consequent.validator_dispersion import private_holdouts
from validator.chain_state import read_consensus_policy, read_weight_policy, remaining_weight_rate_limit_blocks
from validator.discovery import discover_miners
from validator.runner import evaluate_round
from validator.weights import submit_weights


async def wait_until_weight_update_allowed(
    *, client, netuid: int, validator_hotkey: str, rate_limit: int, poll_seconds: float, max_wait_blocks: int
) -> tuple[int, int]:
    starting_remaining: int | None = None
    while True:
        mg = await client.subnets.metagraph(netuid=netuid)
        neuron = mg.by_hotkey(validator_hotkey)
        remaining = remaining_weight_rate_limit_blocks(
            current_block=int(mg.block),
            last_update=int(neuron.last_update),
            rate_limit=rate_limit,
        )
        if starting_remaining is None:
            starting_remaining = remaining
            if remaining > max_wait_blocks:
                raise SystemExit(
                    f"weight window requires {remaining} blocks, above max-wait-blocks={max_wait_blocks}"
                )
        if remaining == 0:
            return int(mg.block), int(starting_remaining)
        await asyncio.sleep(poll_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one independently seeded Consequent validator and settle its row on local Subtensor.")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--poll-seconds", type=float, default=12.5)
    parser.add_argument("--max-wait-blocks", type=int, default=120)
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    settings = NetworkSettings.from_env()
    if settings.netuid is None:
        raise SystemExit("CONSEQUENT_NETUID is required")

    wallet = settings.wallet()
    async with bt.Subtensor(settings.network) as client:
        mg = await client.subnets.metagraph(netuid=settings.netuid)
        validator = mg.by_hotkey(wallet.hotkey.ss58_address)
        if not bool(validator.validator_permit):
            raise SystemExit(
                f"validator uid={int(validator.uid)} hotkey={wallet.hotkey.ss58_address} has no validator permit"
            )

        miners = await discover_miners(
            client=client,
            netuid=settings.netuid,
            exclude_hotkeys=(wallet.hotkey.ss58_address,),
        )
        if len(miners) != 6:
            raise SystemExit(f"M2-V1 requires exactly six served miners, found {len(miners)}")

        reports, weights = await evaluate_round(
            wallet=wallet,
            miners=miners,
            challenge=__import__("consequent.m0_fixture", fromlist=["m0_challenge"]).m0_challenge(),
            hidden_tasks=private_holdouts(args.seed),
        )

        useful = [
            (uid, report) for uid, report in reports.items()
            if report.get("miner_strategy") == "useful_generalizing_memory"
        ]
        overfit = [
            (uid, report) for uid, report in reports.items()
            if report.get("miner_strategy") == "overfit_memory"
        ]
        policy_bad = [
            (uid, report) for uid, report in reports.items()
            if report.get("miner_strategy") == "policy_violating_memory"
        ]
        if len(useful) != 1 or len(overfit) != 1 or len(policy_bad) != 1:
            raise SystemExit("expected canonical six-miner strategy population")

        useful_uid, useful_report = useful[0]
        overfit_uid, overfit_report = overfit[0]
        policy_uid, policy_report = policy_bad[0]
        checks = {
            "useful_top": float(weights[useful_uid]) == max(float(v) for v in weights.values()),
            "useful_beats_overfit": float(useful_report.get("score", 0.0)) > float(overfit_report.get("score", 0.0)),
            "policy_zero": float(weights[policy_uid]) == 0.0,
            "policy_veto_or_admission_reject": bool(policy_report.get("hard_veto", False)) or not bool(policy_report.get("admitted", True)),
            "weights_normalized": abs(sum(float(v) for v in weights.values()) - 1.0) < 1e-9,
        }
        if not all(checks.values()):
            raise SystemExit("M2-V1 validator row failed: " + json.dumps(checks, sort_keys=True))

        weight_policy = await read_weight_policy(client=client, netuid=settings.netuid)
        consensus_policy = await read_consensus_policy(client=client, netuid=settings.netuid)
        if weight_policy.commit_reveal_weights_enabled:
            raise SystemExit("M2-V1 expects commit-reveal disabled; M2-V2 is the separate CR-on proof")

        legal_block, starting_remaining = await wait_until_weight_update_allowed(
            client=client,
            netuid=settings.netuid,
            validator_hotkey=wallet.hotkey.ss58_address,
            rate_limit=weight_policy.weights_rate_limit,
            poll_seconds=args.poll_seconds,
            max_wait_blocks=args.max_wait_blocks,
        )
        result = await submit_weights(
            client=client,
            wallet=wallet,
            netuid=settings.netuid,
            weights=weights,
            version_key=weight_policy.weights_version,
        )
        if not result.success:
            raise SystemExit(
                f"M2-V1 SetWeights failed: {result.error.code} {result.error.name}: {result.error.remediation}"
            )

        matrix = await client.weights.weights(netuid=settings.netuid)
        row = {int(uid): float(value) for uid, value in matrix.get(int(validator.uid), {}).items()}
        positive_expected = {int(uid): float(value) for uid, value in weights.items() if float(value) > 0.0}
        if not all(float(row.get(uid, 0.0)) > 0.0 for uid in positive_expected):
            raise SystemExit("submitted row not observable after SetWeights")

        print(json.dumps({
            "state": "M2_CHAIN_INDEPENDENT_VALIDATOR_PASS",
            "seed": args.seed,
            "validator_uid": int(validator.uid),
            "validator_hotkey": wallet.hotkey.ss58_address,
            "validator_permit": bool(validator.validator_permit),
            "checks": checks,
            "computed_weights": {str(uid): float(value) for uid, value in sorted(weights.items())},
            "observed_weights": {str(uid): float(value) for uid, value in sorted(row.items())},
            "legal_submission_block": legal_block,
            "initial_remaining_rate_limit_blocks": starting_remaining,
            "weight_policy": weight_policy.__dict__,
            "consensus_policy": consensus_policy.__dict__,
            "block_hash": getattr(result, "block_hash", None),
            "extrinsic_id": getattr(result, "extrinsic_id", None),
        }, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    asyncio.run(main())

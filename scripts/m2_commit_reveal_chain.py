from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from collections.abc import Mapping
from datetime import datetime, timezone

import bittensor as bt

from consequent.network import NetworkSettings
from validator.chain_state import read_consensus_policy, read_weight_policy, remaining_weight_rate_limit_blocks
from validator.discovery import discover_miners
from validator.weights import submit_weights


def _row(matrix: Mapping, uid: int) -> dict[int, float]:
    raw = matrix.get(int(uid), {}) or {}
    if not isinstance(raw, Mapping):
        return {}
    return {int(key): float(value) for key, value in raw.items()}


def _plan_payload(plan) -> dict:
    try:
        payload = plan.to_dict()
    except AttributeError:
        payload = {"repr": repr(plan), "ok": bool(getattr(plan, "ok", False))}
    extras = getattr(plan, "extras", None)
    if extras:
        payload["extras"] = dict(extras)
    return payload


async def _wait_for_rate_limit(
    *, client, netuid: int, validator_hotkey: str, rate_limit: int, poll_seconds: float, max_wait_blocks: int
) -> tuple[int, int]:
    starting_remaining: int | None = None
    while True:
        mg = await client.subnets.metagraph(netuid=netuid)
        validator = mg.by_hotkey(validator_hotkey)
        if validator is None:
            raise SystemExit("validator disappeared while waiting for the weight window")
        remaining = remaining_weight_rate_limit_blocks(
            current_block=int(mg.block),
            last_update=int(validator.last_update),
            rate_limit=rate_limit,
        )
        if starting_remaining is None:
            starting_remaining = remaining
            if remaining > max_wait_blocks:
                raise SystemExit(
                    f"weight window requires {remaining} blocks, above max-wait-blocks={max_wait_blocks}"
                )
        print(
            json.dumps(
                {
                    "event": "M2_CR_RATE_LIMIT_WAIT",
                    "current_block": int(mg.block),
                    "remaining_blocks": remaining,
                    "rate_limit": rate_limit,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
            flush=True,
        )
        if remaining == 0:
            return int(mg.block), int(starting_remaining)
        await asyncio.sleep(poll_seconds)


async def _wait_for_row_application(
    *, client, netuid: int, validator_uid: int, target_uid: int, start_block: int,
    poll_seconds: float, max_wait_blocks: int, reveal_round: int | None,
) -> tuple[int, dict[int, float]]:
    deadline = int(start_block) + int(max_wait_blocks)
    while True:
        matrix = await client.weights.weights(netuid=netuid)
        row = _row(matrix, validator_uid)
        mg = await client.subnets.metagraph(netuid=netuid)
        current_block = int(mg.block)
        if float(row.get(int(target_uid), 0.0)) > 0.0:
            return current_block, row
        if current_block >= deadline:
            raise SystemExit(
                "commit-reveal weight row was not applied within the bounded wait "
                f"(start={start_block}, deadline={deadline}, reveal_round={reveal_round})"
            )
        print(
            json.dumps(
                {
                    "event": "M2_CR_WAIT_FOR_APPLICATION",
                    "current_block": current_block,
                    "deadline_block": deadline,
                    "reveal_round": reveal_round,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
            flush=True,
        )
        await asyncio.sleep(poll_seconds)


async def _wait_for_epoch(
    *, client, netuid: int, start_block: int, tempo: int, poll_seconds: float, max_wait_blocks: int
) -> int:
    target = int(start_block) + max(1, int(tempo)) + 5
    deadline = int(start_block) + int(max_wait_blocks)
    while True:
        mg = await client.subnets.metagraph(netuid=netuid)
        current = int(mg.block)
        if current >= target:
            return current
        if current >= deadline:
            raise SystemExit(
                f"post-application epoch was not reached within the bounded wait "
                f"(start={start_block}, target={target}, deadline={deadline})"
            )
        print(
            json.dumps(
                {
                    "event": "M2_CR_WAIT_FOR_EPOCH",
                    "current_block": current,
                    "target_block": target,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
            flush=True,
        )
        await asyncio.sleep(poll_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prove Bittensor commit-reveal weight application without disabling the live setting."
    )
    parser.add_argument("--poll-seconds", type=float, default=12.5)
    parser.add_argument("--max-wait-blocks", type=int, default=120)
    parser.add_argument("--max-application-wait-blocks", type=int, default=520)
    parser.add_argument("--max-epoch-wait-blocks", type=int, default=430)
    parser.add_argument(
        "--skip-epoch-wait",
        action="store_true",
        help="capture application read-back without waiting for the next tempo (diagnostic only)",
    )
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
        if validator is None:
            raise SystemExit("commit-reveal validator is not registered on the target subnet")
        miners = await discover_miners(
            client=client,
            netuid=settings.netuid,
            exclude_hotkeys=(wallet.hotkey.ss58_address,),
        )
        if not miners:
            raise SystemExit("commit-reveal proof requires at least one served miner")

        policy = await read_weight_policy(client=client, netuid=settings.netuid)
        consensus = await read_consensus_policy(client=client, netuid=settings.netuid)
        if not policy.commit_reveal_weights_enabled:
            raise SystemExit("commit-reveal is disabled; this proof must not mutate the setting")
        if policy.commit_reveal_period <= 0:
            raise SystemExit("commit-reveal period must be positive")

        target_hotkey = os.getenv("CONSEQUENT_TARGET_HOTKEY")
        target = next((miner for miner in miners if miner.hotkey == target_hotkey), None) if target_hotkey else miners[0]
        if target is None:
            raise SystemExit("CONSEQUENT_TARGET_HOTKEY is not a served miner on the current metagraph")

        # Equal positive weights keep this proof about the publication path, not
        # about a hand-authored score vector. The live SDK still conforms this
        # mapping to minimum-count, clipping, and u16 quantization rules.
        weights = {int(miner.uid): 1.0 for miner in miners}
        validator_uid = int(validator.uid)
        before_matrix = await client.weights.weights(netuid=settings.netuid)
        before_row = _row(before_matrix, validator_uid)
        legal_block, initial_remaining = await _wait_for_rate_limit(
            client=client,
            netuid=settings.netuid,
            validator_hotkey=wallet.hotkey.ss58_address,
            rate_limit=policy.weights_rate_limit,
            poll_seconds=args.poll_seconds,
            max_wait_blocks=args.max_wait_blocks,
        )

        intent = bt.SetWeights(
            netuid=settings.netuid,
            weights=weights,
            version_key=policy.weights_version,
        )
        preview = await client.plan(intent, wallet)
        if not preview.ok:
            raise bt.PolicyError(preview.violations)
        preview_payload = _plan_payload(preview)
        effect_text = " ".join(str(effect) for effect in getattr(preview, "effects", ())).lower()
        if "commit" not in effect_text or "reveal" not in effect_text:
            raise SystemExit(
                "SetWeights plan did not expose the expected commit-reveal path: "
                + json.dumps(preview_payload, sort_keys=True, default=str)
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
                f"commit-reveal SetWeights failed: {result.error.code} {result.error.name}: {result.error.remediation}"
            )
        result_data = dict(getattr(result, "data", {}) or {})
        reveal_round = result_data.get("reveal_round")
        if reveal_round is None:
            raise SystemExit("successful SetWeights result did not expose the timelock reveal round")
        reveal_round = int(reveal_round)

        immediate_matrix = await client.weights.weights(netuid=settings.netuid)
        immediate_row = _row(immediate_matrix, validator_uid)
        if float(immediate_row.get(int(target.uid), 0.0)) > 0.0:
            raise SystemExit("target weight was visible immediately; commit-reveal delay was not exercised")

        submission_mg = await client.subnets.metagraph(netuid=settings.netuid)
        applied_block, applied_row = await _wait_for_row_application(
            client=client,
            netuid=settings.netuid,
            validator_uid=validator_uid,
            target_uid=int(target.uid),
            start_block=int(submission_mg.block),
            poll_seconds=args.poll_seconds,
            max_wait_blocks=args.max_application_wait_blocks,
            reveal_round=reveal_round,
        )

        outcome_block = applied_block
        if not args.skip_epoch_wait:
            outcome_block = await _wait_for_epoch(
                client=client,
                netuid=settings.netuid,
                start_block=applied_block,
                tempo=consensus.tempo,
                poll_seconds=args.poll_seconds,
                max_wait_blocks=args.max_epoch_wait_blocks,
            )
        final_mg = await client.subnets.metagraph(netuid=settings.netuid)
        target_neuron = final_mg.by_hotkey(target.hotkey)
        if target_neuron is None:
            raise SystemExit("target miner disappeared before commit-reveal outcome capture")

        expected_positive = {int(uid) for uid, value in weights.items() if float(value) > 0.0}
        if not expected_positive.issubset({int(uid) for uid, value in applied_row.items() if float(value) > 0.0}):
            raise SystemExit("applied chain row omitted one or more positive submitted weights")

        print(
            json.dumps(
                {
                    "state": (
                        "M2_COMMIT_REVEAL_CHAIN_PASS"
                        if not args.skip_epoch_wait
                        else "M2_COMMIT_REVEAL_APPLICATION_ONLY"
                    ),
                    "network": settings.network,
                    "netuid": settings.netuid,
                    "validator_uid": validator_uid,
                    "validator_hotkey": wallet.hotkey.ss58_address,
                    "validator_is_owner_uid": validator_uid == 0,
                    "validator_permit": bool(validator.validator_permit),
                    "target_uid": int(target.uid),
                    "target_hotkey": target.hotkey,
                    "served_miner_count": len(miners),
                    "computed_weights": {str(uid): float(value) for uid, value in sorted(weights.items())},
                    "before_row": {str(uid): float(value) for uid, value in sorted(before_row.items())},
                    "immediate_row": {str(uid): float(value) for uid, value in sorted(immediate_row.items())},
                    "applied_row": {str(uid): float(value) for uid, value in sorted(applied_row.items())},
                    "policy": policy.__dict__,
                    "consensus_policy": consensus.__dict__,
                    "preview": preview_payload,
                    "result": result.to_dict() if hasattr(result, "to_dict") else str(result),
                    "reveal_round": reveal_round,
                    "legal_submission_block": legal_block,
                    "initial_remaining_rate_limit_blocks": initial_remaining,
                    "application_block": applied_block,
                    "outcome_block": outcome_block,
                    "outcome_wait_skipped": bool(args.skip_epoch_wait),
                    "target_incentive": float(target_neuron.incentive),
                    "target_emission_rao": int(target_neuron.emission.rao),
                    "target_emission_amount": float(target_neuron.emission.amount),
                    "captured_at": datetime.now(timezone.utc).isoformat(),
                },
                indent=2,
                sort_keys=True,
                default=str,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())

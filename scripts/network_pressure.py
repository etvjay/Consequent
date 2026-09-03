from __future__ import annotations

import asyncio
import json

from consequent.m0_fixture import m0_challenge, m0_hidden_tasks
from consequent.network import NetworkSettings
from validator.discovery import discover_miners
from validator.runner import evaluate_round

EXPECTED = {
    "no_memory",
    "irrelevant_memory",
    "overfit_memory",
    "useful_generalizing_memory",
    "harmful_memory",
    "policy_violating_memory",
}


async def main() -> None:
    import bittensor as bt

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

    if len(miners) < 6:
        raise SystemExit(f"expected at least 6 discoverable miners, found {len(miners)}")

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
            "uid": uid,
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
        raise SystemExit(f"missing expected miner strategies: {sorted(missing)}")

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
    }
    if not all(checks.values()):
        raise SystemExit("M0 network pressure ordering failed: " + json.dumps(checks, sort_keys=True))

    payload = {
        "state": "M0_SIX_MINER_NETWORK_PRESSURE_PASS",
        "netuid": settings.netuid,
        "miner_count": len(miners),
        "checks": checks,
        "strategies": by_strategy,
        "weight_sum": sum(weights.values()),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())

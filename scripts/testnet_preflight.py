from __future__ import annotations

import argparse
import asyncio
import json

import bittensor as bt

from consequent.network import NetworkSettings, served_neurons
from miner.serve import plan_serve_axon
from validator.chain_state import read_weight_policy


def _neuron_payload(neuron):
    if neuron is None:
        return None
    return {
        "uid": int(neuron.uid),
        "hotkey": str(neuron.hotkey),
        "validator_permit": bool(getattr(neuron, "validator_permit", False)),
        "axon": str(neuron.axon) if getattr(neuron, "axon", None) else None,
        "tao_stake": str(getattr(neuron, "tao_stake", "0")),
    }


async def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only Consequent Bittensor network preflight")
    parser.add_argument("--plan-serve", action="store_true", help="also create a non-mutating ServeAxon plan")
    args = parser.parse_args()

    settings = NetworkSettings.from_env()
    if not settings.network_mode:
        raise SystemExit("set CONSEQUENT_NETWORK_MODE=1 for chain preflight")
    assert settings.netuid is not None

    wallet = settings.wallet()
    hotkey_ss58 = wallet.hotkey.ss58_address

    async with bt.Subtensor(network=settings.network) as client:
        mg = await client.subnets.metagraph(netuid=settings.netuid)
        try:
            neuron = mg.by_hotkey(hotkey_ss58)
        except Exception:
            neuron = None

        policy = await read_weight_policy(client=client, netuid=settings.netuid)
        payload = {
            "network": settings.network,
            "netuid": settings.netuid,
            "wallet": settings.wallet_name,
            "hotkey_name": settings.hotkey_name,
            "hotkey_ss58": hotkey_ss58,
            "registered": neuron is not None,
            "neuron": _neuron_payload(neuron),
            "served_neuron_count": len(served_neurons(mg)),
            "weight_policy": {
                "min_allowed_weights": policy.min_allowed_weights,
                "max_weights_limit": policy.max_weights_limit,
                "weights_version": policy.weights_version,
                "weights_rate_limit": policy.weights_rate_limit,
                "commit_reveal_weights_enabled": policy.commit_reveal_weights_enabled,
                "commit_reveal_period": policy.commit_reveal_period,
            },
        }
        print(json.dumps(payload, indent=2, sort_keys=True))

        if args.plan_serve:
            if neuron is None:
                raise SystemExit("cannot plan ServeAxon: hotkey is not registered on this subnet")
            if not settings.advertised_ip:
                raise SystemExit("set CONSEQUENT_ADVERTISED_IP before --plan-serve")
            planned = await plan_serve_axon(
                client=client,
                wallet=wallet,
                netuid=settings.netuid,
                ip=settings.advertised_ip,
                port=settings.advertised_port,
            )
            print("\n--- ServeAxon plan (non-mutating) ---")
            print(planned.plan)


if __name__ == "__main__":
    asyncio.run(main())

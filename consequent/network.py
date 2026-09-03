from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Iterable


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class NetworkSettings:
    """Runtime settings for Consequent's Bittensor-facing surfaces.

    Network mode is deliberately explicit. When enabled, wallet + hotkey + netuid
    are mandatory and miner authentication must fail closed.
    """

    network: str = "test"
    netuid: int | None = None
    wallet_name: str | None = None
    hotkey_name: str | None = None
    wallet_path: str | None = None
    network_mode: bool = False
    advertised_ip: str | None = None
    advertised_port: int = 8091
    require_validator_permit: bool = True
    min_validator_tao_stake: float = 0.0

    @classmethod
    def from_env(cls) -> "NetworkSettings":
        raw_netuid = os.getenv("CONSEQUENT_NETUID")
        settings = cls(
            network=os.getenv("CONSEQUENT_BT_NETWORK", "test"),
            netuid=int(raw_netuid) if raw_netuid is not None else None,
            wallet_name=os.getenv("CONSEQUENT_WALLET"),
            hotkey_name=os.getenv("CONSEQUENT_HOTKEY"),
            wallet_path=os.getenv("CONSEQUENT_WALLET_PATH"),
            network_mode=_env_bool("CONSEQUENT_NETWORK_MODE", False),
            advertised_ip=os.getenv("CONSEQUENT_ADVERTISED_IP"),
            advertised_port=int(os.getenv("CONSEQUENT_ADVERTISED_PORT", "8091")),
            require_validator_permit=_env_bool("CONSEQUENT_REQUIRE_VALIDATOR_PERMIT", True),
            min_validator_tao_stake=float(os.getenv("CONSEQUENT_MIN_VALIDATOR_TAO_STAKE", "0")),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        if self.advertised_port < 1 or self.advertised_port > 65535:
            raise ValueError("CONSEQUENT_ADVERTISED_PORT must be between 1 and 65535")
        if self.min_validator_tao_stake < 0:
            raise ValueError("CONSEQUENT_MIN_VALIDATOR_TAO_STAKE cannot be negative")
        if self.network_mode:
            missing: list[str] = []
            if self.netuid is None:
                missing.append("CONSEQUENT_NETUID")
            if not self.wallet_name:
                missing.append("CONSEQUENT_WALLET")
            if not self.hotkey_name:
                missing.append("CONSEQUENT_HOTKEY")
            if missing:
                raise RuntimeError("network mode requires: " + ", ".join(missing))

    def wallet(self):
        if not self.wallet_name or not self.hotkey_name:
            raise RuntimeError("wallet and hotkey names are required")
        import bittensor as bt

        kwargs = {"name": self.wallet_name, "hotkey": self.hotkey_name}
        if self.wallet_path:
            kwargs["path"] = self.wallet_path
        return bt.Wallet(**kwargs)


@dataclass(frozen=True)
class NeuronEndpoint:
    uid: int
    hotkey: str
    endpoint: str
    validator_permit: bool = False


def neuron_by_hotkey(metagraph: Any, hotkey_ss58: str):
    return metagraph.by_hotkey(hotkey_ss58)


def served_neurons(
    metagraph: Any,
    *,
    exclude_hotkeys: Iterable[str] = (),
) -> list[NeuronEndpoint]:
    excluded = set(exclude_hotkeys)
    result: list[NeuronEndpoint] = []
    for neuron in metagraph:
        if neuron.hotkey in excluded or not neuron.axon:
            continue
        result.append(
            NeuronEndpoint(
                uid=int(neuron.uid),
                hotkey=str(neuron.hotkey),
                endpoint=str(neuron.axon),
                validator_permit=bool(getattr(neuron, "validator_permit", False)),
            )
        )
    return result


async def metagraph(client, netuid: int):
    return await client.subnets.metagraph(netuid=netuid)


async def neuron_state(client, *, netuid: int, hotkey_ss58: str):
    mg = await metagraph(client, netuid)
    return neuron_by_hotkey(mg, hotkey_ss58)

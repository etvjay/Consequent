from __future__ import annotations

from dataclasses import dataclass

import pytest

from consequent.network import NetworkSettings, neuron_by_hotkey, served_neurons
from miner.policy import authorize_caller


@dataclass
class FakeNeuron:
    uid: int
    hotkey: str
    axon: str | None
    validator_permit: bool = False
    tao_stake: float = 0.0

    @property
    def stake(self):
        return self.tao_stake


class FakeMetagraph(list):
    def by_hotkey(self, hotkey: str):
        for neuron in self:
            if neuron.hotkey == hotkey:
                return neuron
        raise KeyError(hotkey)


def test_network_mode_requires_wallet_hotkey_and_netuid(monkeypatch):
    monkeypatch.setenv("CONSEQUENT_NETWORK_MODE", "1")
    monkeypatch.delenv("CONSEQUENT_NETUID", raising=False)
    monkeypatch.delenv("CONSEQUENT_WALLET", raising=False)
    monkeypatch.delenv("CONSEQUENT_HOTKEY", raising=False)

    with pytest.raises(RuntimeError):
        NetworkSettings.from_env()


def test_served_neurons_only_returns_chain_published_endpoints():
    mg = FakeMetagraph(
        [
            FakeNeuron(0, "hk0", None),
            FakeNeuron(1, "hk1", "127.0.0.1:8091"),
            FakeNeuron(2, "hk2", "127.0.0.1:8092"),
        ]
    )
    endpoints = served_neurons(mg, exclude_hotkeys=("hk2",))
    assert [(n.uid, n.hotkey, n.endpoint) for n in endpoints] == [(1, "hk1", "127.0.0.1:8091")]


def test_caller_policy_requires_registered_validator_permit():
    settings = NetworkSettings(require_validator_permit=True)
    mg = FakeMetagraph(
        [
            FakeNeuron(1, "miner", "127.0.0.1:8091", validator_permit=False),
            FakeNeuron(2, "validator", "127.0.0.1:8092", validator_permit=True),
        ]
    )

    denied_unknown = authorize_caller(caller_hotkey="unknown", metagraph=mg, settings=settings)
    denied_miner = authorize_caller(caller_hotkey="miner", metagraph=mg, settings=settings)
    allowed = authorize_caller(caller_hotkey="validator", metagraph=mg, settings=settings)

    assert not denied_unknown.allowed
    assert not denied_miner.allowed
    assert allowed.allowed and allowed.uid == 2


def test_neuron_by_hotkey_uses_v11_metagraph_record_access():
    mg = FakeMetagraph([FakeNeuron(7, "validator", "127.0.0.1:8092", validator_permit=True)])
    assert neuron_by_hotkey(mg, "validator").uid == 7

from __future__ import annotations

from dataclasses import dataclass

from fastapi.testclient import TestClient

from consequent.models import MemoryFormationRequest


@dataclass
class FakeNeuron:
    uid: int
    hotkey: str
    axon: str | None
    validator_permit: bool


class FakeMetagraph(list):
    def by_hotkey(self, hotkey: str):
        for neuron in self:
            if neuron.hotkey == hotkey:
                return neuron
        raise KeyError(hotkey)


def _new_wallet(bt, *, path: str, name: str, hotkey: str):
    wallet = bt.Wallet(name=name, hotkey=hotkey, path=path)
    wallet.create_new_coldkey(use_password=False, overwrite=True)
    wallet.create_new_hotkey(use_password=False, overwrite=True)
    return wallet


def test_real_btauth_signed_http_round_trip(monkeypatch, tmp_path):
    import bittensor as bt
    import miner.app as miner_app

    validator_wallet = _new_wallet(bt, path=str(tmp_path), name="validator", hotkey="validator")
    miner_wallet = _new_wallet(bt, path=str(tmp_path), name="miner", hotkey="miner")

    fake_metagraph = FakeMetagraph(
        [
            FakeNeuron(
                uid=1,
                hotkey=miner_wallet.hotkey.ss58_address,
                axon="127.0.0.1:8091",
                validator_permit=False,
            ),
            FakeNeuron(
                uid=2,
                hotkey=validator_wallet.hotkey.ss58_address,
                axon="127.0.0.1:8092",
                validator_permit=True,
            ),
        ]
    )

    async def fake_load_metagraph(_settings):
        return fake_metagraph

    monkeypatch.setattr(miner_app, "_load_metagraph", fake_load_metagraph)
    monkeypatch.setenv("CONSEQUENT_NETWORK_MODE", "1")
    monkeypatch.setenv("CONSEQUENT_NETUID", "42")
    monkeypatch.setenv("CONSEQUENT_WALLET", "miner")
    monkeypatch.setenv("CONSEQUENT_HOTKEY", "miner")
    monkeypatch.setenv("CONSEQUENT_WALLET_PATH", str(tmp_path))
    monkeypatch.setenv("CONSEQUENT_REQUIRE_VALIDATOR_PERMIT", "1")

    challenge = MemoryFormationRequest(challenge_id="signed-http-roundtrip", episodes=[])
    body = challenge.model_dump_json().encode()
    path = "/v1/memory/formation"
    headers = bt.http_auth.sign(
        validator_wallet,
        method="POST",
        path=path,
        body=body,
        receiver_ss58=miner_wallet.hotkey.ss58_address,
    )
    headers["content-type"] = "application/json"

    client = TestClient(miner_app.app)
    response = client.post(path, content=body, headers=headers)

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["challenge_id"] == "signed-http-roundtrip"


def test_network_mode_rejects_unsigned_request(monkeypatch, tmp_path):
    import bittensor as bt
    import miner.app as miner_app

    miner_wallet = _new_wallet(bt, path=str(tmp_path), name="miner2", hotkey="miner2")

    monkeypatch.setenv("CONSEQUENT_NETWORK_MODE", "1")
    monkeypatch.setenv("CONSEQUENT_NETUID", "42")
    monkeypatch.setenv("CONSEQUENT_WALLET", "miner2")
    monkeypatch.setenv("CONSEQUENT_HOTKEY", "miner2")
    monkeypatch.setenv("CONSEQUENT_WALLET_PATH", str(tmp_path))

    challenge = MemoryFormationRequest(challenge_id="unsigned", episodes=[])
    client = TestClient(miner_app.app)
    response = client.post(
        "/v1/memory/formation",
        content=challenge.model_dump_json().encode(),
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 401

from __future__ import annotations

import pytest


def test_btauth_real_keypair_roundtrip_and_replay_rejection():
    import bittensor as bt
    from bittensor.keyfiles import Keypair

    sender = Keypair.create_from_uri("//Alice")
    receiver = Keypair.create_from_uri("//Bob")
    body = b'{"prompt":"consequent"}'
    path = "/v1/memory/formation"

    # Bittensor 11.1 accepts a raw Keypair as a Signer. Keep this test on the
    # SDK's real signer seam rather than wrapping the key in a fake wallet.
    headers = bt.http_auth.sign(
        sender,
        method="POST",
        path=path,
        body=body,
        receiver_ss58=receiver.ss58_address,
    )
    caller = bt.http_auth.verify(
        headers,
        body,
        method="POST",
        path=path,
        self_hotkey_ss58=receiver.ss58_address,
    )
    assert caller.hotkey_ss58 == sender.ss58_address

    with pytest.raises(bt.http_auth.ReplayedRequest):
        bt.http_auth.verify(
            headers,
            body,
            method="POST",
            path=path,
            self_hotkey_ss58=receiver.ss58_address,
        )


def test_btauth_rejects_body_tampering():
    import bittensor as bt
    from bittensor.keyfiles import Keypair

    sender = Keypair.create_from_uri("//Alice")
    receiver = Keypair.create_from_uri("//Bob")
    path = "/v1/memory/formation"
    headers = bt.http_auth.sign(
        sender,
        method="POST",
        path=path,
        body=b"original",
        receiver_ss58=receiver.ss58_address,
    )

    with pytest.raises(bt.http_auth.BadSignature):
        bt.http_auth.verify(
            headers,
            b"tampered",
            method="POST",
            path=path,
            self_hotkey_ss58=receiver.ss58_address,
        )

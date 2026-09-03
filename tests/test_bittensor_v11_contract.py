from __future__ import annotations


def test_current_bittensor_v11_contract_symbols_exist():
    import bittensor as bt

    assert hasattr(bt, "Subtensor")
    assert hasattr(bt, "ServeAxon")
    assert hasattr(bt, "SetWeights")
    assert hasattr(bt, "http_auth")
    assert callable(bt.http_auth.sign)
    assert callable(bt.http_auth.verify)


def test_v11_intents_can_be_constructed_without_chain_mutation():
    import bittensor as bt

    serve = bt.ServeAxon(netuid=1, ip="127.0.0.1", port=8091)
    weights = bt.SetWeights(netuid=1, weights={0: 0.25, 1: 0.75})

    assert serve.netuid == 1
    assert weights.netuid == 1

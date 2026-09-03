# Consequent local Bittensor development

This document follows the current Bittensor v11 local-development flow. Localnet evidence is not testnet evidence.

## 1. Start a local subtensor chain

```bash
docker run --rm --name consequent-local-chain \
  -p 9944:9944 -p 9945:9945 \
  ghcr.io/raofoundation/subtensor-localnet:devnet
```

The official localnet ships with root subnet 0 and subnet 1. Use a fresh local chain for reproducible lifecycle tests.

## 2. Create role wallets

```bash
btcli wallet create -w consequent-owner -H default --no-password
btcli wallet create -w consequent-validator -H default --no-password
btcli wallet create -w consequent-miner -H default --no-password
```

Local development may use the public Substrate Alice dev key to fund disposable role wallets. Never reuse dev keys outside localnet.

## 3. Create/activate a development subnet

Follow the current Bittensor v11 transaction flow:

```bash
btcli tx register-subnet -w consequent-owner --network local
# Record the returned netuid.
btcli tx start-call --netuid <NETUID> -w consequent-owner --network local
```

Register validator and miner hotkeys:

```bash
btcli tx burned-register --netuid <NETUID> -w consequent-validator --network local
btcli tx burned-register --netuid <NETUID> -w consequent-miner --network local
```

Then confirm chain state:

```bash
btcli query metagraph --netuid <NETUID> --network local --json
```

## 4. Start the Consequent miner HTTP service

Configure the role explicitly:

```bash
export CONSEQUENT_NETWORK_MODE=1
export CONSEQUENT_BT_NETWORK=local
export CONSEQUENT_NETUID=<NETUID>
export CONSEQUENT_WALLET=consequent-miner
export CONSEQUENT_HOTKEY=default
export CONSEQUENT_ADVERTISED_IP=127.0.0.1
export CONSEQUENT_ADVERTISED_PORT=8091

uvicorn miner.app:app --host 0.0.0.0 --port 8091
```

In network mode the miner authenticates btauth/1 requests and authorizes callers against current metagraph state.

## 5. Publish the endpoint

Consequent separates planning from execution. Preview first using Bittensor's transaction plan/dry-run semantics; do not publish an endpoint before the HTTP service is reachable.

The chain-side publication is `bt.ServeAxon(netuid=..., ip=..., port=...)`. It records endpoint metadata only; it does not start the HTTP server.

## 6. Validator discovery

The validator must fetch:

```python
mg = await client.subnets.metagraph(netuid=NETUID)
```

and select miners from per-neuron records whose `n.axon` is non-null. Manual endpoint lists are permitted only as test fixtures, not as canonical network discovery.

## 7. Evidence boundary

A localnet pass can establish:

- wallet/hotkey lifecycle;
- registration and UID resolution;
- ServeAxon publication;
- metagraph discovery;
- btauth/1 validator→miner traffic;
- multi-miner scoring;
- SetWeights transaction mechanics.

It cannot establish `TESTNET_PASS`. Testnet promotion requires the same loop on the current official Bittensor test network with recorded chain evidence.

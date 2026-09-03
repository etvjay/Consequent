# Consequent Protocol v0.1

Consequent uses Bittensor 11's plain-HTTP data plane with `btauth/1` request authentication.

## Endpoint

`POST /v1/memory/formation`

A validator sends execution episodes plus a bounded memory budget. A miner returns a Behavioral Memory Patch (BMP).

## Security invariant

Authentication is performed over the raw request bytes before JSON parsing. The validator binds each signed request to the receiving miner hotkey. The miner verifies method, wire path, body hash, nonce freshness, receiver and signature through `bittensor.http_auth.verify`.

## Commodity invariant

The response is not rewarded for storage, recall, compression or plausibility. Validator scoring is based on paired future execution utility, with regression penalties and a non-compensable policy-violation veto.

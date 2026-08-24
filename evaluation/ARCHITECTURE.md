# Consequent Architecture — Bittensor 11

```text
validator concealed challenge
  ↓ btauth/1 signed HTTP
POST /v1/memory/formation
  ↓
miner HTTP service
  ↓
Behavioral Memory Patch
  ↓
paired A0/A1 evaluator
  ↓
causal utility + regression + policy veto
  ↓
UID score vector
  ↓
chain conformance
  ↓
bt.SetWeights
```

Bittensor 11 does not provide Axon/Dendrite/Synapse. Consequent owns its HTTP server, client and JSON schemas; `bittensor.http_auth.sign/verify` provides hotkey-bound request authentication.

A successful HTTP response is not an outcome. Economic consequence exists only after the validator score is converted into an accepted Bittensor weight transaction.

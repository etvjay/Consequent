# EBI Status — Consequent

**Current:** `LOCAL_NETWORK_PASS`

Canonical build authority:
1. `/GROUND_TRUTH.md`
2. `/audits.md`

Mechanism oracle: LOCAL_PASS.
Category boundary: FROZEN_v0.1.
Bittensor 11 architecture: truth-corrected 2026-08-24.
Toolchain evidence: CI_PASS — `bittensor==11.1.0` installs and the Consequent package/test suite passes on Python 3.10 and 3.12.

M0.1 identity/chain-state primitives: IMPLEMENTED_CI_PASS — explicit network settings, wallet/hotkey/netuid configuration, metagraph reads, neuron lookup, live weight-policy reads.
M0.2 serve/discover primitives: IMPLEMENTED_CI_PASS — `bt.ServeAxon` plan/execute helpers and metagraph-driven miner discovery.
M0.3 authenticated local network: LOCAL_NETWORK_PASS — real Bittensor hotkeys/keypairs sign and verify btauth/1 requests; replay and body tampering are rejected; unsigned network requests fail closed; a signed POST passes through the FastAPI miner endpoint and metagraph validator policy.
M0.4 six-miner pressure network: LOCAL_NETWORK_PASS — CI spawns six independent Uvicorn miner processes, queries them over sockets through the validator HTTP client, scores concealed holdouts, hard-vetoes the policy-violating miner, and normalizes weights with the useful generalizer ranked highest.
Bittensor v11 contract tests: CI_PASS — `Subtensor`, `ServeAxon`, `SetWeights`, and `http_auth` symbols/intents verified against installed 11.1.0.
Expanded CI suite: 19/19 PASS on Python 3.10 and 3.12 (GitHub Actions run 32753997338).

Important evidence boundary:
- `ServeAxon` helper exists and is CI-compatible, but actual chain publication: NOT_RUN;
- metagraph discovery helper exists, but visibility of our own served neuron on chain: NOT_RUN;
- multi-miner process network is local and does not represent registered testnet neurons;
- live weight-policy read and SetWeights plan helpers exist, but an actual plan against our target subnet: NOT_RUN;
- SetWeights execution: NOT_RUN;
- testnet evidence: NOT_RUN;
- submission evidence: NOT_RUN.

Next canonical gate: M0.5 + testnet readiness — document/register wallets and hotkeys, choose/record the testnet netuid/subnet path, plan ServeAxon and SetWeights against live testnet state, then execute only after explicit operator funding/registration prerequisites are satisfied.

No local or CI result may be presented as testnet evidence.

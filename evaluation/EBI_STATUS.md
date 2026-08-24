# EBI Status — Consequent

**Current:** `CHAIN_LOCAL_REGISTRATION_PASS / LOCAL_NETWORK_COMPONENT_PASS`

Canonical build authority:
1. `/GROUND_TRUTH.md`
2. `/audits.md`

Mechanism oracle: LOCAL_PASS.
Category boundary: FROZEN_v0.1.
Bittensor 11 architecture: truth-corrected 2026-08-24.
Toolchain evidence: CI_PASS — `bittensor==11.1.0` installs and the Consequent package/test suite passes on Python 3.10 and 3.12.

M0.1 identity/chain-state primitives: IMPLEMENTED_CI_PASS — explicit network settings, wallet/hotkey/netuid configuration, metagraph reads, neuron lookup, live weight-policy reads.
M0.2 serve/discover primitives: IMPLEMENTED_CI_PASS — `bt.ServeAxon` plan/execute helpers and metagraph-driven miner discovery.
M0.3 authenticated HTTP component: LOCAL_NETWORK_COMPONENT_PASS — real Bittensor hotkeys/keypairs sign and verify btauth/1 requests; replay and body tampering are rejected; unsigned network requests fail closed; a signed POST passes through the FastAPI miner endpoint and metagraph validator policy in the component harness.
M0.4 six-miner HTTP pressure component: LOCAL_NETWORK_COMPONENT_PASS — CI spawns six independent Uvicorn miner processes, queries them over sockets through the validator HTTP client, scores concealed holdouts, hard-vetoes the policy-violating miner, and normalizes weights with the useful generalizer ranked highest. These processes are not chain-registered in this component test.
Bittensor v11 contract tests: CI_PASS — `Subtensor`, `ServeAxon`, `SetWeights`, and `http_auth` symbols/intents verified against installed 11.1.0.

External network read evidence: `READ_ONLY_TESTNET_PASS` — CI connects to Bittensor network `test` and reads live chain state. This proves connectivity/read compatibility only; it is not testnet subnet evidence.

Strict fresh-chain evidence:
- GitHub Actions localnet run 32754995956 used the official Subtensor localnet container with production-like block timing and fail-closed shell semantics.
- subnet registration: PASS — netuid 2 registered at block 10;
- subnet activation: PASS — activation extrinsic succeeded;
- validator burned/collateral registration: PASS — MEV-shielded, UID 1;
- miner burned/collateral registration: PASS — MEV-shielded, UID 2;
- post-registration metagraph assertion: PASS — both hotkeys present and `num_uids=3` including owner;
- authenticated miner HTTP process startup: PASS;
- ServeAxon in that run: FAILED because loopback `127.0.0.1` is invalid chain-advertised IP;
- downstream chain-local discovery/round-trip: NOT_RUN in that failed run.

The current strict workflow now resolves and advertises a non-loopback runner interface while Uvicorn remains bound to `0.0.0.0`. A new run is testing that correction.

Important evidence boundary:
- actual successful chain-local Consequent neuron registration: `CHAIN_LOCAL_REGISTRATION_PASS`;
- actual successful chain-local ServeAxon publication: NOT_YET_PROVEN;
- actual successful chain-local metagraph endpoint discovery/round trip: NOT_YET_PROVEN;
- multi-miner process network is local HTTP/process evidence and does not represent registered testnet neurons;
- live weight-policy helpers and SetWeights plan/submit code exist; strict chain-local execute/read-back probe is being added but has not passed yet;
- testnet neuron/ServeAxon/weight evidence: NOT_RUN;
- submission evidence: NOT_RUN.

Next canonical gate: strict fresh-chain serving lifecycle PASS — ServeAxon → metagraph endpoint discovery → signed round trip. Then execute/read back SetWeights on the same fresh local chain before crossing to funded Bittensor `test` state.

No local, chain-local, CI, or read-only testnet result may be presented as deployed testnet evidence.

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
Expanded established CI suite: 19/19 PASS on Python 3.10 and 3.12 (GitHub Actions run 32753997338).

External network read evidence: `READ_ONLY_TESTNET_PASS` — GitHub Actions run 32754327208 connected to Bittensor network `test` with `bittensor==11.1.0` and read block 7,854,063. This proves connectivity/read compatibility only; it is not testnet subnet evidence.

Chain-local harness correction:
- A prior fresh-Subtensor workflow run was initially displayed green because failing commands were piped through `tee` without `pipefail`.
- Log inspection proved validator neuron registration failed, so ServeAxon/discovery/round-trip also failed downstream.
- That run is classified `FAILED_EVIDENCE_HARNESS`; it MUST NOT be cited as chain-local pass evidence.
- The localnet workflow is now fail-closed with `set -euo pipefail`, explicit post-registration metagraph assertions, and required registered-validator + served-miner probe gates.
- Current strict rerun uses production-like block timing and the CLI's required default MEV-shielded burned-registration path.

Important evidence boundary:
- actual successful chain-local Consequent neuron registration: NOT_YET_PROVEN by the strict harness;
- actual successful chain-local ServeAxon publication: NOT_YET_PROVEN by the strict harness;
- actual successful chain-local metagraph discovery/round trip: NOT_YET_PROVEN by the strict harness;
- multi-miner process network is local HTTP/process evidence and does not represent registered testnet neurons;
- live weight-policy read and SetWeights plan helpers exist, but an actual plan against our target subnet: NOT_RUN;
- SetWeights execution: NOT_RUN;
- testnet neuron/ServeAxon/weight evidence: NOT_RUN;
- submission evidence: NOT_RUN.

Next canonical gate: strict fresh-chain lifecycle PASS — register subnet → activate → register validator/miner → ServeAxon → metagraph discovery → signed round trip. Then add SetWeights plan/execute/read-back on that chain before crossing to funded Bittensor `test` state.

No local, chain-local, CI, or read-only testnet result may be presented as deployed testnet evidence.

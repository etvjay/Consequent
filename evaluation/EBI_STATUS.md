# EBI Status — Consequent

**Current:** `CHAIN_LOCAL_SERVING_PASS / LOCAL_NETWORK_COMPONENT_PASS`

Canonical build authority:
1. `/GROUND_TRUTH.md`
2. `/audits.md`

Mechanism oracle: LOCAL_PASS.
Category boundary: FROZEN_v0.1.
Bittensor 11 architecture: truth-corrected 2026-08-24.
Toolchain evidence: CI_PASS — `bittensor==11.1.0` installs and the Consequent package/test suite passes on Python 3.10 and 3.12.

M0.1 identity/chain-state primitives: IMPLEMENTED_CI_PASS — explicit network settings, wallet/hotkey/netuid configuration, metagraph reads, neuron lookup, live weight-policy reads.
M0.2 serve/discover primitives: CHAIN_LOCAL_PASS — `bt.ServeAxon` publication succeeded on a fresh official Subtensor localnet and the validator discovered the miner from the metagraph-published endpoint.
M0.3 authenticated chain-local network: CHAIN_LOCAL_PASS — a registered validator hotkey signed a btauth/1 request to the chain-discovered miner endpoint; the registered miner verified it and returned a valid BMP response (`LOCAL_NETWORK_AUTH_ROUNDTRIP_PASS`).
M0.4 six-miner HTTP pressure component: LOCAL_NETWORK_COMPONENT_PASS — CI spawns six independent Uvicorn miner processes, queries them over sockets through the validator HTTP client, scores concealed holdouts, hard-vetoes the policy-violating miner, and normalizes weights with the useful generalizer ranked highest. These processes are not yet six chain-registered neurons in one strict fresh-chain run.
Bittensor v11 contract tests: CI_PASS — `Subtensor`, `ServeAxon`, `SetWeights`, and `http_auth` symbols/intents verified against installed 11.1.0.

External network read evidence: `READ_ONLY_TESTNET_PASS` — CI connects to Bittensor network `test` and reads live chain state. This proves connectivity/read compatibility only; it is not testnet subnet evidence.

Strict fresh-chain evidence from GitHub Actions localnet run 32755633843:
- official Subtensor localnet container with production-like block timing and fail-closed shell semantics;
- subnet registration: PASS — netuid 2;
- subnet activation: PASS;
- validator burned/collateral registration: PASS — MEV-shielded, UID 1;
- miner burned/collateral registration: PASS — MEV-shielded, UID 2;
- post-registration metagraph assertion: PASS;
- authenticated miner HTTP process startup: PASS;
- non-loopback advertised runner endpoint: PASS — `10.1.0.171:8091` in that ephemeral run;
- `ServeAxon`: PASS — `AxonServed` event, extrinsic `18-0006`;
- metagraph discovery: PASS — miner UID 2 discovered at the chain-published endpoint;
- signed validator → miner BMP round trip: PASS — challenge `localnet-auth-roundtrip-001`, BMP schema `bmp/0.1`, one rule returned;
- SetWeights execute/read-back: FAILED before submission because the SDK's `subnet_hyperparameters()` returned a mapping while Consequent expected attribute-style fields.

SetWeights defect correction:
- `validator.chain_state.read_weight_policy()` now accepts both mapping and object/model SDK result forms and fails loudly when a required field is missing;
- a mapping-shape regression test was added using the exact localnet hyperparameter form that exposed the defect;
- this correction is committed, but the strict localnet SetWeights execute/read-back rerun has not yet produced pass evidence.

Important evidence boundary:
- chain-local subnet + neuron lifecycle: `CHAIN_LOCAL_PASS`;
- chain-local ServeAxon + metagraph discovery: `CHAIN_LOCAL_PASS`;
- chain-local signed BMP round trip: `CHAIN_LOCAL_PASS`;
- six-miner network: only `LOCAL_NETWORK_COMPONENT_PASS` until six independent chain-registered miners are exercised together;
- chain-local SetWeights execution/read-back: `PATCHED_AWAITING_RERUN`;
- testnet neuron/ServeAxon/weight evidence: NOT_RUN;
- submission evidence: NOT_RUN.

Next canonical gate: rerun the strict fresh-chain lifecycle through `SetWeights` execution and chain read-back. If that passes, M0 is closed. Then promote to a six-chain-registered-miner competitive local subnet before any funded Bittensor `test` mutation.

No local, chain-local, CI, or read-only testnet result may be presented as deployed testnet evidence.

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

Strict fresh-chain evidence:
- official Subtensor localnet container with production-like block timing and fail-closed shell semantics;
- subnet registration: PASS — netuid 2;
- subnet activation: PASS;
- validator burned/collateral registration: PASS — MEV-shielded, UID 1;
- miner burned/collateral registration: PASS — MEV-shielded, UID 2;
- post-registration metagraph assertion: PASS;
- authenticated miner HTTP process startup: PASS;
- non-loopback advertised runner endpoint: PASS;
- `ServeAxon`: PASS — `AxonServed` observed;
- metagraph discovery: PASS — miner discovered from chain-published endpoint;
- signed validator → miner BMP round trip: PASS — challenge `localnet-auth-roundtrip-001`, BMP schema `bmp/0.1`;
- SetWeights execute/read-back: NOT YET PASS.

SetWeights findings and corrections:
1. `subnet_hyperparameters()` returns a mapping on the local v11 path. `read_weight_policy()` now supports both mapping and object/model forms, with a regression test.
2. New subnets default to commit-reveal. For deterministic M0 read-back only, the disposable subnet owner disables `commit_reveal_weights_enabled`; commit-reveal compatibility remains a later production/testnet gate.
3. `weights_rate_limit` is runtime-owned and is not owner-settable in Bittensor 11. An attempted owner mutation was correctly rejected before chain submission.
4. Consequent now models the live rate-limit rule explicitly with `remaining_weight_rate_limit_blocks()` and unit tests.
5. `scripts/localnet_weights.py` now reads the validator UID's live `last_update`, compares it with the current metagraph block and live `weights_rate_limit`, waits until submission is legal, then calls `bt.SetWeights` and performs bounded chain read-back.
6. The strict workflow no longer attempts to mutate `weights_rate_limit`; it requires a positive live value and exercises compliance with that value.

Current authoritative rerun:
- localnet run `32770361036` / run #33 on head `c6516218b14252e94fd976b796a2c72b4cc9ac74`;
- CI run #104: PASS;
- strict localnet #33: IN_PROGRESS at last check.

Important evidence boundary:
- chain-local subnet + neuron lifecycle: `CHAIN_LOCAL_PASS`;
- chain-local ServeAxon + metagraph discovery: `CHAIN_LOCAL_PASS`;
- chain-local signed BMP round trip: `CHAIN_LOCAL_PASS`;
- six-miner network: only `LOCAL_NETWORK_COMPONENT_PASS` until six independent chain-registered miners are exercised together;
- chain-local SetWeights execution/read-back: `RATE_LIMIT_AWARE_RERUN_IN_PROGRESS`;
- testnet neuron/ServeAxon/weight evidence: NOT_RUN;
- submission evidence: NOT_RUN.

Next canonical gate: the strict fresh-chain run must produce a successful `SetWeights` extrinsic and observable target weight after respecting the live 100-block rate limit. If that passes, M0 is closed. Then promote to a six-chain-registered-miner competitive local subnet before any funded Bittensor `test` mutation.

No local, chain-local, CI, or read-only testnet result may be presented as deployed testnet evidence.

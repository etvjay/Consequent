# EBI Status — Consequent

**Current:** `READY_TO_BUILD`

Canonical build authority:
1. `/GROUND_TRUTH.md`
2. `/audits.md`

Mechanism oracle: LOCAL_PASS.
Category boundary: FROZEN_v0.1.
Bittensor 11 architecture: truth-corrected 2026-08-24.
Toolchain evidence: CI_PASS — `bittensor==11.1.0` installs and the Consequent package/test suite passes on Python 3.10 and 3.12.
Implementation evidence: LOCAL_PASS + CI_PASS.

M0.1 identity/chain-state primitives: IMPLEMENTED_CI_PASS — explicit network settings, wallet/hotkey/netuid configuration, metagraph reads, neuron lookup, live weight-policy reads.
M0.2 serve/discover primitives: IMPLEMENTED_CI_PASS — `bt.ServeAxon` plan/execute helpers and metagraph-driven miner discovery.
M0.3 caller policy/auth hardening: IMPLEMENTED_CI_PASS — network mode fails closed, btauth verification returns caller identity, caller must pass metagraph registration/validator-permit policy.
Bittensor v11 contract tests: CI_PASS — `Subtensor`, `ServeAxon`, `SetWeights`, and `http_auth` symbols/intents verified against installed 11.1.0.
Expanded CI suite: 14/14 PASS on Python 3.10 and 3.12 (GitHub Actions run 32753525193).

Important evidence boundary:
- actual `ServeAxon` chain publication: NOT_RUN;
- actual metagraph endpoint visibility from our neuron: NOT_RUN;
- real signed validator → miner HTTP round-trip using real hotkeys: NOT_RUN;
- multi-miner networked evaluation: NOT_RUN;
- actual SetWeights plan against the target subnet: NOT_RUN;
- testnet evidence: NOT_RUN;
- submission evidence: NOT_RUN.

Next canonical gate: real wallet/hotkey fixtures + authenticated local network round-trip, then testnet registration/publication.

No local or CI result may be presented as testnet evidence.

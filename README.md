# Consequent

**A market for memory formation, settled by behavioral consequence.**

Consequent is a Bittensor subnet where miners transform prior execution experience into bounded **Behavioral Memory Patches (BMPs)** and validators reward those patches according to the measurable improvement they cause on concealed future tasks.

## Governing invariant

**STORED ≠ RECALLED ≠ INFLUENTIAL ≠ BENEFICIAL**

Consequent does not primarily reward persistence, retrieval, context injection, or plausible-sounding reflection. A miner earns weight only when its execution-derived memory improves future behavior under paired evaluation and survives regression and policy checks.

## Build authority

Before changing architecture, network behavior, scoring, hackathon claims, or deployment assumptions, read these in order:

1. [`GROUND_TRUTH.md`](./GROUND_TRUTH.md) — current externally verified rules and Bittensor implementation truth.
2. [`evaluation/EBI_STATUS.md`](./evaluation/EBI_STATUS.md) — strongest evidence actually earned and current milestone state.
3. [`audits.md`](./audits.md) — live build/release checklist. Older unchecked items must be reconciled against newer evidence records before being used as status claims.
4. [`skills/README.md`](./skills/README.md) — Subnet, Architecture, Memory Lifecycle, Evaluation, Adversary and Evidence Foundries.
5. [`architecture/README.md`](./architecture/README.md) — canonical system/reference architecture.
6. [`architecture/MEMORY_LIFECYCLE.md`](./architecture/MEMORY_LIFECYCLE.md) — BMP formation, admission, storage, retrieval, application and retirement.
7. [`architecture/PRODUCTION.md`](./architecture/PRODUCTION.md) — production service topology, reliability, security and promotion gates.

Historical templates, prior Bittensor versions, issue text, and old plans do not override those files.

## Status

`M0_CLOSED / CHAIN_LOCAL_ECONOMIC_LOOP_PASS`

M0 is proven on a strict fresh official Subtensor localnet: subnet and neuron lifecycle, `ServeAxon`, metagraph discovery, authenticated validator→miner BMP formation, live weight-policy compliance, accepted `SetWeights`, and chain read-back all passed. The authoritative closure run is GitHub Actions localnet run #34 (`32770499057`).

The next gate is **M1: six independently chain-registered miners competing under concealed evaluation, followed by competitive UID weights and chain read-back**.

Public Bittensor testnet mutation/deployment is still `NOT_RUN`. Do not describe Consequent as a working public-testnet subnet until the testnet evidence gate passes.

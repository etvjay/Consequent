# Consequent

**A market for memory formation, settled by behavioral consequence.**

Consequent is a Bittensor subnet where miners transform prior execution experience into bounded **Behavioral Memory Patches (BMPs)** and validators reward those patches according to the measurable improvement they cause on concealed future tasks.

## Governing invariant

**STORED ≠ RECALLED ≠ INFLUENTIAL ≠ BENEFICIAL**

Consequent does not primarily reward persistence, retrieval, context injection, or plausible-sounding reflection. A miner earns weight only when its execution-derived memory improves future behavior under paired evaluation and survives protocol admission, regression, and policy checks.

## Build authority

Before changing architecture, network behavior, scoring, hackathon claims, or deployment assumptions, read these in order:

1. [`GROUND_TRUTH.md`](./GROUND_TRUTH.md) — externally verified requirements and Bittensor implementation truth.
2. [`evaluation/EBI_STATUS.md`](./evaluation/EBI_STATUS.md) — strongest evidence actually earned and current milestone state.
3. [`audits.md`](./audits.md) — live build/release checklist.
4. [`evaluation/M2_ADVERSARIAL.md`](./evaluation/M2_ADVERSARIAL.md) — active threat model and attack evidence.
5. [`architecture/BITTENSOR_ECONOMICS.md`](./architecture/BITTENSOR_ECONOMICS.md) — Yuma/validator economics model and Consequent implications.
6. [`skills/README.md`](./skills/README.md) — Subnet, Architecture, Memory Lifecycle, Evaluation, Adversary and Evidence Foundries.
7. [`architecture/README.md`](./architecture/README.md) — canonical system/reference architecture.
8. [`architecture/MEMORY_LIFECYCLE.md`](./architecture/MEMORY_LIFECYCLE.md) — BMP formation, admission, storage, retrieval, application and retirement.
9. [`architecture/PRODUCTION.md`](./architecture/PRODUCTION.md) — production service topology, reliability, security and promotion gates.

Historical templates, pre-v11 Axon/Dendrite/Synapse examples, old issue text, and prior plans do not override those files.

## Current status

`M1_CLOSED / CHAIN_LOCAL_COMPETITIVE_ECONOMIC_LOOP_PASS / M2_ACTIVE`

### M0 — closed

A strict fresh official Subtensor localnet proved:

`registration → ServeAxon → metagraph discovery → signed BMP formation → live rate-limit compliance → SetWeights → chain read-back`

Authoritative run: GitHub Actions localnet run #34 / `32770499057`.

### M1 — closed

A fresh-chain six-miner competition proved six independent registrations, six authenticated miner services, six `ServeAxon` records, metagraph-only discovery, signed challenge fan-out, concealed paired evaluation, policy/regression gating, competitive weight construction, accepted `SetWeights`, and chain read-back.

Authoritative run: GitHub Actions `m1-localnet` run #1 / `32906478860`.

Controlled result:

```text
useful_generalizing_memory  → 0.6746805888 computed weight
                               0.6746795697 observed chain weight
overfit_memory              → 0.3253194112 computed weight
                               0.3253204303 observed chain weight
no_memory                   → 0
irrelevant_memory           → 0
harmful_memory              → 0
policy_violating_memory     → 0 (hard veto)
```

M1 evidence artifact: `consequent-m1-localnet-evidence`, artifact ID `9585670375`, digest `sha256:a55dbe1b34eafc0295e3c0398cec92b89039b181ea9e6d816ba609dbc6bb3b2b`.

### M2 — active

Implemented pressure controls include:
- BMP structural/provenance admission before causal scoring;
- declarative-only action grammar and payload-size/budget limits;
- challenge-response binding;
- semantic duplicate digests as audit telemetry, not novelty reward;
- score-jump, duplicate, downtime, stale-evidence and new-miner audit escalation;
- rolling score freshness and evaluator-version requalification;
- private-seed adaptive deep-evaluation selection;
- concealed-holdout serialization regression coverage;
- reference Yuma consensus/clipping model for mechanism falsification;
- independent-validator reference tests;
- 100-private-seed validator-dispersion harness;
- manual M2-V1 chain workflow for non-owner validator permits, independent rows, and actual post-epoch Yuma outcome.

The endpoint-churn pressure lane is now chain-local proven: run #12 /
`33577658110`, artifact `9827546184`. It moved one registered hotkey through
the live ServeAxon rate-limit window and verified refreshed discovery plus
signed traffic at the new endpoint.

The manual M2-V1 workflow is **designed, not yet evidence-backed**. It must not be represented as a passed multi-validator chain test until an actual run succeeds.

## Evidence boundaries

Public Bittensor testnet mutation/deployment is still `NOT_RUN`.

Consequent has **not yet proven**:
- multiple independent non-owner validators on chain;
- commit-reveal-on settlement end-to-end;
- ~~endpoint churn/restart behavior~~ on chain-local infrastructure (M2-C1 passed; public testnet still unrun);
- miner-validator collusion resistance on chain;
- public testnet registration/serving/weights;
- external consumer integration;
- production demand/economics.

Deployment alone is not the target. The subnet is only credible when the rewarded commodity, validator truth, Bittensor settlement, and consumer value all survive pressure.

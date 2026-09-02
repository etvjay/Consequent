# EBI Status — Consequent

**Current:** `M1_CLOSED / CHAIN_LOCAL_COMPETITIVE_ECONOMIC_LOOP_PASS / M2_ACTIVE`

Canonical build authority:
1. `/GROUND_TRUTH.md`
2. `/audits.md`
3. `/skills/README.md`
4. `/architecture/README.md`

Mechanism oracle: LOCAL_PASS.
Category boundary: FROZEN_v0.1.
Bittensor 11 architecture: truth-corrected 2026-08-24.
Toolchain evidence: CI_PASS — `bittensor==11.1.0` installs and the Consequent package/test suite passes on Python 3.10 and 3.12.

## M0 closure

Authoritative M0 run: GitHub Actions localnet run `32770499057` / run #34.

M0 proved one strict fresh-chain economic loop:

`registration → ServeAxon → metagraph discovery → signed BMP formation → live rate-limit compliance → SetWeights → chain read-back`

Final state: `LOCALNET_SET_WEIGHTS_READBACK_PASS`.

## M1 closure

Authoritative M1 run: GitHub Actions `m1-localnet` run `32906478860` / run #1.

The fresh-chain competitive topology completed successfully:
- fresh official Subtensor localnet: PASS;
- subnet registration/activation: PASS — netuid 2;
- owner/economic signer UID 0;
- six miner hotkeys burned-registered — UIDs 1–6;
- six authenticated FastAPI miner processes — ports 8091–8096;
- six `ServeAxon` publications;
- metagraph-only discovery;
- signed challenge fan-out;
- concealed paired A0/A1 evaluation;
- policy/regression gates;
- live `weights_rate_limit=100` respected;
- competitive `SetWeights` — extrinsic `124-0006`;
- chain read-back of competitive positive weights;
- artifact `consequent-m1-localnet-evidence`, ID `9585670375`, digest `sha256:a55dbe1b34eafc0295e3c0398cec92b89039b181ea9e6d816ba609dbc6bb3b2b`.

Final runner state: `M1_CHAIN_COMPETITION_PASS`.

Controlled computed weights:
- UID 4 / `useful_generalizing_memory`: `0.6746805888`;
- UID 3 / `overfit_memory`: `0.3253194112`;
- all other fixture miners: `0`.

Observed chain weights:
- UID 4: `0.6746795697`;
- UID 3: `0.3253204303`.

This closes M1. It does not prove multiple independent validators, production commit-reveal, public testnet mutation, consumer integration, or production demand.

## M2 current checkpoint

Current implementation head at this checkpoint: `b1bc8c0ba4dc6514aea8349d9c407167dfe81da9`.

Current-head CI and chain-local regressions are **PASS** — `ci` #164 /
`33577658164`, `localnet` #93 / `33577658111`, `m1-localnet` #51 /
`33577658106`, and `m2-churn-localnet` #12 / `33577658110`.

M2 controls now implemented and CI-proven include:
- admission before causal scoring;
- challenge binding, bounded patch count/bytes and declarative payload restrictions;
- provenance existence/family checks plus literal source grounding of rule condition key/value pairs;
- semantic BMP digest with miner self-label excluded;
- copycat durability pressure: copying source-bound memory does not manufacture generalization, while equivalent useful memory is not novelty-penalized;
- hidden holdouts excluded from miner request serialization;
- leaked hidden-instance conditions rejected by honest admission;
- policy hard veto plus non-compensable full-unit catastrophic-regression veto;
- audit escalation for score jumps, duplicates, downtime, stale evidence and new miners;
- bounded staged evaluation: cheap screening for all, priority deep evaluation, private random-audit floor, explicit cost ceiling;
- rolling score eligibility integrated into weight construction;
- rolling state bound to current UID + hotkey + evaluated endpoint + evaluator version + freshness;
- recycled UID / moved endpoint / disappearance / repeated failure / evaluator drift fail closed;
- 100-private-seed validator-dispersion pressure;
- transparent Yuma consensus/clipping reference model;
- miner-validator leaked-holdout pressure and minority-vs-majority stake boundary;
- validator-copying audit telemetry based on row similarity and private-evidence commitment reuse.

These are `CI_PASS`/reference controls, not claims that Subtensor has executed every M2 condition.

## M2 manual chain proofs

### M2-V1 — non-owner multi-validator consensus

`.github/workflows/m2-multivalidator-localnet.yml` exists as a manual workflow.

It is designed to prove two staked non-owner validators obtain real permits, miners enforce permits, three validators use independent private seeds, three rows settle, and actual post-epoch Subtensor incentives preserve behavioral-quality ordering.

State: `NOT_RUN`.

### M2-C1 — endpoint churn

`.github/workflows/m2-churn-localnet.yml` exists as a manual workflow.

It is designed to prove a same-hotkey ServeAxon endpoint move is reflected by refreshed metagraph discovery and signed traffic follows the new canonical endpoint.

State: `CHAIN_LOCAL_PASS` — GitHub Actions run `33577658110` / #12, artifact
`9827546184`, digest
`sha256:87947c466473604e422398037c236a83add6ae281166bd2e0ac69c5199e19f32`.
The same registered hotkey moved from endpoint A to endpoint B after the live
ServeAxon rate-limit window; current metagraph discovery and signed traffic
followed endpoint B.

### M2-V2 — commit-reveal-on settlement

Production-shaped proof harness is now implemented in
`.github/workflows/m2-commit-reveal-localnet.yml` and
`scripts/m2_commit_reveal_chain.py`. It keeps commit-reveal enabled, records the
timelocked plan/reveal round, asserts the row is not immediately visible, then
waits for application and an epoch outcome.

State: `NOT_RUN`.

## M2 residual blockers

M2 is **not closed**. Remaining blockers include:
- non-owner multi-validator chain proof;
- commit-reveal-on settlement;
- ~~real chain endpoint churn~~ (M2-C1 `CHAIN_LOCAL_PASS`);
- rolling multi-round chain settlement;
- realistic validator deep-evaluation cost measurement;
- explicit production executor action/capability vocabulary contract;
- majority validator economic capture as a known Bittensor-system boundary;
- public Bittensor testnet mutation/deployment.

M2 exit condition remains: no unresolved CRITICAL finding and no unbounded HIGH finding, with reproducible evidence and residual-risk statements for each closed attack.

Public Bittensor testnet mutations remain `NOT_RUN` and must not be inferred from local/reference evidence.

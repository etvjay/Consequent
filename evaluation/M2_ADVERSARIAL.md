# M2 — Adversarial Mechanism Pressure

Status: `ACTIVE`

M2 asks one question:

> Can an economically motivated miner or validator make Consequent reward something other than generalized beneficial behavioral influence?

M2 is not closed by test count. Each attack requires a named threat model, a bounded protocol/economic control, reproducible evidence, and an explicit residual-risk statement.

## Severity

- `CRITICAL` — breaks the rewarded commodity or validator economic integrity.
- `HIGH` — sustained profitable gaming or material validator-truth failure.
- `MEDIUM` — bounded degradation, availability, or auditability failure.
- `LOW` — nuisance or operational weakness.

M2 exit condition: no unresolved `CRITICAL` finding and no unbounded `HIGH` finding.

---

## Current evidence checkpoint

Current M2 head: `b94f008abe9fba838f0d5a35caf6afd586397567`.

Current-head CI and chain-local regressions are **PASS**: GitHub Actions `ci`
run #164 / `33577658164`, `localnet` #93 / `33577658111`, `m1-localnet` #51 /
`33577658106`, and endpoint-churn #12 / `33577658110`. The authoritative
historical M1 closure remains run #1 / `32906478860`; these fresh runs are
regressions of the current head, not a replacement for its evidence artifact.
The independent-validator M2-V1 run #6 / `33577658140` remains in progress.

---

## Attack matrix

| ID | Attack | Severity | Current control | Evidence | State |
|---|---|---:|---|---|---|
| M2-01 | forged / laundered source provenance | CRITICAL | every provenance ID must exist, match rule family, and every BMP condition key/value must occur in a cited same-family source episode | `consequent/admission.py`, admission/adversarial/collusion tests | `CI_PASS` |
| M2-02 | capability / executable smuggling | CRITICAL | BMP actions are bounded declarative tokens and payload conditions are scalar/safe; BMP cannot ship code/modules/tools | admission tests | `CI_PASS / ACTION_VOCABULARY_RESIDUAL` |
| M2-03 | patch-budget / oversized payload abuse | HIGH | request memory budget + serialized-byte ceiling + bounded schema | admission tests | `CI_PASS` |
| M2-04 | replayed response / wrong challenge binding | HIGH | response challenge ID must exactly match active challenge before admission/scoring; btauth replay/freshness controls remain separate | adversarial runner + auth tests | `CI_PASS` |
| M2-05 | copied semantic response | HIGH | canonical semantic digest surfaces duplicates without novelty penalty; copied source-bound BMPs remain source-bound across private seeds; equivalent useful BMPs may tie | copycat durability + duplicate telemetry tests | `CI_PASS / CHAIN_COPY_PRESSURE_NOT_RUN` |
| M2-06 | benchmark / holdout leakage | CRITICAL | hidden tasks never serialized to miner request; hidden-instance values absent from source cannot be laundered into admitted conditions | holdout secrecy + source-grounding + collusion tests | `CI_PASS / MULTI_VALIDATOR_CHAIN_NOT_RUN` |
| M2-07 | source-instance memorization | HIGH | shifted concealed holdouts + 100-private-seed dispersion gate; useful generalizer must beat source-bound overfit | authoritative M1 + validator dispersion tests | `CHAIN_LOCAL_PASS_ORIGINAL_M1 / CURRENT_RUNTIME_CHAIN_REGRESSION_PENDING` |
| M2-08 | catastrophic regression hidden by aggregate uplift | CRITICAL | any full-unit behavioral regression (`ΔU <= -1` in MVP utility scale) hard-vetoes reward; smaller regressions remain continuously penalized | scoring regression-compensation test | `CI_PASS / CURRENT_RUNTIME_CHAIN_REGRESSION_PENDING` |
| M2-09 | policy violation compensated by uplift | CRITICAL | any policy violation hard-vetoes score | scoring tests + authoritative M1 | `CHAIN_LOCAL_PASS_ORIGINAL_M1 / CURRENT_RUNTIME_CHAIN_REGRESSION_PENDING` |
| M2-10 | sudden score gaming / selective evaluation | HIGH | audit signals escalate deep evaluation; budgeted staged planner prioritizes risk plus private random-audit floor | audit policy, scheduler, staged-evaluation tests | `CI_PASS / LIVE_COST_MEASUREMENT_PENDING` |
| M2-11 | repeated downtime / stale winner | HIGH | rolling economic state feeds weight construction; repeated failures, stale evidence, old evaluator epochs, identity mismatch, and unevaluated endpoint changes become ineligible | score-state + rolling-economics tests | `CI_PASS / ROLLING_CHAIN_SETTLEMENT_NOT_RUN` |
| M2-12 | miner churn / endpoint changes / UID reuse | MEDIUM | current metagraph only; score binds UID+hotkey; recycled UID cannot inherit score; endpoint move must be re-evaluated | churn identity tests; `m2-churn-localnet` run #12 / artifact `9827546184` | `CHAIN_LOCAL_PASS` |
| M2-13 | miner-validator collusion / leaked holdout | CRITICAL | honest admission rejects leaked hidden-instance conditions; raw leaked advantage fails to transfer to independent seeds; minority malicious validator row is clipped in Yuma reference model | collusion pressure tests | `CI_PASS_REFERENCE / MULTI_VALIDATOR_CHAIN_NOT_RUN` |
| M2-14 | validator copying / independence failure | HIGH | identical rows are weak audit evidence; shared private challenge/evaluation commitments are stronger telemetry; no automatic reward penalty | validator audit tests | `CI_PASS / CHAIN_EVIDENCE_NOT_RUN` |
| M2-15 | evaluator-version drift | HIGH | old evaluator score is immediately economically ineligible; first new-version success starts a fresh score epoch; rolling weight construction enforces it | score-state + rolling-economics tests | `CI_PASS / ROLLING_CHAIN_SETTLEMENT_NOT_RUN` |
| M2-16 | seed variance / lucky miner | HIGH | 100-private-seed dispersion gate; useful generalizer must remain top and policy-violating memory never receives positive weight | validator-dispersion tests/script | `CI_PASS` |
| M2-17 | duplicate rule IDs / ambiguous semantics | MEDIUM | duplicate rule IDs rejected before evaluation | admission tests | `CI_PASS` |
| M2-18 | forged novelty / self-label manipulation | MEDIUM | semantic digest excludes miner self-label; novelty is not rewarded | admission + copycat tests | `CI_PASS` |
| M2-19 | malicious validator minority overweights unsafe/colluding miner | CRITICAL | reference Yuma clipping requires stake-supported consensus; unsupported minority row receives zero target consensus/incentive in pressure fixtures | Yuma + multivalidator + collusion tests | `CI_PASS_REFERENCE / CHAIN_NOT_RUN` |
| M2-20 | malicious validator stake crosses consensus threshold | CRITICAL | **no Consequent-local repair claimed** once malicious stake satisfies Bittensor consensus support; security depends on Bittensor economic/governance assumptions | Yuma pressure tests | `KNOWN_SYSTEM_BOUNDARY` |

---

## Protocol/economic controls now implemented

### 1. Admission before causal scoring

```text
signed response
→ challenge binding
→ BMP structural/source-grounding admission
→ semantic digest + duplicate telemetry
→ concealed causal evaluation
→ policy/catastrophic-regression vetoes
→ rolling identity/freshness eligibility
→ normalized weight construction
```

A protocol-invalid BMP receives zero current-round economic score. High task utility cannot rescue an invalid artifact.

### 2. Literal source grounding for bmp/0.1

For every rule condition `(key, value)`, at least one same-family episode explicitly cited by that rule must contain the same `(key, value)`.

This permits abstraction by dropping volatile fields while forbidding a miner from introducing validator-private or otherwise unseen instance facts and laundering them through a legitimate provenance ID.

This is intentionally a bmp/0.1 rule, not a universal claim about all future memory representations.

### 3. Duplicate/copy policy

```text
same semantic BMP
→ same digest
→ audit signal
≠ automatic punishment
```

Two miners may independently produce the same useful memory and earn equally. Conversely, copying a source-bound patch does not make it generalize: consequence remains the reward criterion.

### 4. Non-compensable critical failures

Policy violations are hard-vetoed. In the MVP utility scale, a full-unit behavioral regression (`ΔU <= -1`) is also hard-vetoed, so many unrelated wins cannot purchase permission to destroy previously-correct behavior.

Smaller regressions remain part of continuous regression-rate/uncertainty penalties rather than being mislabeled catastrophic.

### 5. Rolling economic eligibility

Persistent credit is bound to current chain identity and evaluation truth:

```text
(hotkey, current UID placement, evaluated endpoint, evaluator version, freshness)
```

A recycled UID cannot inherit another hotkey's score. A moved endpoint is ineligible until the same hotkey is successfully evaluated at the new endpoint. Disappeared miners are absent from the current weight vector. Repeated transport failure and stale evidence fail closed.

### 6. Staged validator evaluation

Every miner receives cheap screening. Deep concealed evaluation capacity is allocated first to high-priority audit signals and then, when capacity remains, to a private random-audit floor.

The planner exposes both estimated and maximum cost units. It changes evidence depth, never reward directly.

### 7. Validator independence / Yuma boundary

Consequent separates three layers:

1. an honest validator enforces Consequent admission/evaluation rules;
2. independent honest validators should converge statistically on underlying quality despite private seeds;
3. Bittensor/Yuma decides which stake-supported validator opinions become economic consensus.

A malicious validator can ignore Consequent and submit arbitrary weights. Consequent cannot cryptographically force a validator to run its reference evaluator. The defense against unsupported minority behavior is Bittensor's economic consensus; majority economic capture remains a system boundary.

The local Yuma implementation is a transparent falsification/reference model only. Subtensor is authoritative economic evidence.

---

## Manual chain proofs designed but not yet earned

### M2-V1 — non-owner multi-validator consensus

Workflow: `.github/workflows/m2-multivalidator-localnet.yml` (`workflow_dispatch` only).

Required evidence:
- two independently registered/staked non-owner validators obtain real permits;
- miners enforce actual validator permits;
- owner + two non-owner validators evaluate the same six miners with different private seeds;
- all three settle independent rows;
- after an epoch, actual Subtensor miner incentives preserve the intended quality ordering.

Commit-reveal is disabled only for this observable-row fixture.

State: `NOT_RUN`.

### M2-C1 — endpoint churn — passed

Workflow: `.github/workflows/m2-churn-localnet.yml` (`workflow_dispatch` only).

Required evidence:
- same registered miner hotkey serves endpoint A;
- endpoint A is discovered and used;
- miner restarts on endpoint B and republishes `ServeAxon`;
- refreshed metagraph no longer treats A as canonical;
- signed validator traffic succeeds at B.

State: `CHAIN_LOCAL_PASS`.

Evidence: GitHub Actions run `33577658110` / #12, artifact `9827546184`,
digest `sha256:87947c466473604e422398037c236a83add6ae281166bd2e0ac69c5199e19f32`.
The same hotkey was republished only after the chain-owned ServeAxon window;
the refreshed metagraph endpoint and signed challenge response both followed
endpoint B.

### M2-V2 — commit-reveal-on settlement

Production-shaped proof harness is implemented in
`.github/workflows/m2-commit-reveal-localnet.yml` and
`scripts/m2_commit_reveal_chain.py`; it keeps commit-reveal enabled and waits
for delayed row application plus an epoch outcome.

Required evidence:
- commit-reveal remains enabled;
- validator submits production-shaped weights through the correct path;
- reveal/application occurs after the configured epoch delay;
- final chain state/economic outcome is captured without disabling commit-reveal.

State: `NOT_RUN`.

---

## Residual risks that still block M2 closure

1. actual non-owner multi-validator chain behavior is unproven;
2. commit-reveal-on settlement is unproven;
3. rolling multi-round economic state has not yet been used in an authoritative chain settlement loop;
4. validator evaluation cost is bounded in a reference planner but not measured under realistic deep execution;
5. action tokens are declarative-only, but a production executor capability/action registry is not yet frozen as an explicit protocol field;
6. majority validator economic capture is a Bittensor-system security boundary, not locally solvable by Consequent;
7. public Bittensor testnet mutation remains `NOT_RUN`.

---

## Next pressure tranche

1. inspect the current-head chain-local regression artifacts for any semantic-ordering failure;
2. complete M2-V1 multi-validator localnet and verify real permits + post-epoch chain incentives;
3. run the M2-V2 commit-reveal-on settlement proof;
4. execute a multi-round rolling-weight chain/simulation harness with disappearance, endpoint move and evaluator migration;
5. measure actual canary/deep evaluation cost and set a validator economic budget;
6. freeze a production capability/action vocabulary contract without conflating it with source provenance;
7. only then reassess M2 exit readiness and M3 consumer integration.

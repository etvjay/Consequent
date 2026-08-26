# M2 — Adversarial Mechanism Pressure

Status: `ACTIVE`

M2 exists to answer one question:

> Can an economically motivated miner or validator make Consequent reward something other than generalized beneficial behavioral influence?

M2 is not closed by a large unit-test count. Each attack must have a named threat model, a protocol mitigation, reproducible pressure evidence, and a residual-risk statement.

## Severity

- `CRITICAL` — breaks the rewarded commodity or validator economic integrity.
- `HIGH` — sustained profitable gaming or material validator-truth failure.
- `MEDIUM` — bounded degradation, availability, or auditability failure.
- `LOW` — nuisance or operational weakness.

M2 exit condition: no unresolved `CRITICAL` finding and no unbounded `HIGH` finding.

---

## Attack matrix

| ID | Attack | Severity | Current control | Evidence | State |
|---|---|---:|---|---|---|
| M2-01 | forged source provenance | CRITICAL | validator admission requires every provenance ID to exist in supplied source episodes and match rule family | `tests/test_admission.py`, `tests/test_adversarial_runner.py` | `CI_PASS_ON_PRIOR_M2_HEAD / CURRENT_HEAD_PENDING` |
| M2-02 | capability/executable smuggling | CRITICAL | BMP actions restricted to bounded declarative tokens; multiline/control payloads rejected before scoring | `tests/test_admission.py` | `CI_PASS_ON_PRIOR_M2_HEAD / CURRENT_HEAD_PENDING` |
| M2-03 | patch-budget / oversized payload abuse | HIGH | request memory budget + serialized-byte ceiling + bounded schema | `tests/test_admission.py` | `CI_PASS_ON_PRIOR_M2_HEAD / CURRENT_HEAD_PENDING` |
| M2-04 | replayed response / wrong challenge binding | HIGH | response challenge ID must exactly match active challenge before admission/scoring | `tests/test_adversarial_runner.py` | `CI_PASS_ON_PRIOR_M2_HEAD / CURRENT_HEAD_PENDING` |
| M2-05 | copied semantic response | HIGH | canonical semantic BMP digest; duplicates surfaced as audit signal, not novelty penalty | `tests/test_admission.py`, `tests/test_adversarial_runner.py` | `CI_PASS_ON_PRIOR_M2_HEAD / CURRENT_HEAD_PENDING` |
| M2-06 | benchmark/holdout leakage | CRITICAL | active miner request serialization excludes concealed holdouts; procedural/private-seed generation remains separate | holdout-secrecy regression test + architecture | `LOCAL_DESIGN_PASS / MULTI_VALIDATOR_CHAIN_NOT_RUN` |
| M2-07 | source-instance memorization | HIGH | shifted concealed holdouts; useful generalizer must beat source-bound overfit | M1 chain competition + seeded validator-dispersion harness | `CHAIN_LOCAL_PASS / SEEDED_LOCAL_PASS_PENDING_CI` |
| M2-08 | catastrophic regression hidden by mean uplift | CRITICAL | explicit regression rate penalty | golden/M1 controlled evaluator | `LOCAL_PASS` |
| M2-09 | policy violation compensated by uplift | CRITICAL | any policy violation hard-vetoes score | golden + M1 chain competition | `CHAIN_LOCAL_PASS` |
| M2-10 | sudden score gaming | HIGH | score-jump signal escalates deep evaluation | `validator/audit_policy.py`, tests | `CI_PASS_ON_PRIOR_M2_HEAD / CURRENT_HEAD_PENDING` |
| M2-11 | repeated downtime / stale winner | HIGH | rolling score state zeroes economically eligible score after bounded consecutive failures or staleness | `validator/score_state.py`, `tests/test_score_state.py` | `CI_PASS_ON_PRIOR_M2_HEAD / CURRENT_HEAD_PENDING` |
| M2-12 | miner churn / endpoint changes | MEDIUM | metagraph-based discovery; persistent churn pressure not yet exercised | M1 discovery only | `PARTIAL` |
| M2-13 | miner-validator collusion | CRITICAL | independent validators/private seeds + Yuma consensus boundary modeled; real multi-validator chain evidence absent | `tests/test_multivalidator_consensus.py`, `consequent/yuma_reference.py` | `REFERENCE_MODEL_PASS_PENDING_CI / CHAIN_NOT_RUN` |
| M2-14 | validator copying/collusion | HIGH | independent seed requirement, semantic/timing evidence, Yuma clipping reference model, validator-dispersion harness | `tests/test_multivalidator_consensus.py`, `tests/test_validator_dispersion.py` | `REFERENCE_MODEL_PASS_PENDING_CI / CHAIN_NOT_RUN` |
| M2-15 | evaluator-version drift | HIGH | old evaluator scores are immediately economically ineligible; first score under new evaluator resets EMA/history | `validator/score_state.py`, `tests/test_score_state.py` | `CI_PASS_ON_PRIOR_M2_HEAD / CURRENT_HEAD_PENDING` |
| M2-16 | seed variance / lucky miner | HIGH | uncertainty discount + 100-private-seed dispersion gate; useful generalizer must remain top and above overfit across all seeds | `consequent/validator_dispersion.py`, `tests/test_validator_dispersion.py`, `scripts/validator_dispersion.py` | `SEEDED_LOCAL_PASS_PENDING_CI` |
| M2-17 | duplicate rule IDs / ambiguous semantics | MEDIUM | duplicate rule IDs rejected | `tests/test_admission.py` | `CI_PASS_ON_PRIOR_M2_HEAD / CURRENT_HEAD_PENDING` |
| M2-18 | forged novelty / self-label manipulation | MEDIUM | semantic digest excludes miner self-label; novelty is not rewarded | `tests/test_admission.py` | `CI_PASS_ON_PRIOR_M2_HEAD / CURRENT_HEAD_PENDING` |
| M2-19 | malicious validator minority overweights unsafe miner | CRITICAL | Yuma reference clipping at stake-supported consensus threshold prevents unsupported weight from becoming miner incentive | `tests/test_yuma_reference.py`, `tests/test_multivalidator_consensus.py`, `scripts/yuma_pressure.py` | `REFERENCE_MODEL_PASS_PENDING_CI / CHAIN_NOT_RUN` |
| M2-20 | malicious validator stake crosses consensus threshold | CRITICAL | no local mitigation claimed; explicit economic-security boundary. Requires stake/governance assumptions and chain evidence. | `tests/test_multivalidator_consensus.py`, `scripts/yuma_pressure.py` | `KNOWN_SYSTEM_BOUNDARY` |

---

## Current protocol changes introduced by M2

### Admission before scoring

Canonical validator order is now:

```text
signed response
→ challenge binding
→ BMP structural/provenance admission
→ semantic digest + duplicate telemetry
→ concealed causal evaluation
→ veto/regression/uncertainty score
→ rolling eligibility/freshness
→ weight construction
```

A rejected BMP receives zero economic score. Validator evaluation must never rescue a protocol-invalid artifact through high apparent task utility.

### Duplicate output policy

Consequent does not reward novelty. Two miners may independently discover the same useful behavioral rule and should not be penalized merely for equivalence.

Therefore:

```text
same semantic BMP
→ same digest
→ audit/collusion signal
≠ automatic punishment
```

Deep evaluation, timing correlation, cross-validator comparison, and response-history evidence should determine whether copying is economically relevant.

### Audit escalation

Suspicion changes evaluation depth, not guilt. Current triggers include:
- sudden score jump;
- duplicate semantic output;
- repeated unavailability;
- stale evaluation evidence;
- new-miner exploration.

Adaptive Stage-C selection provides a private-seed random-audit floor in addition to explicit triggers.

### Evaluator epoch boundary

Scores are evaluator-version scoped. When the validator's evaluator version changes:

```text
old rolling score → economically ineligible
new successful evaluation → new EMA epoch, sample_count = 1
```

A miner cannot inherit historical economic credit across a changed evaluator truth function.

### Multi-validator / Yuma boundary

Consequent now separates two claims:

1. independent validators should derive non-identical rows from private evidence while converging statistically on behavioral quality;
2. Bittensor/Yuma decides which stake-supported opinions become economic consensus.

The local Yuma helper is a reference model only. It is used to falsify Consequent's evaluator-to-weight mechanism before expensive chain experiments. Subtensor remains authoritative economic evidence.

---

## Current next pressure tranche

1. pass current-head CI, M0 regression and M1 six-miner regression with all M2/Yuma changes;
2. run/report the 100-private-seed validator-dispersion harness and retain evidence;
3. sweep malicious validator stake around the live/reference `kappa` threshold and record the boundary where unsafe consensus becomes possible;
4. run M1 topology under miner disappearance/restart and endpoint churn;
5. build an actual chain-local multi-validator harness using independently registered hotkeys and private challenge seeds;
6. prove validator permit/activity semantics rather than relying on owner-validator special status;
7. prove commit-reveal enabled settlement rather than disabling it for immediate read-back;
8. only then decide whether M2 is strong enough for consumer integration/public-testnet preparation.

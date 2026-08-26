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
| M2-01 | forged source provenance | CRITICAL | validator admission requires every provenance ID to exist in supplied source episodes and match rule family | `tests/test_admission.py`, `tests/test_adversarial_runner.py` | `CI_AWAITING` |
| M2-02 | capability/executable smuggling | CRITICAL | BMP actions restricted to bounded declarative tokens; multiline/control payloads rejected before scoring | `tests/test_admission.py` | `CI_AWAITING` |
| M2-03 | patch-budget / oversized payload abuse | HIGH | request memory budget + serialized-byte ceiling + bounded schema | `tests/test_admission.py` | `CI_AWAITING` |
| M2-04 | replayed response / wrong challenge binding | HIGH | response challenge ID must exactly match active challenge before admission/scoring | `tests/test_adversarial_runner.py` | `CI_AWAITING` |
| M2-05 | copied semantic response | HIGH | canonical semantic BMP digest; duplicates surfaced as audit signal, not novelty penalty | `tests/test_admission.py`, `tests/test_adversarial_runner.py` | `CI_AWAITING` |
| M2-06 | benchmark/holdout leakage | CRITICAL | source request excludes concealed holdouts; procedural/private-seed design | existing architecture + new pressure test required | `PARTIAL` |
| M2-07 | source-instance memorization | HIGH | shifted concealed holdouts; useful generalizer must beat source-bound overfit | M1 chain competition | `CHAIN_LOCAL_PASS` |
| M2-08 | catastrophic regression hidden by mean uplift | CRITICAL | explicit regression rate penalty | golden/M1 controlled evaluator | `LOCAL_PASS` |
| M2-09 | policy violation compensated by uplift | CRITICAL | any policy violation hard-vetoes score | golden + M1 chain competition | `CHAIN_LOCAL_PASS` |
| M2-10 | sudden score gaming | HIGH | score-jump signal escalates deep evaluation | `validator/audit_policy.py`, tests | `CI_AWAITING` |
| M2-11 | repeated downtime / stale winner | HIGH | failures and stale evidence trigger deep requalification | `validator/audit_policy.py`, tests | `CI_AWAITING / REWARD_DECAY_NOT_IMPLEMENTED` |
| M2-12 | miner churn / endpoint changes | MEDIUM | metagraph-based discovery; persistent churn pressure not yet exercised | M1 discovery only | `PARTIAL` |
| M2-13 | miner-validator collusion | CRITICAL | independent challenges/validators proposed; no multi-validator evidence yet | mechanism design only | `OPEN` |
| M2-14 | validator copying/collusion | HIGH | independent seeds/evidence digests proposed; no dispersion harness yet | mechanism design only | `OPEN` |
| M2-15 | evaluator-version drift | HIGH | evaluator version in challenge; migration/reset policy not implemented | schema only | `OPEN` |
| M2-16 | seed variance / lucky miner | HIGH | uncertainty discount exists; broad procedural multi-seed network test pending | local golden robustness only | `PARTIAL` |
| M2-17 | duplicate rule IDs / ambiguous semantics | MEDIUM | duplicate rule IDs rejected | `tests/test_admission.py` | `CI_AWAITING` |
| M2-18 | forged novelty / self-label manipulation | MEDIUM | semantic digest excludes miner self-label; novelty is not rewarded | `tests/test_admission.py` | `CI_AWAITING` |

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

The next step is to feed these triggers into an adaptive Stage B/Stage C evaluation scheduler.

---

## Next pressure tranche

1. prove active challenge serialization contains no concealed holdout fields/data;
2. implement rolling miner state with freshness/requalification and bounded downtime decay;
3. implement adaptive deep-evaluation selection from audit signals;
4. run copied-response miners across multiple private seeds and prove copying source-bound output does not create durable uplift;
5. add two-validator independent-seed simulation and rank-dispersion evidence;
6. add explicit evaluator-version migration/reset test;
7. run M1 topology under miner disappearance/restart and endpoint churn;
8. then decide whether M2 is strong enough for consumer integration/public-testnet preparation.

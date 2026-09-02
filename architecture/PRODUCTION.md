# Consequent Production Architecture

This document defines the production operating shape that follows from the proven M0/M1 chain-local mechanism and the active M2 adversarial program.

Production goal:

> Run Consequent as a reliable Bittensor subnet whose independent validators can continuously discover miners, issue concealed formation challenges, evaluate causal behavioral uplift, and publish defensible weights while external runtimes consume accepted BMPs safely.

## 1. Production topology

```text
                         ┌──────────────────────┐
                         │ Bittensor Subtensor  │
                         │ identity / Yuma /    │
                         │ weights / emissions  │
                         └──────────┬───────────┘
                                    │
                  metagraph / permits / weights / ServeAxon
                                    │
          ┌─────────────────────────┴──────────────────────────┐
          │                                                    │
┌─────────▼─────────┐                                ┌─────────▼─────────┐
│ Validator Set     │                                │ Miner Population  │
│                  │                                │                  │
│ private seeds    │◄──── btauth/1 signed HTTP ───►│ formation API    │
│ challenge gen    │                                │ strategy/model   │
│ admission        │                                │ BMP construction │
│ paired evaluator │                                │ telemetry        │
│ score state      │                                └───────────────────┘
│ weight scheduler │
└─────────┬─────────┘
          │ accepted/evaluated BMP references
          ▼
┌─────────────────────┐        ┌────────────────────────┐
│ Evidence Store      │        │ Consumer Integration   │
│ append-only records │        │ episode ingest         │
│ digests/commitments │        │ BMP registry/storage   │
│ chain references    │        │ retrieval/application  │
└─────────────────────┘        └────────────────────────┘
```

Bittensor owns network identity, registration, validator permits/activity, stake-weighted consensus, clipping, bonds/dividends, weight settlement and emissions. Consequent owns the digital commodity, HTTP protocol, challenge generation, admission rules, causal evaluator, score state and evidence.

## 2. Validator production services

### Metagraph / consensus watcher
- refresh UID/hotkey/axon state;
- detect registration, deregistration and endpoint churn;
- record validator permit/stake/activity state;
- read live weight constraints;
- record tempo, kappa, validator cap, activity window, bond/Yuma policy and commit-reveal state.

### Challenge generator
- sample task family and latent rule;
- generate source episodes;
- independently generate concealed holdouts;
- version generator/evaluator grammar;
- preserve private seeds;
- emit public commitments without exposing active holdouts.

### Query scheduler
- select miner sample;
- sign requests;
- enforce deadlines/timeouts and bounded concurrency;
- retry only when replay/freshness semantics permit;
- distinguish unavailable, unauthorized, malformed and invalid responses.

### Admission engine
Before expensive evaluation reject:
- wrong challenge binding;
- schema/version violations;
- forged/mismatched provenance;
- memory-budget or serialized-size overflow;
- duplicate rule IDs / ambiguous shape;
- executable/capability payloads;
- unsafe action/condition grammar.

Semantic duplicate BMPs are audit signals, not automatic guilt or novelty penalties.

### Evaluator workers
- paired A0/A1 execution;
- matched seeds and constant capabilities;
- concealed future tasks;
- family utility;
- regression and policy violation detection;
- cost/latency metrics where relevant;
- adaptive repeat sampling for uncertain/suspicious miners.

### Score service
Maintains:
- per-family rolling evidence;
- robust uplift and uncertainty;
- recency/sample requirements;
- consecutive-failure/downtime state;
- policy hard vetoes;
- evaluator-version epochs;
- audit signals for score jumps, duplicates, stale evidence and new miners.

Old evaluator-version scores are economically ineligible. First success under a new evaluator starts a new score epoch rather than inheriting old credit.

### Weight scheduler
- convert eligible miner scores to non-negative normalized UID weights;
- read live rate limit/version/min-max constraints;
- obey validator activity requirements;
- handle commit-reveal state rather than assuming immediate visibility;
- plan/dry-run mutations where possible;
- submit weights;
- record transaction/commit/reveal evidence;
- verify the chain/Yuma result independently of Consequent's local reference model.

## 3. Multi-validator invariant

Production Consequent must not require validators to share exact challenges or identical rows.

Required property:

```text
same latent commodity semantics
+ independent private seeds
+ different concealed instances
→ non-identical validator rows
→ statistically convergent miner-quality ranking
→ stake-supported Bittensor consensus
```

The local `consequent.yuma_reference` helper exists only to falsify our evaluator-to-weight reasoning cheaply. It is not authoritative chain evidence.

Security boundary: if adversarial validator stake itself crosses Bittensor's consensus threshold, Consequent cannot locally repair the economic majority. That is a network/economic assumption which must be stated rather than hidden inside evaluator logic.

## 4. Miner production services

Each miner is independently deployable and competitive.

Required components:
- wallet/hotkey + network/netuid config;
- HTTP service;
- fail-closed btauth verification;
- registered caller authorization;
- validator-permit/stake policy in production mode;
- open formation-strategy adapter;
- BMP structural validation before response;
- request resource/rate guards by verified identity;
- health/readiness + structured telemetry;
- graceful restart/shutdown.

Miner algorithm internals remain open competition.

## 5. Consumer integration surface

The consumer does not need to run a validator.

Reference responsibilities:
- normalized execution-episode ingest;
- request competitive BMP formation;
- persist accepted BMPs with lifecycle metadata;
- retrieve by scope/trigger under a memory budget;
- apply declarative guidance without adding capabilities;
- record influence/outcome evidence where possible;
- expire/supersede/revoke stale or unsafe BMPs.

## 6. Availability and failure policy

### Miner timeout
Current challenge contribution is unavailable/zero; batch continues; repeated downtime eventually removes old score eligibility.

### Validator evaluator failure
Mark sample invalid rather than silently penalizing the miner; retry under bounded policy and retain evaluator-failure evidence.

### Chain unavailable
Retain the computed score snapshot but do not claim weight publication; do not regenerate a different challenge solely because settlement was delayed.

### Evidence store unavailable
Fail settlement closed if the required evidence cannot be durably recorded.

### Evaluator version change
Old score state becomes ineligible until requalified under the new evaluator epoch.

## 7. Security / privacy policies

- network/testnet/live miner mode requires authentication;
- signed identity and authorization are separate checks;
- active holdout seeds/tasks never sent to miners;
- raw body/path preserved for btauth verification;
- replay cache bounded and deployment-appropriate;
- wallet secrets never enter logs/artifacts;
- public challenge commitment separated from private holdout material;
- BMP is declarative-only and cannot auto-install code/tools/models;
- duplicate outputs escalate audits instead of creating a novelty reward;
- external consumer namespaces remain isolated.

## 8. Evidence and observability

Validator metrics/evidence should include:
- discovered/served miners and endpoint churn;
- validator permit/activity state;
- request success/error class and latency;
- admission rejection reasons;
- evaluator version/private challenge commitment;
- evaluation cost by miner/family;
- uplift/regression/policy/uncertainty/sample counts;
- audit-escalation reason;
- rolling eligible score;
- cross-validator score/rank dispersion where available;
- live kappa/tempo/activity/bond/Yuma environment;
- commit/reveal/submission state;
- chain rate-limit remaining;
- accepted transaction and eventual chain/Yuma outcome.

A batch without complete required evidence must not be promoted as proof.

## 9. Deployment stages

```text
M0     one-miner strict chain-local economic loop                 CLOSED
M1     six-miner competitive chain-local economic loop            CLOSED
M2     adversarial mechanism pressure                             ACTIVE
M2-V1  non-owner multi-validator chain-local/Yuma proof           DESIGNED / IN PROGRESS
M2-C1  endpoint churn / ServeAxon refresh                        CHAIN_LOCAL_PASS
M2-V2  commit-reveal-on chain-local settlement                    HARNESS READY / NOT_RUN
M3     external consumer integration                              PENDING
T1     funded Bittensor public-test deployment                    PENDING
T2     repeated public-test multi-validator operation             PENDING
P0     production candidate                                       PENDING
```

M1 authoritative run: `32906478860`.

M2-V1 is intentionally a manual evidence workflow because validator permits/Yuma outcomes depend on epoch timing. The current run is still in progress and is **not evidence that it passed**. M2-C1 is chain-local proven by Actions run #12 / `33577658110` (artifact `9827546184`): the same hotkey moved through the live ServeAxon window and signed traffic followed the refreshed endpoint.

## 10. Release gates

Before public-test mutation:
- M1 remains regression-green;
- no unresolved CRITICAL M2 finding and no unbounded HIGH finding;
- provenance/capability/admission controls are CI-backed;
- validator-dispersion pressure is evidence-backed;
- non-owner validator permit semantics are understood/proven or explicitly bounded;
- commit-reveal behavior has a dedicated proof plan;
- lifecycle expiry/supersession/revocation surface is implemented sufficiently for consumer use;
- evidence ledger and cold-clone setup are complete.

Before production candidate:
- repeated public-test rounds;
- multiple independent permitted validators;
- statistically convergent private-seed evaluation;
- commit-reveal-on settlement proven;
- validator cost envelope measured;
- leakage/copying/collusion/churn/restart pressure-tested;
- consumer integration demonstrates actual beneficial influence;
- monitoring/runbooks and security review complete;
- demand-side reason for the subnet to receive economic support is demonstrated.

Deployment alone is insufficient. Production promotion requires mechanism correctness, validator-economic correctness, evidence quality and consumer value.

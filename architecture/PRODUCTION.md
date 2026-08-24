# Consequent Production Architecture

This document defines the production operating shape that follows from the mechanism and M0 chain-local proof.

Production goal:

> Run Consequent as a reliable Bittensor subnet whose validators can continuously discover miners, issue concealed formation challenges, evaluate causal behavioral uplift, and publish defensible weights while external runtimes consume accepted BMPs safely.

---

## 1. Production topology

```text
                         ┌──────────────────────┐
                         │ Bittensor Subtensor  │
                         │ registration/weights │
                         └──────────┬───────────┘
                                    │
                  metagraph / weights / ServeAxon
                                    │
          ┌─────────────────────────┴──────────────────────────┐
          │                                                    │
┌─────────▼─────────┐                                ┌─────────▼─────────┐
│ Validator Cluster │                                │ Miner Population  │
│                  │                                │                  │
│ metagraph watch  │◄──── btauth/1 signed HTTP ───►│ formation API    │
│ challenge gen    │                                │ strategy/model   │
│ evaluator workers│                                │ BMP construction │
│ score state      │                                │ telemetry        │
│ weight scheduler │                                └───────────────────┘
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

---

## 2. Validator production services

### Metagraph watcher
Responsibilities:
- refresh subnet state;
- maintain UID/hotkey/axon map;
- detect registration/deregistration;
- record validator permit/stake state;
- flag stale or invalid served endpoints.

### Challenge generator
Responsibilities:
- sample task family;
- generate latent rule/environment;
- create source episodes;
- create concealed holdouts independently;
- version generator grammar;
- preserve private seeds;
- emit challenge commitments.

### Query scheduler
Responsibilities:
- select miner sample;
- sign requests;
- enforce deadlines/timeouts;
- bound concurrency;
- retry only when replay/freshness semantics permit;
- distinguish unavailable, unauthorized, malformed and invalid responses.

### Admission engine
Cheap pre-evaluation rejection:
- schema;
- provenance;
- budget;
- duplicate/digest;
- capability smuggling;
- action grammar;
- challenge binding;
- deadline/freshness.

### Evaluator workers
Responsibilities:
- paired A0/A1 execution;
- matched seeds;
- task-family utility;
- policy violation detection;
- regression accounting;
- cost/latency metrics where relevant;
- repeat sampling for uncertain miners.

### Score service
Maintains:
- per-family rolling evidence;
- robust mean/quantile statistics;
- uncertainty;
- recent-sample requirements;
- downtime decay;
- policy hard vetoes;
- evaluator-version epochs.

### Weight scheduler
Responsibilities:
- read live subnet hyperparameters;
- obey `weights_rate_limit`;
- obey `weights_version`;
- handle min/max weight constraints;
- handle commit-reveal state;
- plan/dry-run mutations where possible;
- submit weights;
- verify chain acceptance/read-back;
- write chain evidence.

---

## 3. Miner production services

Each miner should be independently deployable.

Required components:
- wallet/hotkey config;
- network/netuid config;
- HTTP service;
- fail-closed btauth verification;
- registered-caller authorization policy;
- optional validator-permit/stake threshold policy;
- formation strategy adapter;
- BMP structural validator before response;
- request budget/resource guard;
- rate limiting by verified hotkey;
- structured logs/metrics;
- health/readiness endpoints;
- graceful shutdown.

Miner algorithm internals are deliberately open competition.

---

## 4. Consumer integration production surface

Reference external API/SDK responsibilities:

### Episode ingest
Accept execution traces in a normalized schema without requiring Consequent to own the originating agent runtime.

### Formation request
A consumer may ask the network/runtime adapter to obtain one or more candidate/evaluated BMPs from prior episodes.

### BMP registry
Stores accepted patches and lifecycle metadata.

### Retrieval
Runtime-side scope/trigger matching plus bounded ranking.

### Application hook
Injects selected declarative BMP guidance without changing executor capabilities.

### Influence logging
Records which BMPs were available/applied and resulting outcomes when possible.

Consequent should support consumers without making them run a validator.

---

## 5. Availability and failure policy

### Miner timeout
- score current challenge as unavailable/zero contribution;
- do not block evaluation batch;
- track repeated downtime separately from harmful output.

### Validator evaluator failure
- mark sample invalid rather than silently zeroing miner;
- retry under bounded policy;
- preserve evaluator error evidence.

### Chain unavailable
- retain computed score snapshot;
- do not claim weight publication;
- retry only under chain/rate-limit policy;
- avoid recomputing with different challenge data solely because settlement was delayed.

### Evidence store unavailable
- fail weight publication closed if required evidence cannot be durably recorded;
- mechanism should prefer delayed settlement over unauditable settlement.

### Consumer store unavailable
Does not affect validator consensus; consumer runtime decides fallback behavior.

---

## 6. Security policies

- network/testnet/live miner mode requires authentication;
- signed identity and authorization are separate checks;
- active holdout seeds never sent to miners;
- raw request body/path preserved for btauth verification;
- replay cache bounded and persistent enough for deployment topology;
- no wallet secrets in logs or evidence artifacts;
- validator challenge evidence separates public commitment from private holdout material;
- BMP payload is declarative-only;
- runtime cannot auto-install tools/modules from BMP content;
- external consumer namespaces are isolated.

---

## 7. Data retention

### Public/replayable
- protocol/evaluator versions;
- retired fixtures;
- score methodology;
- chain weight transactions;
- sanitized evaluation evidence;
- challenge commitments.

### Private while active
- current holdout seeds;
- exact hidden task composition;
- anti-gaming sampling policy details that enable benchmark extraction;
- wallet secrets.

### Consumer-private
- raw execution episodes unless explicitly submitted;
- tenant BMP registry;
- influence records tied to private workloads.

---

## 8. Observability

Validator metrics:
- miners discovered/served;
- request success/error classes;
- p50/p95 latency;
- admission rejection reasons;
- evaluation cost per miner/family;
- uplift distribution;
- regression/policy violation rates;
- uncertainty/sample count;
- weight submission delay;
- chain rate-limit remaining;
- commit/reveal state;
- score dispersion across validators where available.

Miner metrics:
- authenticated request count;
- unauthorized/replay/stale failures;
- formation latency;
- BMP size/rule count;
- strategy failures;
- resource utilization.

Evidence metrics:
- batches without complete evidence should be zero;
- digest mismatch should page/fail closed.

---

## 9. Deployment stages

```text
M0  one-miner strict chain-local economic loop        CLOSED
M1  six chain-registered miners + competitive weight NEXT
M2  adversarial mechanism pressure                   PENDING
M3  external consumer integration                    PENDING
T1  funded Bittensor test deployment                 PENDING
T2  multi-validator testnet                          PENDING
P0  production candidate                             PENDING
```

Production promotion requires both protocol correctness and evidence quality; deployment alone is not sufficient.

---

## 10. Production release gates

Before public testnet mutation:
- M1 six-chain-miner competitive loop passes;
- no unresolved critical adversarial findings;
- BMP lifecycle schema includes expiry/supersession/revocation;
- structural admission rejects capability payloads;
- validator live hyperparameter handling tested;
- evidence ledger is complete;
- cold-clone setup works.

Before production candidate:
- repeated testnet rounds;
- multiple validators or credible independent evaluation;
- commit-reveal behavior proven rather than disabled;
- validator cost envelope measured;
- challenge leakage pressure-tested;
- consumer integration demonstrated;
- restart/recovery and state continuity tested;
- monitoring/runbooks exist;
- security review complete.

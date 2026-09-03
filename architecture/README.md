# Consequent Reference Architecture

This directory is the canonical system-design layer for Consequent.

The architecture exists to preserve one mechanism invariant:

> Consequent rewards memory formation only when a bounded, provenance-linked Behavioral Memory Patch causes better unseen future execution.

The architecture must not drift toward rewarding storage, retrieval, fluent text generation or capability expansion.

---

## 1. System layers

```text
┌─────────────────────────────────────────────────────────────┐
│  Consumer / Agent Runtime                                  │
│  executes work, emits episodes, retrieves/applies BMPs     │
└──────────────────────────┬──────────────────────────────────┘
                           │ execution episodes / objectives
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Consequent Formation Plane                                │
│  validator creates challenge → miners propose BMPs         │
└──────────────────────────┬──────────────────────────────────┘
                           │ candidate BMPs
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Consequent Evaluation Plane                               │
│  admission → concealed A0/A1 → utility → vetoes → scores  │
└──────────────────────────┬──────────────────────────────────┘
                           │ UID score vector
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Bittensor Chain Plane                                     │
│  registration · ServeAxon · metagraph · SetWeights         │
└──────────────────────────┬──────────────────────────────────┘
                           │ economic selection signal
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Memory Integration Plane                                  │
│  accepted BMP store · index · retrieve · apply · retire    │
└──────────────────────────┬──────────────────────────────────┘
                           │ influence evidence
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Evidence Plane                                             │
│  provenance · digests · eval records · chain references    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Responsibility boundary

### Bittensor subnet owns
- miner competition;
- formation request protocol;
- BMP admission rules;
- concealed evaluation;
- score construction;
- validator weight output;
- network identity and discovery.

### Consumer/runtime owns
- raw execution lifecycle;
- episode capture;
- durable BMP storage;
- task-time retrieval;
- applying selected BMPs to the executor;
- local policy deciding whether an accepted BMP is eligible for use.

Consequent may ship reference implementations for runtime storage/retrieval, but these are not rewarded commodities unless the mechanism is explicitly revised.

---

## 3. Core protocol objects

### ExecutionEpisode
A source event or trajectory fragment from which a miner may learn.

Minimum semantic fields:
- episode ID;
- task family;
- observable state/actions/outcome;
- timestamp/version context;
- provenance identity.

### MemoryFormationRequest
Validator challenge containing:
- challenge ID;
- source episodes;
- objective;
- constraints;
- memory budget;
- evaluator version;
- optional task-family scope.

The request must not disclose concealed holdouts or expected answers.

### BehavioralMemoryPatch
A bounded declarative behavioral delta.

Production target shape:

```json
{
  "patch_id": "bmp_...",
  "patch_version": "bmp/0.2",
  "scope": {
    "task_family": "api_protocol",
    "environment": "optional namespace"
  },
  "triggers": [
    {"when": {"retrying_non_idempotent_operation": true}}
  ],
  "guidance": [
    {"action": "reuse_original_idempotency_key"}
  ],
  "avoid": [
    {"action": "generate_new_key_per_retry"}
  ],
  "source_evidence": ["episode:18:event:7"],
  "confidence": 0.93,
  "status": "candidate",
  "created_at": "...",
  "expires_at": null,
  "supersedes": [],
  "revocation": null
}
```

BMPs are declarative. They may select, constrain or prioritize existing behavior; they may not add hidden tools, executable modules or new capabilities.

### EvaluationRecord
Binds:
- challenge;
- miner identity;
- patch digest;
- evaluator version;
- concealed holdout commitment;
- A0 result;
- A1 result;
- utility delta;
- regressions;
- policy violations;
- final score;
- chain context.

### MemoryRecord
Runtime-side persisted form of an accepted BMP plus lifecycle metadata.

---

## 4. Trust boundaries

### Miner is untrusted
Assume miners may:
- fabricate provenance;
- overfit source instances;
- inject executable behavior;
- return malformed payloads;
- coordinate with other miners;
- target benchmark leakage.

Therefore validator admission/evaluation never trusts BMP claims.

### Validator is economically trusted but adversarially audited
Assume validators may:
- leak challenges;
- copy evaluation outcomes;
- use biased/private task distributions;
- collude with miners;
- misreport evidence.

Mitigations include independent validators, challenge commitments, replayable retired fixtures, cross-validator dispersion and observable chain weights.

### Runtime is outside consensus
The consumer decides which validated BMPs to store and apply. A subnet score is evidence of evaluated utility, not authority to mutate an agent automatically.

---

## 5. Causal treatment invariant

For canonical validator evaluation:

```text
Capabilities(A0) == Capabilities(A1)
Task(A0)         == Task(A1)
Environment(A0)  == Environment(A1)
Objective(A0)    == Objective(A1)
Treatment difference == BMP presence
```

Breaking this invariant invalidates causal attribution.

---

## 6. Network path

```text
registered miner hotkey
→ miner HTTP service
→ bt.ServeAxon publishes endpoint
→ validator reads metagraph
→ validator selects registered served miner
→ btauth/1 signed challenge
→ miner verifies sender/receiver/freshness/replay
→ caller policy authorizes validator
→ miner returns BMP
→ validator admits + evaluates
→ score mapped to UID
→ SetWeights under live subnet constraints
→ weight accepted/read back from chain
```

M0 has proven this path for one registered miner through economic read-back on a fresh local Subtensor chain.

---

## 7. Production services

Expected production decomposition:

### Miner node
- HTTP API;
- btauth verification;
- caller authorization;
- strategy/model adapter;
- BMP constructor;
- telemetry.

### Validator node
- metagraph watcher;
- challenge generator;
- signed HTTP client;
- admission engine;
- evaluator workers;
- rolling score state;
- weight scheduler;
- evidence writer.

### Consumer integration service / SDK
- episode ingestion;
- BMP registry/store;
- retrieval/index adapter;
- runtime application hook;
- influence reporting;
- revoke/supersede/expiry processing.

### Evidence store
Append-oriented records with deterministic digests. Raw active holdouts remain private; commitments and retired fixtures can later be disclosed for audit.

---

## 8. Architecture documents

- `MEMORY_LIFECYCLE.md` — formation, acceptance, storage, retrieval, application and retirement.
- `PRODUCTION.md` — deployment topology, reliability and operational policies.
- `../docs/PROTOCOL.md` — wire/protocol-level semantics.
- `../GROUND_TRUTH.md` — external and mechanism truth.
- `../audits.md` — live release gate.
- `../skills/README.md` — operating foundries used to change this architecture safely.

When a major architecture decision changes the rewarded commodity, causal treatment, validator truth model or Bittensor settlement path, update `GROUND_TRUTH.md`/the category boundary before implementation.

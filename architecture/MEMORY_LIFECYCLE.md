# Consequent Memory Lifecycle

This document defines how a Behavioral Memory Patch moves from execution experience into durable runtime influence.

The subnet rewards **formation quality**. Storage and retrieval are integration concerns unless a future mechanism revision explicitly changes that boundary.

---

## 1. Lifecycle state machine

```text
SOURCE_EPISODES
    ↓
FORMATION_CHALLENGE
    ↓
CANDIDATE_BMP
    ↓ structural admission
ADMITTED_BMP
    ↓ concealed causal evaluation
EVALUATED_BMP
    ├─ reject
    └─ accept
         ↓
ACCEPTED_BMP
    ↓ runtime persistence
STORED_BMP
    ↓ contextual selection
RETRIEVED_BMP
    ↓ bounded injection/application
APPLIED_BMP
    ↓ observed future execution
INFLUENCE_RECORD
    ├─ reinforce
    ├─ supersede
    ├─ expire
    └─ revoke
```

A BMP can be accepted economically but never used by a particular consumer. Economic score is not mandatory runtime authority.

---

## 2. Formation

Input:
- source execution episodes;
- objective;
- task-family scope;
- policy constraints;
- memory budget.

Miner output:
- bounded declarative BMP;
- source provenance references;
- confidence/metadata;
- no executable capability payload.

Formation should answer:

> What should survive this experience because it is likely to alter future execution beneficially?

It should not answer:

> What entire transcript should be remembered?

---

## 3. Admission

Validator structural checks run before expensive causal evaluation.

Required checks:
- challenge ID binding;
- schema/version validity;
- serialized size/rule budget;
- provenance IDs exist in supplied source episodes;
- allowed task family/actions;
- no code/binary/tool/module payload;
- no hidden capability expansion;
- deadline/freshness;
- digest/deduplication;
- explicit status metadata.

Admission failure earns zero and is not evaluated further.

---

## 4. Evaluation

An admitted BMP is a proposed treatment.

```text
A0: executor without BMP
A1: identical executor with BMP
```

The validator holds task, environment, objective, capabilities, timeout and seed constant wherever possible.

Acceptance signal is not simply `ΔU > 0` on one sample. It must incorporate:
- mean/robust uplift;
- uncertainty;
- regressions;
- policy violations;
- family coverage/generalization;
- cost/efficiency where relevant.

Hard policy violations can make a BMP economically ineligible even when mean uplift is positive.

---

## 5. Storage

Reference runtime storage model:

```text
MemoryRecord {
  patch_id,
  patch_version,
  patch_digest,
  bmp,
  source_provenance,
  formation_miner,
  validator/evaluation references,
  score/rank metadata,
  scope,
  created_at,
  valid_from,
  expires_at,
  supersedes[],
  superseded_by[],
  revoked_at,
  revocation_reason,
  status
}
```

Recommended properties:
- append-oriented history;
- content-addressed patch digest;
- immutable source/evaluation references;
- mutable lifecycle status only through explicit events;
- consumer namespace/tenant isolation;
- no active holdout data stored with the BMP.

Storage backend is deliberately replaceable: SQLite, Postgres, document store or specialized memory infrastructure can all satisfy the contract.

---

## 6. Indexing and retrieval

Retrieval is context-driven and bounded.

Input context may include:
- current task family;
- environment/tool namespace;
- operation/action type;
- current policy state;
- semantic/task features;
- recency/version constraints.

Reference selection pipeline:

```text
current task
→ hard scope filter
→ lifecycle filter (active / non-expired / non-revoked)
→ trigger match
→ relevance ranking
→ evidence/quality prior
→ diversity/conflict resolution
→ memory-budget truncation
→ selected BMP set
```

Important: retrieval quality is not the current subnet reward target. A consumer may choose a sophisticated retrieval engine without changing Consequent's miner incentive.

---

## 7. Application

BMP application must preserve capability equality.

Allowed:
- add declarative guidance to context;
- constrain choices among already available actions;
- prioritize or avoid existing behaviors;
- set reminders/checklists/policies;
- select among existing tools.

Not allowed as BMP application:
- load a new executable module;
- grant a new tool permission;
- fetch a hidden model endpoint unavailable to A0;
- mutate authority/capabilities only in A1;
- inject opaque code.

Reference runtime injection:

```text
base system/runtime context
+ current task
+ selected active BMP guidance
→ fixed executor
```

The runtime should log which patch IDs were made available and which were actually consulted/applied when that signal can be observed.

---

## 8. Influence records

A runtime can optionally report post-deployment evidence:

```text
InfluenceRecord {
  execution_id,
  patch_ids_available[],
  patch_ids_applied[],
  task_family,
  outcome,
  utility_proxy,
  regressions,
  policy_events,
  timestamp,
  runtime_version
}
```

These records can support future re-evaluation and reputation, but should not automatically become validator ground truth without anti-manipulation controls.

---

## 9. Conflict resolution

Two BMPs may conflict.

Resolution order should be explicit, for example:
1. policy/safety constraints;
2. revocation status;
3. exact scope specificity;
4. newer superseding patch;
5. higher validated quality/evidence;
6. confidence;
7. stable deterministic tie-break.

Do not concatenate contradictory instructions and hope the executor resolves them.

---

## 10. Supersession, expiry and revocation

### Supersede
Use when a newer BMP replaces an older lesson within the same scope.

### Expire
Use when validity is time/version bounded, e.g. an API behavior or dependency version changed.

### Revoke
Use when a patch is discovered to be harmful, compromised, based on invalid provenance or no longer policy-compatible.

Lifecycle events should be retained; old BMP content should not silently disappear.

---

## 11. Formation vs retrieval boundary

A useful diagnostic:

- **Formation problem:** Which behavioral lesson should be created from these episodes?
- **Retrieval problem:** Which already-created lessons are relevant to this new task?

Consequent's subnet mechanism currently solves the first problem competitively.

If the system starts rewarding which patch was retrieved rather than which patch was formed, that is a mechanism change and must go through the category/ground-truth process.

---

## 12. Production acceptance checklist

Before a BMP is eligible for runtime use:
- provenance resolves;
- schema supported;
- no capability payload;
- active/non-revoked;
- within validity window;
- compatible with runtime/evaluator version as required;
- scope matches;
- conflict policy resolves cleanly;
- consumer policy permits it.

Before a BMP is promoted as "useful":
- causal evaluation evidence exists;
- regressions and policy events were checked;
- evidence label accurately reflects environment (`LOCAL`, `CHAIN_LOCAL`, `TESTNET`, etc.).

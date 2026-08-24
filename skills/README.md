# Consequent Foundries

These are reusable reasoning/build skills for developing Consequent and future Bittensor subnets.

They are not documentation categories. Each foundry is an operating discipline with an input, a procedure, a required output, and a stop condition.

Canonical order:

```text
SUBNET FOUNDRY
  ↓
ARCHITECTURE FOUNDRY
  ↓
MEMORY LIFECYCLE FOUNDRY
  ↓
EVALUATION FOUNDRY
  ↓
ADVERSARY FOUNDRY
  ↓
EVIDENCE FOUNDRY
```

The loop is iterative. Evidence or adversarial failure may send the system back to any earlier foundry.

---

## 1. Subnet Foundry

Purpose: determine whether an idea deserves to be a Bittensor subnet and define the economic primitive correctly.

Input:
- problem/use case;
- proposed digital commodity;
- candidate miner behavior;
- candidate validator behavior;
- expected demand side.

Procedure:
1. name the scarce resource;
2. state why decentralised competition improves it;
3. define miner output precisely;
4. define validator truth source;
5. define what gets rewarded;
6. identify how miners can game the reward;
7. define how weights map to economic consequence;
8. state who consumes the resulting commodity;
9. compare against a non-subnet architecture;
10. reject the subnet if Bittensor is not necessary.

Required output:
- commodity definition;
- miner contract;
- validator contract;
- scoring function;
- incentive hypothesis;
- demand-side consumer;
- falsification conditions.

Consequent application:
- commodity: Behavioral Memory Patch;
- scarce resource: useful memory formation;
- settlement criterion: generalized causal behavioral uplift.

Stop condition:
Do not build until `MECHANISM_NECESSITY` and `CANONICAL_SCORE` are defensible.

---

## 2. Architecture Foundry

Purpose: turn mechanism truth into a system that preserves the mechanism under implementation pressure.

Input:
- frozen commodity;
- miner/validator contracts;
- Bittensor protocol constraints;
- security/evidence requirements.

Procedure:
1. draw system boundaries;
2. separate chain plane, data plane, evaluation plane, memory plane and evidence plane;
3. define canonical protocol objects;
4. define ownership of state;
5. define trust boundaries;
6. define lifecycle transitions;
7. state invariants beside every transition;
8. define failure/recovery paths;
9. define production observability;
10. map every architectural component to a mechanism requirement.

Required output:
- system context;
- container/service topology;
- trust-boundary map;
- state model;
- protocol sequence;
- deployment topology;
- architecture decision records when choices are contested.

Stop condition:
No implementation component may exist without a named architectural responsibility.

---

## 3. Memory Lifecycle Foundry

Purpose: design BMP formation, validation, storage, retrieval, application, supersession and retirement without drifting into generic memory infrastructure.

Lifecycle:

```text
execution episodes
→ formation challenge
→ candidate BMP
→ structural admission
→ causal evaluation
→ accepted BMP
→ storage/indexing
→ context retrieval
→ bounded application
→ observed influence
→ reinforce / supersede / expire / revoke
```

Questions for every lifecycle stage:
- who owns the state?
- what is immutable?
- what is versioned?
- what can be revoked?
- what provenance is required?
- what causes transition to the next state?
- what evidence proves the transition?

Hard boundary:
Storage and retrieval are runtime/integration responsibilities unless the subnet explicitly chooses to make them a rewarded commodity. Consequent currently rewards memory formation quality, not storage or retrieval quality.

Stop condition:
A BMP may not be production-eligible unless its source provenance, scope, application contract, status and evaluation state are explicit.

---

## 4. Evaluation Foundry

Purpose: design validator truth so TAO emissions select better memory-formation algorithms instead of benchmark gaming.

Canonical experiment:

```text
A0 = fixed executor + task + environment + no BMP
A1 = same executor + same task + same environment + BMP
ΔU = U(A1) - U(A0)
```

Invariant:

`Capabilities(A0) == Capabilities(A1)`

Procedure:
1. define utility per task family;
2. define policy/safety vetoes;
3. conceal future evaluation distribution;
4. hold non-treatment variables constant;
5. estimate uncertainty;
6. test regressions, not just positive uplift;
7. aggregate per family;
8. apply conservative score transforms;
9. normalize non-negative weights;
10. replay retired seeds to audit validator integrity.

Required output:
- task generator;
- source/holdout separation;
- paired evaluator;
- score decomposition;
- veto rules;
- variance/uncertainty policy;
- evidence record.

Stop condition:
No reward if retrieval, fluency or judge preference is being mistaken for beneficial influence.

---

## 5. Adversary Foundry

Purpose: try to make the subnet reward the wrong thing, leak evaluator truth, lose economic integrity or fail operationally.

Attack surfaces:
- commodity gaming;
- benchmark leakage;
- source-instance memorization;
- capability smuggling;
- malformed/oversized BMPs;
- provenance forgery;
- replay/freshness abuse;
- miner copying;
- miner-validator collusion;
- validator copying/collusion;
- score manipulation;
- catastrophic regression hidden by mean uplift;
- policy violation compensated by positive reward;
- endpoint/stake/identity spoofing;
- chain-rate-limit mistakes;
- availability/downtime gaming;
- evaluator-version drift;
- Sybil/economic concentration;
- external consumer abuse.

For every attack, produce:
1. attacker objective;
2. preconditions;
3. cheapest attack path;
4. expected profit/benefit;
5. detection signal;
6. protocol mitigation;
7. residual risk;
8. pressure test;
9. evidence required to close the finding.

Severity classes:
- CRITICAL: breaks rewarded commodity or economic integrity;
- HIGH: sustained profitable gaming or validator truth failure;
- MEDIUM: bounded degradation/availability issue;
- LOW: nuisance/operational weakness.

Stop condition:
A release cannot advance with unresolved CRITICAL findings or unbounded HIGH findings.

---

## 6. Evidence Foundry

Purpose: ensure every claim has the strongest evidence class actually earned.

Evidence ladder:

```text
UNVERIFIED
→ SIMULATED_PASS
→ LOCAL_PASS
→ CI_PASS
→ LOCAL_NETWORK_COMPONENT_PASS
→ CHAIN_LOCAL_PASS
→ TESTNET_PASS
→ PUBLIC_EVALUATOR_PASS
→ PRODUCTION_PASS
```

Procedure:
1. write the claim;
2. name the required evidence class;
3. define the exact experiment;
4. capture inputs/versions/seeds;
5. capture raw output;
6. capture chain references where applicable;
7. record failure as evidence too;
8. prevent lower-class evidence from satisfying higher-class claims;
9. regenerate evidence when architecture/evaluator versions change.

Required evidence record for validator batches:
- validator hotkey;
- miner UID/hotkey;
- challenge ID;
- generator/evaluator version;
- source digest;
- BMP digest;
- holdout commitment;
- A0/A1 outcomes;
- uplift/regressions/policy violations;
- final score;
- resulting weight;
- timestamp/block context;
- chain transaction reference when submitted.

Stop condition:
No submission or production claim may use an evidence label stronger than the captured artifact proves.

---

## Daily practice mode

A useful training loop is one foundry problem per day:

- Monday — reverse-engineer a live subnet with Subnet Foundry;
- Tuesday — redraw one architecture boundary;
- Wednesday — design one memory-lifecycle edge case;
- Thursday — build one evaluator experiment;
- Friday — attack one mechanism assumption;
- Saturday — reconcile claims with evidence;
- Sunday — write a one-page design review from memory.

Consequent should be the default worked example, but not the only one. The objective is to become capable of designing, attacking and proving arbitrary subnet mechanisms rather than merely operating the SDK.

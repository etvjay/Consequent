# Consequent — Ground Truth

Status: `CANONICAL_BUILD_BASELINE`
Frozen from: 2026-08-24
Scope: Bittensor Global Subnet Hackathon + current Bittensor v11 implementation truth
Repository: `etvjay/Consequent`

This file is the highest-authority internal build document for Consequent. It exists to prevent implementation drift, legacy-Bittensor assumptions, hackathon-rule invention, and evidence inflation.

If code, README copy, an issue, a PR, a demo claim, or an internal plan conflicts with this file, this file wins unless it is explicitly revised with a new source check.

---

## 1. Authority order

Consequent uses the following authority hierarchy:

1. Current published Bittensor Global Subnet Hackathon page and host-issued updates.
2. Current official Bittensor documentation for the installed major SDK/runtime.
3. Live Bittensor chain state and subnet hyperparameters when we deploy.
4. Reproducible repository evidence: CI, local integration runs, chain receipts, testnet logs.
5. This `GROUND_TRUTH.md`.
6. `audits.md` and other evaluation/build-control documents.
7. Architecture notes, issue text, comments, previous plans, historical templates, prior Bittensor examples.

No old hackathon round, archived subnet template, previous Bittensor SDK behavior, or example project may silently override current published truth.

---

## 2. Hackathon ground truth

Source of record:
- https://www.hackquest.io/hackathons/Bittensor-Global-Subnet-Hackathon

Verified 2026-08-24.

### Program objective

The hackathon asks teams to take a subnet idea from concept and mechanism design to a working Bittensor testnet implementation that demonstrates:

- what digital commodity or useful work the subnet produces;
- what miners do;
- what validators measure;
- how contributions are scored;
- why incentives reward the desired behavior;
- how miner-validator interaction works;
- evidence that the mechanism behaves as intended.

Functional correctness and conceptual integrity matter more than polish.

### Checkpoints

Hackathon duration published on the page: Aug. 22 – Oct. 19, 2026.

Checkpoint #1 — Sep. 20, 2026: Subnet Proposal.
The proposal must cover:

- problem and use case;
- subnet architecture;
- miner responsibilities and tasks;
- validator responsibilities and evaluation;
- incentive and reward mechanism;
- scoring methodology;
- expected users and ecosystem value;
- roadmap toward testnet and future deployment.

Final — Oct. 19, 2026:

- updated proposal;
- public GitHub repository;
- testnet implementation;
- short demo video;
- final pitch.

### Public repository requirements

The public repository should contain:

- subnet code;
- miner code;
- validator code;
- setup instructions;
- technical documentation;
- testnet deployment instructions.

### Judging criteria

Published judging dimensions:

1. Mechanism & Incentive Design
2. Technical Implementation
3. Miner-Validator Architecture
4. Evaluation & Scoring Quality
5. Problem & Market Relevance
6. Bittensor Ecosystem Value
7. Scalability & Long-Term Potential

### Things that are NOT published hard requirements

The following must not be represented as mandatory unless the organizers later publish them as such:

- a specific starter repository or builder kit;
- use of the archived `bittensor-subnet-template`;
- a specific framework such as FastAPI;
- exactly 3 validators;
- exactly 10 miners;
- a polished frontend;
- a specific model provider;
- a specific miner implementation algorithm.

The hackathon cites Proven's 3-validator / 10-miner deployment as an example of a strong implementation, not as a universal requirement.

---

## 3. Current Bittensor builder ground truth

Primary sources:

- Migration: https://www.bittensor.com/docs/migration
- Signed requests: https://www.bittensor.com/docs/guides/signed-requests
- Validating: https://preview.bittensor.com/docs/guides/validating

Verified 2026-08-24.

### Installed major version

Consequent currently targets Bittensor v11 and CI has successfully installed `bittensor==11.1.0`.

This repo must not import architecture assumptions from v9/v10 without an explicit compatibility reason.

### v11 networking truth

Bittensor v11 removed the old SDK networking objects:

- `bt.Axon`
- `bt.Dendrite`
- `bt.Synapse`
- `bt.StreamingSynapse`

Consequent therefore owns its application data plane:

- its own HTTP server;
- its own HTTP client;
- its own request/response models;
- its own fan-out and timeout behavior;
- its own rate limiting;
- its own service lifecycle.

Bittensor still supplies network identity and authentication through hotkeys.

### Signed request truth

Validator → miner requests use `btauth/1` via:

- `bt.http_auth.sign(...)`
- `bt.http_auth.verify(...)`

The signature binds the request method, exact request target, body hash, nonce, sender hotkey, and receiver hotkey.

Consequent network mode must fail closed on invalid/missing authentication.

Authentication answers "which hotkey sent this request?" It does not by itself answer "is this hotkey an authorized validator for this subnet?"

Consequent must therefore apply metagraph caller policy after signature verification.

Minimum production/testnet caller checks should include:

- sender is registered on the relevant netuid;
- sender identity resolves from current metagraph state;
- validator permit policy is enforced where appropriate;
- stake threshold/rate-limit policy is explicit rather than accidental.

### Chain-side endpoint publication remains required

The disappearance of `bt.Axon` does NOT remove endpoint publication.

A miner must publish the endpoint validators should use through the chain-side `ServeAxon` intent:

`bt.ServeAxon(netuid=..., ip=..., port=...)`

TLS may use `bt.ServeAxonTls` where required.

A real Consequent validator should discover miner UIDs, hotkeys and published endpoints from current metagraph/chain state rather than relying on a manually supplied endpoint list in canonical operation.

### Registration remains required

A real miner or validator must be a registered neuron on the target subnet/netuid before the chain can treat it as a subnet participant.

Registration, wallet/hotkey creation, funding, neuron UID state and validator permits are chain evidence, not application assumptions.

### Validator weight truth

The canonical v11 weight operation is `bt.SetWeights` or the higher-level `bt.set_weights` flow.

Weights may be supplied as a UID→weight mapping. The SDK handles canonical normalization/clipping/quantization/submission behavior, but Consequent must still respect live subnet state, including relevant constraints such as:

- registration state;
- validator permit;
- weight rate limits;
- minimum allowed weight count;
- maximum weight limits;
- required version key, if any;
- commit-reveal mode where enabled.

We must query or derive these from the actual subnet/testnet configuration when live.

A Python dictionary that sums to 1 is not testnet weight evidence.

### Dry-run / test discipline

Before live mutation, prefer plan/dry-run paths when available and test against local/test networks before mainnet.

### Hyperparameter read shape

The official `get_subnet_hyperparams_v3` runtime read is forward-compatible,
but its returned field set is runtime/version-dependent. Current localnet
responses expose the consensus fields needed by Consequent while omitting
`bonds_penalty`, even though that parameter exists in the broader
hyperparameter model. Consequent must preserve an omitted optional field as
unknown and must not invent a default that could be mistaken for chain
evidence. A fresh chain run is required before treating the resulting
consensus-policy record as complete.

---

## 4. Consequent product ground truth

### One-line protocol definition

Consequent is a Bittensor subnet where miners compete to form bounded, provenance-linked behavioral memory patches from prior execution experience, and validators reward those patches according to their causal effect on concealed future execution.

### Canonical category distinction

**STORED ≠ RECALLED ≠ INFLUENTIAL ≠ BENEFICIAL**

Consequent is not primarily a storage network, retrieval system, context database, generic agent-memory product, generic capability market, or generic agent benchmark.

The economic commodity is memory formation that causes beneficial future behavior.

### Digital commodity

The miner output is a **Behavioral Memory Patch (BMP)**.

A BMP must:

1. derive from identifiable prior execution experience;
2. carry source provenance;
3. remain within validator-provided memory bounds;
4. remain declarative and not smuggle a new executable capability;
5. be consumable after the miner is offline;
6. be testable in paired future execution;
7. support invalidation, expiry, or supersession semantics as the protocol matures.

### Miner responsibility

Given:

- prior execution episodes;
- objective;
- constraints;
- memory budget;
- challenge identifier;

A miner returns one or more candidate BMPs.

The protocol does not prescribe the miner's learning algorithm. Reflection, causal attribution, trajectory analysis, symbolic induction, learned models, LLMs and hybrids may all compete so long as the returned artifact obeys the protocol.

### Validator responsibility

A validator must:

1. generate or select source execution experience;
2. construct a challenge without leaking concealed future holdouts;
3. query miners;
4. structurally validate the BMP;
5. run paired evaluation with the same executor/capabilities/environment controls;
6. compare no-memory vs memory-conditioned execution;
7. measure uplift, regression, policy violations, cost and uncertainty;
8. aggregate results into miner scores;
9. transform scores into chain-conformant UID weights;
10. submit weights when permitted;
11. preserve enough evidence to replay or audit the score.

### Counterfactual invariant

The canonical evaluation is:

`U0 = utility(A, T, no_patch)`

`U1 = utility(A, T, patch)`

`ΔU = U1 - U0`

The executor capabilities must remain fixed between conditions:

`Capabilities(A0) == Capabilities(A1)`

Only the memory condition should differ.

### Reward truth

A patch is not rewarded merely because it:

- was stored;
- was retrieved;
- looks plausible;
- is semantically similar to a successful answer;
- is preferred by a judge model;
- compresses history;
- contains more detail.

It is rewarded for generalized beneficial influence on concealed future execution.

Policy violations and catastrophic regressions must remain hard-veto or strongly non-compensable conditions.

### Anti-skill boundary

If a miner adds a new executable tool, binary, model endpoint, implementation module or otherwise expands the executor's capabilities, that artifact is not a BMP for the canonical Consequent mechanism.

Consequent may later interface with capability markets, but it must not silently become one.

---

## 5. Current repository evidence truth

As of this freeze:

### Proven

- Public repository exists: `etvjay/Consequent`.
- `bootstrap/m0` contains the current implementation work.
- CI installs the Consequent package with Bittensor 11.1.0 on Python 3.10 and 3.12.
- CI test suite passes on both lanes.
- BMP/request-response models exist.
- Deterministic adversarial miner strategies exist.
- Local causal scoring and policy-veto logic exists.
- Validator HTTP query skeleton exists.
- `btauth/1` signing and verification hooks exist.
- `bt.SetWeights` intent path exists.
- Golden local mechanism simulation previously passed its defined adversarial ranking checks.

### Not yet proven

- real wallet/hotkey configuration in this repo flow;
- neuron registration on a Consequent testnet netuid;
- `ServeAxon` endpoint publication;
- metagraph-driven miner discovery;
- metagraph-driven validator caller authorization;
- a real authenticated validator→miner network round trip;
- six independently running miner services;
- networked concealed evaluation across those miners;
- live hyperparameter-conformant weight setting;
- validator permit on the target subnet;
- successful weight extrinsic on Bittensor testnet;
- 3-validator / 10-miner topology;
- testnet demo;
- final hackathon submission.

No statement in the README, pitch or demo may imply these are complete until evidence exists.

---

## 6. Evidence classes

Use these evidence states consistently:

- `UNVERIFIED` — asserted but not tested.
- `SIMULATED_PASS` — synthetic/simulation result only.
- `LOCAL_PASS` — real code passed locally but not networked/live.
- `CI_PASS` — reproducible CI execution passed.
- `LOCAL_NETWORK_PASS` — independently running local services communicated successfully.
- `CHAIN_DRY_RUN_PASS` — live SDK/chain planning/preflight succeeded without mutation.
- `TESTNET_PASS` — required behavior executed on Bittensor testnet.
- `PUBLIC_EVALUATOR_PASS` — externally replayable/public evaluation passed.
- `PRODUCTION_PASS` — mainnet/production operation passed.
- `FAILED` — attempted and failed.
- `BLOCKED` — cannot currently execute due to an external prerequisite.

A lower state never satisfies a higher state.

CI is not testnet.
A signed local request is not neuron registration.
A normalized weight vector is not a successful weight extrinsic.
A transaction receipt is not proof that the economic mechanism works.

---

## 7. Build-from-here rule

All new implementation work should assume we are starting from the state recorded above, not from historical plans.

The next canonical implementation sequence is:

1. wallet/hotkey configuration and safe local/test fixtures;
2. chain abstraction for netuid/metagraph queries;
3. miner endpoint publication via `ServeAxon`;
4. metagraph-based miner discovery;
5. fail-closed signed HTTP authentication;
6. metagraph caller authorization;
7. real signed validator→miner round trip;
8. six independent miner services;
9. networked concealed evaluation;
10. live subnet hyperparameter inspection;
11. chain-conformant weight construction and dry-run;
12. Bittensor testnet registration/deployment;
13. successful testnet scoring and weight submission;
14. evidence capture and replay;
15. checkpoint/final documentation and demo.

Do not build the frontend before this core path produces live evidence unless the frontend is required to inspect/debug the mechanism.

---

## 8. Change-control rule

This file may be revised only when one of the following occurs:

- HackQuest publishes or changes a requirement;
- Bittensor changes the relevant SDK/runtime/API;
- live chain behavior contradicts documentation;
- Consequent explicitly revises its economic commodity or evaluation mechanism;
- a previously unknown requirement becomes externally verified.

Every revision should record:

- date;
- changed truth;
- source;
- implementation consequences.

Do not silently rewrite history to make an old assumption look correct.

---

## 9. Source register

Verified 2026-08-24:

1. HackQuest — Bittensor Global Subnet Hackathon
   https://www.hackquest.io/hackathons/Bittensor-Global-Subnet-Hackathon

2. Bittensor — Migrating from v9/v10
   https://www.bittensor.com/docs/migration

3. Bittensor — Signed requests
   https://www.bittensor.com/docs/guides/signed-requests

4. Bittensor — Validating
   https://preview.bittensor.com/docs/guides/validating

5. Bittensor — Subnet/neuron chain operations
   https://www.bittensor.com/docs/guides/evm/subnet-and-neuron

6. Bittensor — Metagraph chain state
   https://www.bittensor.com/docs/guides/evm/read-chain-state

---

## 10. Canonical sentence

**Consequent is not complete when a miner returns a memory patch. Consequent is complete only when registered Bittensor participants can form, evaluate and economically weight behavioral memory on the network, with evidence that the rewarded memory causes better concealed future execution.**

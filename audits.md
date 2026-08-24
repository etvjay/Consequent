# Consequent — Build Audit

Status: `ACTIVE`
Ground truth authority: [`GROUND_TRUTH.md`](./GROUND_TRUTH.md)
Current branch: `bootstrap/m0`
Audit baseline date: 2026-08-24

This file is the live release gate for Consequent. It should be updated as implementation evidence changes.

A checkbox is not evidence. Every `PASS` must have a reproducible artifact, command result, CI run, chain read, transaction result, or testnet receipt behind it.

---

## 0. Current release state

**EBI state:** `READY_TO_BUILD`

**Current mechanism evidence:** `LOCAL_PASS + CI_PASS`

**Current Bittensor-network evidence:** `NOT_RUN`

**Current testnet evidence:** `NOT_RUN`

Consequent must not be described as a working testnet subnet yet.

---

## 1. Hard stop conditions

Any of the following blocks promotion toward testnet/submission:

- [ ] unresolved conflict with `GROUND_TRUTH.md`;
- [ ] legacy v9/v10 networking architecture reintroduced as canonical implementation;
- [ ] missing miner authentication in network mode;
- [ ] no chain-published miner endpoint;
- [ ] validator uses hard-coded miner endpoints as canonical discovery;
- [ ] no metagraph caller policy;
- [ ] scoring can reward a policy-violating patch through compensating positive uplift;
- [ ] miner artifact can expand executor capabilities without being rejected;
- [ ] testnet claims are backed only by local/CI evidence;
- [ ] weight submission ignores current subnet state or validator permission;
- [ ] concealed evaluation data is leaked to miners;
- [ ] hackathon requirements are represented from memory rather than the published source.

If any checked condition becomes true, status becomes `BLOCKED` until corrected.

---

## 2. A00 — Hackathon truth audit

**Goal:** ensure we are building what the current program asks for.

- [x] Current HackQuest event page rechecked on 2026-08-24.
- [x] Sep. 20 proposal checkpoint captured.
- [x] Oct. 19 final deliverables captured.
- [x] Judging criteria captured.
- [x] Public-repo requirements captured.
- [x] Testnet implementation requirement captured.
- [x] No unsupported mandatory starter-kit claim.
- [x] 3 validators / 10 miners classified as example/evaluator pressure, not hard requirement.
- [ ] Organizer workshop/office-hour updates rechecked when released.
- [ ] Final submission form fields captured when available.

**State:** `PASS_WITH_FUTURE_RECHECK`

Evidence: `GROUND_TRUTH.md` source register.

---

## 3. A01 — Builder stack audit

**Goal:** prove Consequent targets the actual current Bittensor stack.

- [x] Bittensor v11 migration docs rechecked.
- [x] Legacy `Axon`/`Dendrite`/`Synapse` assumptions removed from canonical architecture.
- [x] Application data plane uses own HTTP client/server.
- [x] Request/response schema is Consequent-owned.
- [x] `bt.http_auth.sign` integration exists.
- [x] `bt.http_auth.verify` integration exists.
- [x] `bt.SetWeights` integration path exists.
- [x] CI installed `bittensor==11.1.0` on Python 3.10.
- [x] CI installed `bittensor==11.1.0` on Python 3.12.
- [ ] `bt.ServeAxon` implementation exists.
- [ ] metagraph discovery implementation exists.
- [ ] live chain client abstraction exists.
- [ ] live hyperparameter read path exists.

**State:** `PARTIAL_PASS`

Blocking gap before calling this a real subnet skeleton: ServeAxon + metagraph discovery + live chain state.

---

## 4. A02 — Commodity/category audit

**Goal:** prevent drift into generic memory infrastructure or capability markets.

Canonical invariant: **STORED ≠ RECALLED ≠ INFLUENTIAL ≠ BENEFICIAL**

- [x] Digital commodity is Behavioral Memory Patch (BMP).
- [x] BMP must derive from prior execution experience.
- [x] BMP carries source provenance.
- [x] BMP is bounded by validator-provided budget.
- [x] BMP is declarative.
- [x] Capability expansion is out of scope.
- [x] Miner algorithm is open/competitive.
- [x] Retrieval alone is not rewarded.
- [x] Storage alone is not rewarded.
- [x] Semantic plausibility alone is not rewarded.
- [x] Paired future execution is central to scoring.
- [ ] BMP expiry/supersession semantics implemented.
- [ ] protocol-level executable-payload rejection hardened beyond schema assumptions.

**State:** `PASS_DESIGN / PARTIAL_IMPLEMENTATION`

---

## 5. A03 — Protocol/schema audit

**Goal:** make challenge and BMP objects bounded, replayable and safe.

- [x] Challenge ID exists.
- [x] Source episodes represented.
- [x] Task family represented.
- [x] Objective represented.
- [x] Constraints represented.
- [x] Memory budget represented.
- [x] BMP response schema exists.
- [x] Challenge-response ID binding tested.
- [ ] source provenance references validated against supplied episodes.
- [ ] byte/token budget enforced on serialized response.
- [ ] maximum patch count enforced.
- [ ] unknown/extra payload fields policy explicit.
- [ ] executable/binary content rejection test exists.
- [ ] schema version negotiation defined.
- [ ] canonical hashing/digest format defined for evidence.

**State:** `PARTIAL_PASS`

---

## 6. A04 — Miner service audit

**Goal:** prove a miner can safely expose the memory-formation commodity.

- [x] FastAPI miner service exists.
- [x] health endpoint exists.
- [x] memory-formation endpoint exists.
- [x] strategy selection exists for deterministic test miners.
- [x] raw request body is preserved for auth verification.
- [x] exact raw request target is reconstructed for verification.
- [ ] network mode fails closed if hotkey configuration is missing.
- [ ] startup validates wallet/hotkey state.
- [ ] startup validates netuid/registration where required.
- [ ] sender hotkey returned by verification is propagated to caller policy.
- [ ] rate limiting keyed by verified hotkey.
- [ ] malformed request abuse tests.
- [ ] oversized-body rejection.
- [ ] request timeout/resource bounds.
- [ ] miner endpoint can be launched as an independent process via documented command.

**State:** `PARTIAL_PASS`

Security blocker: authentication must become mandatory in network/testnet mode.

---

## 7. A05 — Bittensor identity/authentication audit

**Goal:** prove requests are hotkey-authenticated and replay resistant.

- [x] validator signing hook exists.
- [x] receiver hotkey binding is supplied.
- [x] miner verification hook exists.
- [ ] real Bittensor wallet fixture used in integration test.
- [ ] valid signed request accepted end-to-end.
- [ ] invalid signature rejected.
- [ ] modified body rejected.
- [ ] modified route rejected.
- [ ] wrong receiver rejected.
- [ ] stale/replayed nonce rejected according to SDK behavior.
- [ ] unsigned request rejected in network mode.

**State:** `NOT_PROVEN_NETWORKED`

Next hard gate.

---

## 8. A06 — Neuron registration and endpoint publication audit

**Goal:** make miners discoverable as real Bittensor neurons.

- [ ] wallet creation/configuration documented.
- [ ] hotkey creation/configuration documented.
- [ ] target testnet/netuid selection recorded.
- [ ] funding requirement recorded without embedding secrets.
- [ ] miner registration path implemented/documented.
- [ ] validator registration path implemented/documented.
- [ ] miner UID confirmed by chain read.
- [ ] `bt.ServeAxon` publication implementation exists.
- [ ] advertised IP/port validated.
- [ ] metagraph `axon` data confirms publication.
- [ ] reset/update endpoint procedure documented.

**State:** `NOT_RUN`

This gate is mandatory before claiming a real Bittensor miner.

---

## 9. A07 — Metagraph discovery and caller policy audit

**Goal:** make network participation derive from Bittensor state rather than manual configuration.

- [ ] validator reads current metagraph for target netuid.
- [ ] miner UID→hotkey mapping comes from metagraph.
- [ ] miner endpoint comes from metagraph axon data.
- [ ] unavailable/unserved miners are skipped safely.
- [ ] stale metagraph refresh policy defined.
- [ ] miner checks caller is registered.
- [ ] validator permit policy defined and enforced.
- [ ] optional minimum-stake policy explicitly configured.
- [ ] authorization denial test exists.
- [ ] policy cannot be bypassed by valid signature from unauthorized hotkey.

**State:** `NOT_RUN`

---

## 10. A08 — Multi-miner network loop audit

**Goal:** prove Consequent behaves as a competitive subnet, not a single-service API.

Target M0 pressure topology: six deterministic miner archetypes.

- [ ] no-memory miner runs independently.
- [ ] irrelevant-memory miner runs independently.
- [ ] overfit-memory miner runs independently.
- [ ] useful-generalizing miner runs independently.
- [ ] harmful-memory miner runs independently.
- [ ] policy-violating miner runs independently.
- [ ] validator discovers or is test-fixtured against all six.
- [ ] validator fans out challenges.
- [ ] per-miner timeout handled.
- [ ] malformed miner response handled.
- [ ] unavailable miner handled.
- [ ] duplicate/replayed response handled.
- [ ] results bind to miner UID/hotkey and challenge ID.

**State:** `NOT_RUN`

Note: six miners are an internal falsification topology, not a HackQuest hard requirement.

---

## 11. A09 — Evaluator and causal scoring audit

**Goal:** reward only generalized beneficial behavioral influence.

- [x] no-memory A0 condition exists in local mechanism oracle.
- [x] memory-conditioned A1 exists.
- [x] utility delta is central to score.
- [x] useful generalizing miner outranks overfit miner in golden simulation.
- [x] irrelevant/no-memory artifacts do not earn meaningful weight.
- [x] harmful patch is penalized.
- [x] policy-violating patch is hard-vetoed despite positive average uplift.
- [x] capabilities remain fixed between paired conditions in golden design.
- [x] robustness suite passed across private seeds in existing local harness.
- [ ] procedural source/holdout generator integrated into repo runtime.
- [ ] concealed holdout never transmitted to miner.
- [ ] repeated paired trials supported where executor is nondeterministic.
- [ ] per-family minimum gates implemented.
- [ ] uncertainty discount implemented in networked evaluator.
- [ ] adaptive/deep evaluation staging implemented.
- [ ] evaluator version recorded in evidence.
- [ ] source and holdout seeds/commitments recorded safely.

**State:** `LOCAL_PASS / NETWORK_NOT_RUN`

---

## 12. A10 — Anti-gaming audit

**Goal:** stop miners or validators from winning through protocol artifacts rather than useful memory formation.

- [ ] active holdouts never committed publicly before evaluation.
- [ ] source and holdout generated separately from same latent rule/distribution.
- [ ] challenge identifiers are one-time/fresh.
- [ ] miner cannot infer expected output from protocol metadata.
- [ ] static benchmark memorization pressure test exists.
- [ ] capability-smuggling mutation test exists.
- [ ] oversized-patch mutation test exists.
- [ ] source-provenance forgery mutation test exists.
- [ ] exact-output leakage mutation test exists.
- [ ] score-jump/random-audit policy defined.
- [ ] validator evidence supports later retired-seed replay.

**State:** `DESIGN_ONLY`

---

## 13. A11 — Weight construction/submission audit

**Goal:** ensure economic output is valid Bittensor validator behavior.

- [x] score→UID mapping implementation exists.
- [x] `bt.SetWeights` intent path exists.
- [ ] validator confirms its UID/registration.
- [ ] validator confirms validator permit.
- [ ] target subnet live hyperparameters are read.
- [ ] minimum allowed weights handled.
- [ ] maximum weight limits handled.
- [ ] version key handled explicitly if enforced.
- [ ] weights rate limit/preflight handled.
- [ ] commit-reveal behavior verified for target subnet.
- [ ] dry-run/plan succeeds.
- [ ] actual testnet set-weights succeeds.
- [ ] extrinsic result/receipt recorded.
- [ ] emitted weights can be read back from chain/metagraph.

**State:** `IMPLEMENTED_SKELETON / LIVE_NOT_RUN`

---

## 14. A12 — Evidence/provenance audit

**Goal:** make every important claim reconstructable.

Each evaluation batch should eventually record:

- [ ] validator hotkey;
- [ ] miner UID;
- [ ] miner hotkey;
- [ ] challenge ID;
- [ ] generator version;
- [ ] evaluator/executor version;
- [ ] source digest;
- [ ] response/BMP digest;
- [ ] concealed holdout commitment/digest;
- [ ] A0 outcome;
- [ ] A1 outcome;
- [ ] delta utility;
- [ ] regressions;
- [ ] policy violations;
- [ ] final score;
- [ ] weight contribution;
- [ ] timestamp/block context;
- [ ] chain transaction evidence when weights are submitted.

Evidence must distinguish `LOCAL_PASS`, `CI_PASS`, `LOCAL_NETWORK_PASS`, `TESTNET_PASS`, etc.

**State:** `PARTIAL_DESIGN`

---

## 15. A13 — Testnet deployment audit

**Goal:** satisfy the final program requirement with actual Bittensor testnet evidence.

- [ ] current official test network configuration confirmed.
- [ ] subnet/netuid strategy decided.
- [ ] owner/operator wallet documented safely.
- [ ] miner hotkeys funded/registered.
- [ ] validator hotkey funded/registered.
- [ ] miner endpoint reachable from validator.
- [ ] endpoint publication visible on chain.
- [ ] signed network request passes.
- [ ] multiple miners participate.
- [ ] concealed evaluation runs.
- [ ] scores generated.
- [ ] weights submitted.
- [ ] weights visible on chain.
- [ ] restart/recovery test passes.
- [ ] evidence package captured.

**State:** `NOT_RUN`

No submission-ready status before this gate passes.

---

## 16. A14 — Hackathon proposal audit

Checkpoint target: Sep. 20, 2026.

- [x] problem/use case defined.
- [x] digital commodity defined.
- [x] subnet architecture defined at mechanism level.
- [x] miner task defined.
- [x] validator responsibility defined.
- [x] incentive mechanism defined.
- [x] scoring methodology defined.
- [ ] expected users written as a concrete demand-side story.
- [ ] Bittensor ecosystem value written without generic AI-memory claims.
- [ ] testnet roadmap updated from actual implementation status.
- [ ] mechanism diagrams prepared.
- [ ] claims checked against evidence ledger.
- [ ] proposal cold-read against all judging criteria.

**State:** `STRONG_DRAFT_BASE / NOT_SUBMISSION_READY`

---

## 17. A15 — Public repository/final deliverable audit

Final target: Oct. 19, 2026.

- [x] repository is public.
- [x] miner code exists.
- [x] validator code exists.
- [x] core protocol code exists.
- [ ] canonical setup instructions complete.
- [ ] local development instructions complete.
- [ ] wallet/security instructions complete.
- [ ] technical architecture documentation complete.
- [ ] testnet deployment instructions complete.
- [ ] reproducible testnet command path complete.
- [ ] public testnet evidence linked.
- [ ] demo script written from actual evidence.
- [ ] short demo video recorded.
- [ ] final pitch prepared.
- [ ] final proposal updated.
- [ ] repo cold-clone test succeeds.

**State:** `IN_PROGRESS`

---

## 18. Immediate build order from this audit

Do not skip ahead to frontend/demo polish.

### Gate M0.1 — Identity + chain state

1. Add wallet/hotkey configuration layer.
2. Add Bittensor client/netuid configuration.
3. Add metagraph reads.
4. Add registration/UID helpers.

Exit condition: code can resolve a configured hotkey to current subnet participation state without mutating chain state.

### Gate M0.2 — Serve + discover

1. Add `ServeAxon` publication helper.
2. Add miner advertised endpoint configuration.
3. Add metagraph endpoint discovery.
4. Add stale/unserved endpoint handling.

Exit condition: validator can derive miner UID/hotkey/endpoint from Bittensor state rather than a manual endpoint list.

### Gate M0.3 — Authenticated round trip

1. Make network auth fail closed.
2. Add metagraph caller policy.
3. Start miner service with a real hotkey fixture.
4. Send signed validator request.
5. Verify caller and return BMP.
6. Add negative auth/replay tests.

Exit condition: `LOCAL_NETWORK_PASS` for signed validator→miner BMP formation.

### Gate M0.4 — Six-miner pressure network

1. Spawn six archetype miners independently.
2. Fan out one challenge.
3. Evaluate concealed holdouts.
4. reproduce expected rank/veto ordering.
5. bind scores to UIDs/hotkeys.

Exit condition: networked scorer reproduces golden ordering.

### Gate M0.5 — Weight path

1. inspect live target-subnet hyperparameters;
2. construct compliant weights;
3. dry-run/plan SetWeights;
4. test against appropriate Bittensor test environment;
5. record evidence.

Exit condition: chain-conformant weight path passes without claiming mainnet/testnet beyond actual evidence.

### Gate M1 — Testnet

Register/deploy, publish miner endpoints, run evaluation, submit weights, read them back, capture evidence.

Exit condition: `TESTNET_PASS`.

---

## 19. Promotion states

`READY_TO_BUILD`
→ chain/network implementation may proceed.

`READY_FOR_LOCAL_NETWORK`
→ identity, ServeAxon/discovery and auth policy implemented.

`LOCAL_NETWORK_PASS`
→ independently running validator/miner services communicate correctly.

`READY_FOR_TESTNET`
→ registration/deployment docs, security gates, score/weight path and evidence capture are ready.

`TESTNET_PASS`
→ actual Bittensor testnet interaction and weight evidence exists.

`READY_FOR_SUBMISSION`
→ testnet + repo docs + proposal + demo/pitch evidence are complete.

No state may be skipped by renaming a lower-level test.

---

## 20. Current verdict

Consequent has a strong mechanism core and a Bittensor 11-compatible application skeleton, but it is **not yet a complete Bittensor subnet skeleton** because the chain-side neuron lifecycle is incomplete.

The next implementation work is therefore unambiguous:

**wallet/hotkey state → metagraph → ServeAxon → discovery → caller policy → signed round trip → six-miner network → live-conformant SetWeights → testnet.**

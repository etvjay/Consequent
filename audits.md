# Consequent — Build Audit

Status: `ACTIVE`
Ground truth authority: [`GROUND_TRUTH.md`](./GROUND_TRUTH.md)
Current branch: `bootstrap/m0`
Audit date: 2026-08-24

A checkbox is not evidence. Every `PASS` requires a reproducible artifact, CI run, chain read, transaction result, or public-network receipt.

---

## 0. Current release state

**EBI state:** `M0_CLOSED / M1_ACTIVE`

**Current mechanism evidence:** `LOCAL_PASS + CI_PASS`

**Current Bittensor-network evidence:** `CHAIN_LOCAL_ECONOMIC_LOOP_PASS`

**Current public testnet evidence:** `READ_ONLY_TESTNET_PASS` only

Consequent must not be described as a deployed testnet subnet yet.

Authoritative M0 closure evidence: GitHub Actions localnet run `32770499057` / run #34.

---

## 1. Hard stop conditions

Any checked condition blocks promotion toward testnet/submission:

- [ ] unresolved conflict with `GROUND_TRUTH.md`;
- [ ] legacy pre-v11 Axon/Dendrite/Synapse architecture reintroduced as canonical;
- [ ] missing btauth authentication in network mode;
- [ ] no chain-published miner endpoint;
- [ ] canonical validator discovery depends on hard-coded endpoints;
- [ ] no metagraph-backed caller policy;
- [ ] scoring can reward policy-violating BMPs through compensating uplift;
- [ ] BMP can add executable capability;
- [ ] lower evidence class is used to claim testnet or production status;
- [ ] weight submission ignores live subnet constraints;
- [ ] concealed evaluation data is exposed to miners;
- [ ] hackathon requirements are represented from memory rather than current published sources.

---

## 2. A00 — Hackathon truth

- [x] Current HackQuest event page checked 2026-08-24.
- [x] Sep. 20 proposal checkpoint captured.
- [x] Oct. 19 final deliverables captured.
- [x] Judging criteria captured.
- [x] Public-repo and testnet requirements captured.
- [x] No unsupported mandatory starter-kit claim.
- [x] 3 validators / 10 miners classified as evaluator pressure, not published hard requirement.
- [ ] Organizer updates rechecked when new workshops/office hours are published.
- [ ] Final submission form fields captured when available.

**State:** `PASS_WITH_FUTURE_RECHECK`

---

## 3. A01 — Bittensor v11 stack

- [x] Bittensor `11.1.0` pinned/tested.
- [x] Python 3.10 + 3.12 CI pass.
- [x] Own HTTP data plane implemented.
- [x] Consequent-owned schemas implemented.
- [x] `bt.http_auth.sign/verify` integrated.
- [x] `bt.ServeAxon` implemented and chain-proven.
- [x] metagraph discovery implemented and chain-proven.
- [x] live subnet hyperparameter reads implemented.
- [x] live rate-limit compliance implemented.
- [x] `bt.SetWeights` implemented and chain-proven.
- [x] chain weight read-back proven.

**State:** `CHAIN_LOCAL_PASS`

---

## 4. A02 — Commodity/category boundary

Canonical invariant: **STORED ≠ RECALLED ≠ INFLUENTIAL ≠ BENEFICIAL**

- [x] Digital commodity is Behavioral Memory Patch (BMP).
- [x] BMP derives from source execution experience.
- [x] BMP carries provenance.
- [x] BMP is bounded by validator memory budget.
- [x] BMP is declarative rather than executable.
- [x] Capability expansion is excluded.
- [x] Retrieval/storage alone cannot earn reward.
- [x] Paired unseen future execution is central to scoring.
- [ ] expiry/supersession/revocation semantics implemented end-to-end.
- [ ] lifecycle implementation matches `architecture/MEMORY_LIFECYCLE.md`.

**State:** `PASS_DESIGN / PARTIAL_IMPLEMENTATION`

---

## 5. A03 — Protocol/admission

- [x] challenge ID/source episodes/objective/constraints/budget represented.
- [x] BMP response schema exists.
- [x] challenge-response binding tested.
- [x] provenance admission code exists.
- [x] bounded patch count/shape tests exist.
- [x] executable-payload rejection path exists.
- [x] malformed request tests exist.
- [ ] canonical digest format frozen across challenge/BMP/evaluation records.
- [ ] protocol version-negotiation policy frozen.
- [ ] M1 multi-miner duplicate/copy-response handling chain-tested.

**State:** `CI_PASS / CHAIN_MULTI_MINER_NOT_RUN`

---

## 6. A04 — Miner service

- [x] FastAPI health + memory-formation routes implemented.
- [x] raw request body preserved for btauth verification.
- [x] network mode fails closed.
- [x] wallet/hotkey identity loads in network mode.
- [x] sender identity feeds caller policy.
- [x] registered-caller policy exists.
- [x] independent miner process startup proven.
- [x] one chain-registered miner served a signed BMP successfully.
- [ ] six independently chain-registered miner services proven together.
- [ ] production resource/rate limits finalized.

**State:** `CHAIN_LOCAL_SINGLE_MINER_PASS`

---

## 7. A05 — Authentication/authorization

- [x] real Bittensor keypairs used.
- [x] valid signed requests pass.
- [x] replay/tamper rejection tested.
- [x] receiver binding enforced.
- [x] unsigned network requests rejected.
- [x] registered validator → chain-discovered miner signed round trip proven.
- [ ] validator-permit/stake policy proven with non-owner production-like validator state.

**State:** `CHAIN_LOCAL_AUTH_PASS / PRODUCTION_POLICY_NOT_PROVEN`

---

## 8. A06 — Registration and endpoint publication

- [x] wallet/hotkey creation documented.
- [x] subnet registration/activation proven on fresh local chain.
- [x] validator registration proven — UID 1 in M0 run.
- [x] miner registration proven — UID 2 in M0 run.
- [x] non-loopback advertised endpoint validated.
- [x] `ServeAxon` publication proven — extrinsic `18-0006` in M0 run.
- [x] metagraph endpoint read-back proven.
- [ ] six miner registrations/publications proven in one run.
- [ ] public testnet registration/publication proven.

**State:** `CHAIN_LOCAL_SINGLE_MINER_PASS`

---

## 9. A07 — Metagraph discovery/caller policy

- [x] validator reads current metagraph.
- [x] UID/hotkey/endpoint derive from metagraph state.
- [x] unserved miners can be filtered.
- [x] miner checks caller registration.
- [x] caller policy uses current v11 stake field semantics.
- [x] manual endpoints are test adapters, not canonical discovery.
- [ ] multi-miner refresh/churn behavior chain-tested.
- [ ] permit/stake production thresholds validated on public testnet.

**State:** `CHAIN_LOCAL_PASS / M1_CHURN_NOT_RUN`

---

## 10. A08 — Competitive multi-miner loop

Controlled six-miner archetypes:
- no-memory;
- irrelevant-memory;
- overfit-memory;
- useful-generalizing-memory;
- harmful-memory;
- policy-violating-memory.

Current evidence:
- [x] six independent Uvicorn processes run over real sockets.
- [x] validator fans out challenges.
- [x] concealed scoring works.
- [x] results bind miner identity/challenge.
- [x] useful generalizer ranks highest in component pressure test.
- [x] policy-violating miner is hard-vetoed.
- [ ] six hotkeys registered on one Bittensor subnet.
- [ ] six endpoints published with `ServeAxon`.
- [ ] all six discovered from metagraph only.
- [ ] all six queried over btauth using their registered hotkeys.
- [ ] competitive UID weights accepted/read back from chain.

**State:** `LOCAL_NETWORK_COMPONENT_PASS / M1_CHAIN_NOT_RUN`

---

## 11. A09 — Causal evaluator

- [x] A0 no-memory baseline exists.
- [x] A1 memory-conditioned path exists.
- [x] paired utility delta drives score.
- [x] capabilities held constant in controlled evaluator.
- [x] useful generalization beats overfit under distribution shift.
- [x] harmful memory incurs regression penalty.
- [x] policy violation is non-compensable.
- [x] robustness tested across private seeds.
- [ ] adaptive deep-evaluation staging implemented.
- [ ] rolling uncertainty/recency score state implemented for persistent validators.
- [ ] evaluator-major-version migration behavior proven.

**State:** `LOCAL_PASS / M1_ROLLING_ECONOMICS_NOT_PROVEN`

---

## 12. A10 — Adversarial pressure

- [x] benchmark/source-instance overfit fixture exists.
- [x] harmful-memory regression fixture exists.
- [x] policy-violation compensation attack is blocked.
- [x] capability invariance is asserted in controlled evaluation.
- [ ] provenance forgery mutation suite.
- [ ] copied-response/copycat miner chain test.
- [ ] holdout-leakage pressure test.
- [ ] validator/miner collusion simulation.
- [ ] validator cross-seed dispersion audit.
- [ ] stale winner/downtime/churn test.
- [ ] score-jump random-audit policy implemented.

**State:** `PARTIAL_PASS`

---

## 13. A11 — Weight construction and settlement

M0 strict evidence:
- [x] live `min_allowed_weights` read.
- [x] live `max_weights_limit` read.
- [x] live `weights_version` read.
- [x] live `weights_rate_limit=100` read.
- [x] validator waited from 87 remaining blocks to legal submission block 110.
- [x] commit-reveal visibility delay handled explicitly in disposable M0 fixture.
- [x] `SetWeights` accepted — extrinsic `111-0006`.
- [x] chain read-back observed validator UID 0 → miner UID 2 weight `1.0`.
- [ ] competitive six-miner weight vector chain-proven.
- [ ] production commit-reveal path proven without disabling it.
- [ ] public testnet weight submission proven.

**State:** `CHAIN_LOCAL_SINGLE_MINER_ECONOMIC_PASS`

---

## 14. A12 — Evidence/provenance

- [x] evidence classes defined.
- [x] CI and chain-local evidence kept distinct.
- [x] failures retained as evidence rather than erased.
- [x] strict localnet artifact uploaded for M0.
- [x] chain extrinsic references captured for ServeAxon and SetWeights.
- [ ] validator batch evidence record includes all canonical digests/commitments.
- [ ] retired holdout manifests support later replay.
- [ ] M1 competitive evidence bundle generated.

**State:** `M0_PASS / M1_PARTIAL`

---

## 15. A13 — Public testnet deployment

- [x] read-only Bittensor `test` connectivity proven.
- [ ] funded owner/operator wallet prepared.
- [ ] public-test subnet/netuid created/selected.
- [ ] miner hotkeys funded/registered.
- [ ] validator hotkeys funded/registered.
- [ ] public endpoints reachable.
- [ ] `ServeAxon` visible on public test chain.
- [ ] signed BMP traffic succeeds.
- [ ] competitive scoring succeeds.
- [ ] `SetWeights` succeeds under live public-test policy.
- [ ] weight commit/reveal/read-back evidence captured.
- [ ] restart/recovery proof captured.

**State:** `READ_ONLY_TESTNET_PASS / MUTATIONS_NOT_RUN`

---

## 16. A14 — Hackathon proposal

- [x] problem/use case defined.
- [x] digital commodity defined.
- [x] miner task defined.
- [x] validator responsibility defined.
- [x] incentive/scoring design defined.
- [x] architecture reference exists.
- [x] Foundries exist as operating disciplines.
- [ ] demand-side user story sharpened with one concrete consumer integration.
- [ ] M1 evidence incorporated.
- [ ] testnet roadmap updated from real M1 state.
- [ ] proposal cold-read against all seven judging dimensions.

**State:** `STRONG_DRAFT_BASE / NOT_SUBMISSION_READY`

---

## 17. A15 — Public repo/final deliverables

- [x] public repository.
- [x] miner code.
- [x] validator code.
- [x] protocol code.
- [x] localnet documentation.
- [x] testnet runbook draft.
- [x] reference architecture.
- [x] operating Foundries.
- [ ] M1 competitive chain-local evidence.
- [ ] public testnet evidence.
- [ ] cold-clone setup proof.
- [ ] demo script/video.
- [ ] final pitch/proposal.

**State:** `IN_PROGRESS`

---

## 18. Current build order

### M0 — strict one-miner economic loop

**CLOSED.** Run `32770499057` proved registration → serving → discovery → signed BMP → rate-limit compliance → `SetWeights` → chain read-back.

### M1 — competitive chain-local subnet

Build six independently chain-registered miner hotkeys/services and prove:

```text
metagraph discovery
→ signed fan-out
→ six BMPs
→ concealed paired evaluation
→ vetoes/regression penalties
→ competitive UID score vector
→ accepted SetWeights
→ chain read-back
```

Controlled expected ordering:

`useful_generalizing > overfit > no_memory`, with irrelevant, harmful and policy-violating miners at zero under the fixture.

### M2 — adversarial mechanism pressure

Attack copying, leakage, provenance forgery, capability smuggling, collusion, churn, downtime, score jumps and evaluator drift.

### M3 — consumer integration

Prove one external runtime can emit episodes, request competitive BMP formation, persist an accepted BMP, retrieve/apply it later and report influence evidence.

### M4 — public Bittensor testnet

Only after M1/M2/M3 local gates are evidence-backed should funded public-test mutations begin.

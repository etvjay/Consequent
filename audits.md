# Consequent — Build Audit

Status: `ACTIVE`
Ground truth authority: [`GROUND_TRUTH.md`](./GROUND_TRUTH.md)
Current branch: `bootstrap/m0`
Audit date: 2026-09-03

A checkbox is not evidence. Every `PASS` requires a reproducible artifact, CI run, chain read, transaction result, or public-network receipt.

## 0. Current release state

**EBI state:** `M1_CLOSED / M2_ACTIVE`

**Mechanism evidence:** `LOCAL_PASS + CI_PASS`

**Bittensor-network evidence:** `CHAIN_LOCAL_COMPETITIVE_ECONOMIC_LOOP_PASS`

**Public testnet evidence:** `READ_ONLY_TESTNET_PASS` only. Public testnet mutation/deployment remains `NOT_RUN`.

Authoritative closures:
- M0: localnet run #34 / `32770499057`.
- M1: `m1-localnet` run #1 / `32906478860`, evidence artifact `9585670375`, digest `sha256:a55dbe1b34eafc0295e3c0398cec92b89039b181ea9e6d816ba609dbc6bb3b2b`.
- M2-C1 endpoint churn: Actions run #12 / `33577658110`, artifact `9827546184`, digest `sha256:87947c466473604e422398037c236a83add6ae281166bd2e0ac69c5199e19f32`.
- M2-V1 independent validators/Yuma: Actions run #6 / `33577658140`, artifact `9830668013`, digest `sha256:6c0def492691767889e9e10e1ddc74445c7e3fe60e4d07ffaf442d5921298a2b`.

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

## 2. A00 — Hackathon truth

- [x] Current HackQuest event page checked.
- [x] Sep. 20 proposal checkpoint captured.
- [x] Oct. 19 final deliverables captured.
- [x] Judging criteria captured.
- [x] Public-repo and testnet requirements captured.
- [x] No unsupported mandatory starter-kit claim.
- [x] 3 validators / 10 miners classified as evaluator pressure, not published hard requirement.
- [ ] Organizer updates rechecked when new workshops/office hours are published.
- [ ] Final submission form fields captured when available.

**State:** `PASS_WITH_FUTURE_RECHECK`

## 3. A01 — Bittensor v11 stack

- [x] Bittensor `11.1.0` pinned/tested.
- [x] Python 3.10 + 3.12 CI proven.
- [x] Own HTTP data plane + Consequent schemas.
- [x] `bt.http_auth.sign/verify` integrated.
- [x] `bt.ServeAxon` chain-proven.
- [x] metagraph discovery chain-proven.
- [x] live weight hyperparameter reads implemented.
- [x] live Yuma/consensus-environment reads implemented.
- [x] rate-limit compliance chain-proven.
- [x] `bt.SetWeights` and read-back chain-proven.

**State:** `CHAIN_LOCAL_PASS`

## 4. A02 — Commodity/category boundary

Canonical invariant: **STORED ≠ RECALLED ≠ INFLUENTIAL ≠ BENEFICIAL**

- [x] Commodity is Behavioral Memory Patch (BMP).
- [x] BMP derives from source execution experience and carries provenance.
- [x] BMP is bounded and declarative.
- [x] Capability expansion excluded.
- [x] Retrieval/storage alone cannot earn reward.
- [x] Paired unseen future execution drives utility.
- [ ] expiry/supersession/revocation implemented end-to-end.
- [ ] lifecycle implementation matches `architecture/MEMORY_LIFECYCLE.md` end-to-end.

**State:** `PASS_DESIGN / PARTIAL_IMPLEMENTATION`

## 5. A03 — Protocol/admission

- [x] challenge/episode/constraint/budget schema.
- [x] challenge-response binding.
- [x] provenance admission.
- [x] patch count and serialized-size bounds.
- [x] declarative-only action grammar / capability-smuggling rejection.
- [x] malformed protocol coverage.
- [x] semantic BMP digest excludes miner self-label.
- [x] duplicate semantic output surfaced as audit telemetry, not novelty reward.
- [ ] canonical digest format frozen across all evidence records.
- [ ] protocol version-negotiation policy frozen.
- [ ] copy-response behavior proven on chain across multiple miners/validators.

**State:** `CI_PASS_ON_PRIOR_M2_HEAD / CURRENT_HEAD_REVALIDATING`

## 6. A04 — Miner service

- [x] FastAPI health + memory-formation routes.
- [x] raw request body preserved for btauth.
- [x] network mode fails closed.
- [x] wallet/hotkey identity loads in network mode.
- [x] metagraph-backed caller authorization.
- [x] six independent chain-registered miner services proven together in M1.
- [x] six chain-published endpoints proven together in M1.
- [ ] production resource/rate limits finalized.

**State:** `CHAIN_LOCAL_SIX_MINER_PASS`

## 7. A05 — Authentication/authorization

- [x] real Bittensor keypairs.
- [x] valid signed requests pass.
- [x] replay/tamper/receiver binding tested.
- [x] unsigned network requests rejected.
- [x] chain-discovered signed validator→miner round trip.
- [x] non-owner validator permit/stake semantics chain-proven.

M2-V1 registered/staked two non-owner validators, waited for real permits,
required miner-side permit authorization, and submitted three independent
rows. The successful chain-local evidence is recorded above.

**State:** `CHAIN_LOCAL_AUTH_AND_PERMIT_PASS`

## 8. A06 — Registration and endpoint publication

- [x] subnet registration/activation proven.
- [x] M0 one-validator/one-miner lifecycle proven.
- [x] M1 six independent miner registrations proven — UIDs 1–6.
- [x] M1 six `ServeAxon` publications proven.
- [x] metagraph endpoint read-back proven.
- [ ] public testnet registration/publication proven.

**State:** `CHAIN_LOCAL_MULTI_MINER_PASS`

## 9. A07 — Metagraph discovery/caller policy

- [x] current metagraph drives UID/hotkey/endpoint discovery.
- [x] unserved miners filtered.
- [x] caller registration checked.
- [x] v11 stake semantics used.
- [x] M1 exactly six miners discovered from metagraph only.
- [x] endpoint-churn pressure run (M2-C1).
- [ ] persistent disappearance/restart pressure run.
- [x] permit/stake thresholds validated outside owner special status (M2-V1).

**State:** `CHAIN_LOCAL_MULTI_MINER_PASS / ENDPOINT_CHURN_PASS / RESTART_NOT_RUN`

## 10. A08 — Competitive multi-miner loop

Controlled archetypes: no-memory, irrelevant-memory, overfit-memory, useful-generalizing-memory, harmful-memory, policy-violating-memory.

- [x] six independent Uvicorn processes.
- [x] six chain-registered hotkeys.
- [x] six `ServeAxon` records.
- [x] metagraph-only discovery.
- [x] btauth challenge fan-out.
- [x] concealed paired scoring.
- [x] useful generalizer beats overfit.
- [x] no-memory/irrelevant/harmful receive zero.
- [x] policy-violating miner hard-vetoed.
- [x] competitive UID vector accepted and read back from chain.

Authoritative M1 result: useful UID4 `0.6746805888` computed / `0.6746795697` observed; overfit UID3 `0.3253194112` computed / `0.3253204303` observed.

**State:** `CHAIN_LOCAL_COMPETITIVE_PASS`

## 11. A09 — Causal evaluator and rolling economics

- [x] A0 baseline and A1 memory treatment.
- [x] paired utility delta drives score.
- [x] capabilities held constant.
- [x] generalization beats source-bound overfit.
- [x] regression penalty.
- [x] policy violation non-compensable.
- [x] adaptive deep-evaluation scheduler implemented.
- [x] score-jump / duplicate / new-miner / stale / failure audit signals implemented.
- [x] rolling EMA/freshness/failure state implemented.
- [x] evaluator-version mismatch makes old score economically ineligible.
- [x] first success under new evaluator resets history to a new epoch.
- [ ] persistent rolling economics proven in repeated chain rounds.

**State:** `LOCAL_IMPLEMENTATION_PASS / PERSISTENT_CHAIN_ROUNDS_NOT_RUN`

## 12. A10 — Adversarial pressure

See [`evaluation/M2_ADVERSARIAL.md`](./evaluation/M2_ADVERSARIAL.md).

Implemented/local/reference controls:
- [x] source-instance overfit fixture.
- [x] provenance-forgery rejection.
- [x] capability-smuggling rejection.
- [x] malformed/oversized BMP rejection.
- [x] challenge-binding/replay defense.
- [x] duplicate semantic-response telemetry.
- [x] holdout serialization separation regression coverage.
- [x] catastrophic regression penalty.
- [x] policy compensation hard veto.
- [x] stale winner/downtime score ineligibility.
- [x] score-jump/random-audit policy.
- [x] evaluator-version drift requalification.
- [x] Yuma reference consensus/clipping model.
- [x] three-validator independent-seed reference test.
- [x] 100-private-seed validator-dispersion harness implemented.
- [x] current-head CI for newest dispersion/Yuma additions completed (prior current-head run; packaging-only follow-up in progress).
- [x] endpoint churn chain pressure (M2-C1).
- [ ] restart/disappearance chain pressure.
- [x] non-owner multi-validator chain proof (M2-V1).
- [ ] commit-reveal-on settlement proof (M2-V2).
- [ ] miner-validator collusion chain pressure.

**State:** `M2_ACTIVE / REFERENCE_AND_LOCAL_CONTROLS_ADVANCED / CHAIN_LOCAL_V1_PASS / CR_NOT_RUN`

## 13. A11 — Weight construction and settlement

- [x] live min/max/version/rate-limit reads.
- [x] M0 single-miner `SetWeights` + read-back.
- [x] M1 competitive six-miner `SetWeights` + read-back — extrinsic `124-0006`.
- [x] weight-rate-limit compliance proven.
- [x] current consensus environment (tempo/kappa/validator cap/activity/bond/Yuma fields) readable.
- [x] multiple independent validator rows chain-proven (M2-V1).
- [x] actual post-epoch Yuma outcome chain-proven for Consequent (M2-V1).
- [ ] production commit-reveal path proven without disabling it.
- [ ] public testnet weight submission proven.

**State:** `CHAIN_LOCAL_COMPETITIVE_ECONOMIC_PASS / MULTIVALIDATOR_YUMA_PASS / CR_NOT_RUN`

## 14. A12 — Evidence/provenance

- [x] evidence classes defined.
- [x] lower evidence classes not promoted to chain/testnet claims.
- [x] failures retained.
- [x] M0 evidence artifact.
- [x] M1 competitive evidence artifact.
- [x] chain extrinsic references retained.
- [ ] complete validator batch digest/commitment record.
- [ ] retired holdout manifests support later replay.
- [x] M2-V1 evidence bundle generated by a successful run.

**State:** `M1_PASS / M2_EVIDENCE_ACTIVE`

## 15. A13 — Public testnet deployment

- [x] read-only Bittensor `test` connectivity.
- [ ] funded public-test operator setup.
- [ ] subnet/netuid mutation.
- [ ] miner/validator registrations.
- [ ] public served endpoints.
- [ ] signed BMP traffic.
- [ ] competitive scoring.
- [ ] commit/reveal and weight settlement.
- [ ] restart/recovery proof.

**State:** `READ_ONLY_TESTNET_PASS / MUTATIONS_NOT_RUN`

## 16. A14 — Hackathon proposal

- [x] problem/use case.
- [x] digital commodity.
- [x] miner task.
- [x] validator responsibility.
- [x] incentive/scoring design.
- [x] architecture/Foundries.
- [ ] one concrete demand-side consumer integration.
- [x] M1 evidence incorporated into submission draft.
- [x] roadmap updated from M2 evidence.
- [ ] cold-read against all seven judging dimensions.

**State:** `STRONG_DRAFT_BASE / NOT_SUBMISSION_READY`

## 17. A15 — Public repo/final deliverables

- [x] public repo, miner code, validator code, protocol code.
- [x] localnet documentation and reference architecture.
- [x] M1 competitive chain-local evidence.
- [ ] public testnet evidence.
- [ ] cold-clone proof.
- [ ] demo/video.
- [ ] final proposal/pitch.

**State:** `IN_PROGRESS`

## 18. Current build order

### M0 — CLOSED
One-miner strict chain-local economic loop.

### M1 — CLOSED
Six independently chain-registered miners, concealed competitive evaluation, competitive UID weights, accepted `SetWeights`, chain read-back. Authoritative run `32906478860`.

### M2 — ACTIVE
Attack the measurement and economic mechanism. Immediate gates:

```text
current-head CI/M0/M1 regression
→ 100-seed validator-dispersion evidence
→ M2-C1 endpoint-churn pressure
→ M2-V1 non-owner multi-validator/Yuma chain proof
→ M2-V2 commit-reveal-on settlement
→ restart/disappearance and rolling chain rounds
→ residual-risk review
```

M2 exit: no unresolved `CRITICAL` finding and no unbounded `HIGH` finding, with reproducible evidence for every closed attack.

### M3 — consumer integration
One external runtime emits episodes, requests competitive BMP formation, persists/retrieves/applies accepted BMPs, and reports influence evidence.

### M4 — public Bittensor testnet
Only after the preceding local/chain gates are evidence-backed should funded public-test mutations begin.

# Consequent Subnet Proposal

**Checkpoint:** HackQuest — Bittensor Global Subnet Hackathon, Checkpoint #1  
**Status:** `DRAFT / DESIGN-FROZEN, TESTNET EVIDENCE INCOMPLETE`  
**Repository:** `etvjay/Consequent`  
**Implementation branch:** `bootstrap/m0`  
**Proposal revision:** 2026-09-01

This proposal describes the mechanism we intend to build. Evidence labels are
deliberate: a local or simulated result is not represented as testnet proof.

## 1. Problem and use case

Agents generate large amounts of execution history, but preserving or
retrieving that history does not establish that the agent learned anything
useful from it. The important question is:

> Given prior execution experience, what should an agent learn so that its
> behavior improves on unseen future tasks?

Existing memory products commonly optimize storage, retrieval, context
injection, or summarization. Consequent targets a different commodity:
**formation of bounded behavioral memory whose causal effect can be measured.**

The governing distinction is:

```text
STORED ≠ RECALLED ≠ INFLUENTIAL ≠ BENEFICIAL
```

Initial task families are:

- API and protocol adaptation;
- tool-execution recovery;
- authority and policy execution.

Example: an agent encounters an authentication failure and later discovers a
credential-refresh procedure. A miner should form a rule that generalizes that
lesson to concealed future authentication tasks, without introducing a new
tool, endpoint, or executable capability.

## 2. Digital commodity

The commodity is a **Behavioral Memory Patch (BMP)**: a bounded,
provenance-linked, declarative artifact that can be consumed after its miner
goes offline.

A BMP must:

1. derive from identifiable execution episodes;
2. cite source episode IDs;
3. fit the validator's rule and byte budget;
4. contain declarative behavior only;
5. be evaluated on future tasks;
6. support invalidation, expiry, or supersession as the protocol matures.

The protocol does not prescribe how a miner forms a BMP. Reflection, causal
attribution, symbolic induction, learned models, language models, or hybrids
may compete. The returned artifact must satisfy the shared protocol.

Consequent is not a decentralized vector database, generic agent memory
layer, prompt or skill marketplace, Engram replacement, or generic agent
benchmark.

## 3. Subnet architecture

```text
source execution episodes
          ↓
validator challenge with hidden holdout boundary
          ↓  btauth/1 signed HTTP
multiple miner BMPs
          ↓
structural and provenance admission
          ↓
concealed paired execution
 A0: no patch     A1: candidate patch
          ↓
uplift, regressions, policy and uncertainty checks
          ↓
UID score vector and chain-conformant weights
          ↓
Bittensor SetWeights and Yuma settlement
```

The boundary between the application and Bittensor is explicit:

| Layer | Consequent owns | Bittensor owns |
|---|---|---|
| Data plane | HTTP service, schemas, fan-out, timeouts, signed request verification | Network identity and hotkeys |
| Evaluation | BMP admission, concealed tasks, paired execution, scoring, evidence | Validator eligibility and permits |
| Settlement | UID-to-score/weight construction | Weight acceptance, consensus, incentives, bonds, dividends |
| Discovery | Current metagraph-derived endpoint selection | Registration, endpoint records, chain state |

The MVP does not store BMP payloads on chain. It produces evaluated, portable
artifacts and evidence; an external consumer integration is a subsequent
milestone.

## 4. Miner responsibilities and interface

### Input

`POST /v1/memory/formation`, authenticated with `btauth/1`, contains:

- `challenge_id`;
- prior `ExecutionEpisode` records;
- optional task family;
- memory budget, capped at 16 rules in BMP v0.1;
- policy constraints;
- evaluator version.

### Output

The miner returns a `MemoryFormationResponse` containing the same
`challenge_id` and a `BehavioralMemoryPatch`:

```json
{
  "patch_version": "bmp/0.1",
  "miner_strategy": "example-strategy",
  "rules": [
    {
      "rule_id": "auth-refresh-1",
      "family": "api_protocol",
      "conditions": {"error_class": "expired_credential"},
      "action": "refresh_credential_then_retry_once",
      "provenance": ["episode-12", "episode-18"],
      "confidence": 0.92
    }
  ]
}
```

Admission rejects malformed, unbound, oversized, duplicate, or capability-
smuggling patches before they can earn causal score. A miner is rewarded for
the consequences of its patch, not for length, retrieval frequency, semantic
similarity, or a validator's aesthetic preference.

## 5. Validator responsibilities and evaluation

A validator must:

1. generate or select source episodes from a private task distribution;
2. construct a challenge without serializing concealed holdout facts;
3. fan the challenge out to registered miners discovered from the metagraph;
4. verify the signed response and challenge binding;
5. perform structural and provenance admission;
6. execute identical future tasks in paired conditions;
7. measure utility, uplift, regression, policy violations, and uncertainty;
8. maintain rolling identity, freshness, and evaluator-version state;
9. convert eligible scores into a chain-conformant UID weight row;
10. submit and read back weights when chain policy permits;
11. retain enough evidence to replay or audit the result.

The counterfactual invariant is:

```text
U0 = utility(A, task, no_patch)
U1 = utility(A, task, patch)
ΔU = U1 - U0
```

`A0` and `A1` use the same task, environment, objective, and capabilities.
The patch condition is the controlled treatment variable. Hidden future tasks
are never sent to miners.

The MVP evaluator is deterministic and bounded. Unrestricted LLM-agent judging
is outside the validated mechanism.

## 6. Scoring and incentive mechanism

For each concealed task, the evaluator records `ΔU`. The current MVP score is:

```text
diagnostic_quality
  = mean_uplift
  - 0.75 × regression_rate
  - 0.10 × uncertainty
```

The score is `max(0, diagnostic_quality)` unless either of the following is
true:

- any policy violation occurs; or
- a catastrophic regression occurs (`ΔU ≤ -1` on the MVP utility scale).

Either condition is a hard veto and produces zero economic score for the
patch. Smaller regressions remain continuously penalized. Positive uplift
cannot purchase permission to violate policy or destroy previously correct
behavior.

Eligible miner scores are normalized into a UID-to-weight mapping. Bittensor
then applies its live validator-permit, rate-limit, minimum/maximum weight,
version, commit-reveal, and Yuma rules. Consequent does not claim that a
locally normalized vector is an economic outcome; accepted chain settlement is
the relevant evidence.

Validators are economically rewarded through Bittensor's normal validator
incentive path when their fresh, stake-supported opinions contribute to useful
consensus. Consequent's design therefore requires private holdouts and fresh
evaluation: copying a public weight row should not provide the information
advantage earned by doing the work.

## 7. Adversarial boundaries

The mechanism explicitly addresses:

- source-provenance laundering;
- benchmark and holdout leakage;
- source-instance memorization;
- copied or replayed responses;
- oversized or executable payloads;
- policy violations hidden by aggregate uplift;
- catastrophic regressions;
- stale winners, endpoint changes, and UID reuse;
- evaluator-version drift;
- validator copying and correlated evaluation;
- malicious validator minority behavior.

Some defenses are protocol-local. Others are system boundaries. In particular,
Consequent cannot cryptographically force a malicious validator to run its
reference evaluator; Bittensor's stake-weighted consensus is the protection
against unsupported minority rows. Majority economic capture remains a
Bittensor-level assumption, not a Consequent claim.

## 8. Expected users and ecosystem value

The immediate user is an agent runtime or agent fleet that wants portable,
execution-derived behavioral knowledge rather than raw transcripts. Potential
consumers include:

- agent runtimes that apply approved BMPs before future work;
- workflow and tool-use systems that need recovery rules;
- protocol/API agents that must adapt to changing interfaces;
- safety and authority systems that need reusable operational lessons.

The consumer surface is intentionally not part of the first scoring proof. The
next consumer milestone will expose a winning BMP together with provenance,
evaluator version, score evidence, and validity state so a runtime can decide
whether and how to apply it.

The longer-term ecosystem value is a competitive market over the transformation
of experience into useful future behavior. Different miners can specialize in
abstraction, failure recovery, policy learning, conservative formation, or
tool-use adaptation while validators select for measured generalization.

Demand and production willingness to pay are hypotheses, not yet validated
facts.

## 9. Current implementation and evidence

| Claim | Evidence state |
|---|---|
| BMP/request/response schema exists | `CI_PASS` |
| Declarative admission and provenance checks exist | `CI_PASS` |
| Deterministic paired evaluator and vetoes exist | `CI_PASS` / `SIMULATED_PASS` |
| Signed HTTP transport exists | `CI_PASS` / local round-trip coverage |
| Six-miner competitive local chain loop | `CHAIN_LOCAL_PASS` (M1) |
| UID weights accepted and read back locally | `CHAIN_LOCAL_PASS` (M1) |
| Endpoint churn workflow | `CHAIN_LOCAL_PASS` in current GitHub Actions run |
| Independent non-owner validator rows and Yuma settlement | `FAILED` at current M2 row-submission step |
| Commit-reveal-on settlement | `UNPROVEN` |
| Public Bittensor testnet deployment | `NOT_RUN` |
| External BMP consumer | `UNPROVEN` |

The failed M2 run reached the row-submission step but stopped before the first
row was written because the local Subtensor `get_subnet_hyperparams_v3` response
did not expose `bonds_penalty`. The compatibility fix preserves that value as
explicitly unknown instead of fabricating a default; a fresh workflow run is
still required to earn the chain evidence.

The current code is on [`bootstrap/m0`](https://github.com/etvjay/Consequent/tree/bootstrap/m0).
The default `main` branch is not yet the implementation branch. The open draft
PR is [#1](https://github.com/etvjay/Consequent/pull/1).

## 10. Roadmap

### Checkpoint #1 — proposal

- freeze the commodity, architecture, miner task, validator truth mechanism,
  scoring formula, incentive path, and evidence boundaries;
- publish this proposal with explicit limitations.

### Testnet implementation

1. repair M2 independent validator-row submission;
2. prove non-owner validator permits and post-epoch Yuma outcome;
3. prove commit-reveal-on submission, application, and read-back;
4. run registered miners through current-metagraph discovery and `ServeAxon`;
5. deploy the smallest reproducible Bittensor testnet topology;
6. capture receipts, chain state, logs, and replay instructions.

### Ecosystem and final submission

1. add a minimal consumer that requests and applies a winning BMP;
2. measure repeated-round freshness, disappearance, endpoint change, and
   evaluator migration;
3. reconcile repository status documents and promote the implementation branch
   when evidence supports it;
4. produce the demo video, updated proposal, setup instructions, and final
   pitch.

## 11. Claims we will not make yet

Consequent will not claim that it has a production subnet, public testnet
traction, demonstrated market demand, independent learned miner algorithms,
commit-reveal settlement, or robust protection against majority validator
capture until the corresponding evidence exists.

The design is complete enough for the proposal checkpoint. The implementation
is not complete enough for the final submission checkpoint.

## References

- [HackQuest — Bittensor Global Subnet Hackathon](https://www.hackquest.io/hackathons/Bittensor-Global-Subnet-Hackathon)
- [Consequent ground truth](../GROUND_TRUTH.md)
- [Consequent protocol](./PROTOCOL.md)
- [Architecture](../evaluation/ARCHITECTURE.md)
- [Bittensor economics](../architecture/BITTENSOR_ECONOMICS.md)
- [Adversarial evaluation](../evaluation/M2_ADVERSARIAL.md)

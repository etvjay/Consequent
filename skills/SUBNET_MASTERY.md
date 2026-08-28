# Subnet Mastery Skill

Purpose: train a builder to design, implement, attack, operate and explain a Bittensor subnet at protocol-engineering depth rather than merely use the SDK.

This is a learn-by-doing skill. Reading without a design decision, implementation consequence or evidence artifact does not count as a completed session.

## Competence target

A practitioner using this skill should be able to answer, from first principles:

1. What scarce digital commodity does this subnet produce?
2. Why should miners compete to produce it?
3. What does a validator actually know, observe or measure?
4. Why does the score select the desired commodity rather than a proxy?
5. How can miners, validators or coalitions game the mechanism?
6. How do local scores become Bittensor weights and economic consequence?
7. Which Bittensor constraints are protocol facts versus subnet choices?
8. What evidence proves the mechanism on chain?
9. Who consumes the subnet output and why would demand persist?
10. What would make the subnet unnecessary?

## Knowledge ladder

### L0 — Chain and network literacy
Master:
- coldkeys, hotkeys, UIDs and netuids;
- registration and deregistration;
- metagraph state;
- validator permits and stake;
- miner serving and endpoint publication;
- signed data-plane authentication;
- weight versioning, min/max constraints and rate limits;
- commit-reveal weights;
- tempo/epoch timing;
- Yuma consensus, clipping, miner incentive, validator dividends and bonds.

Exit test: trace one validator weight from local computation to chain acceptance and eventual economic effect.

### L1 — Commodity and mechanism design
Master:
- digital-commodity definition;
- miner output contract;
- validator truth source;
- objective and proxy separation;
- incentive compatibility;
- generalisation versus benchmark memorisation;
- cost asymmetry between mining and validation;
- selection pressure and exploration;
- non-compensable safety/policy failures.

Exit test: explain why the mechanism still rewards the intended resource under an adversarial miner population.

### L2 — Miner engineering
Master:
- protocol schemas;
- identity/authentication;
- caller authorisation;
- bounded resource use;
- strategy/model adapters;
- deterministic versus learned strategies;
- availability and restart behaviour;
- telemetry;
- compatibility/version handling.

Exit test: independently deploy a miner that can be registered, served, discovered, queried and evaluated without privileged validator knowledge.

### L3 — Validator engineering
Master:
- challenge generation;
- hidden evaluation distributions;
- source/holdout separation;
- paired/counterfactual testing;
- uncertainty and repeat sampling;
- regression and policy gates;
- adaptive deep evaluation;
- rolling scores and freshness;
- UID/hotkey/endpoint binding;
- score-to-weight conversion;
- live chain-policy reads and settlement scheduling.

Exit test: reproduce the score and resulting weight from an evidence record without trusting the original validator process.

### L4 — Adversarial economics
Master attacks involving:
- source-instance overfitting;
- holdout leakage;
- capability smuggling;
- malformed/oversized responses;
- provenance forgery;
- replay and staleness;
- miner copying;
- validator copying;
- miner-validator collusion;
- majority stake capture;
- endpoint/UID churn;
- score jumps;
- downtime games;
- evaluator-version drift;
- commit-reveal mistakes;
- selective evaluation and evidence omission.

Exit test: produce an attack, demonstrate it or bound it, then show the mitigation does not destroy the rewarded commodity.

### L5 — Production subnet operations
Master:
- independent validators;
- private challenge seeds;
- commit-reveal settlement;
- public-test deployment;
- key/secret isolation;
- evidence durability;
- cold-start and recovery;
- cost envelopes;
- latency/throughput budgets;
- monitoring and incident response;
- protocol upgrades;
- backwards compatibility;
- reproducible runbooks.

Exit test: operate repeated rounds without manual semantic intervention and preserve auditable evidence across restarts/upgrades.

### L6 — Subnet product and market
Master:
- consumer integration;
- demand-side utility;
- why Bittensor competition beats a central service;
- miner entry incentives;
- validator operating economics;
- commodity quality improvement over time;
- external benchmarks and adoption evidence;
- mechanism evolution without category drift.

Exit test: identify a real consumer whose utility increases because the subnet exists, and demonstrate the path from subnet output to that utility.

## Session contract

Every training session contains exactly these phases:

```text
SCENARIO
→ DESIGN DECISION
→ PREDICTION
→ IMPLEMENT / MODEL
→ ADVERSARIAL CASE
→ EVIDENCE
→ POST-MORTEM
```

Required output:
- one architectural/mechanism decision;
- one invariant;
- one attack;
- one experiment or chain observation;
- one evidence classification;
- one unresolved question.

## Consequent default case study

Use Consequent unless another subnet gives a better contrast.

Canonical question:

> Can validators economically select miners that form execution-derived memory which causes generalised beneficial future behaviour, without rewarding storage, retrieval, capability expansion, leakage or benchmark gaming?

Consequent progression:
- M0: strict one-miner chain-local economic loop — CLOSED;
- M1: six-miner competitive chain-local loop — CLOSED;
- M2: adversarial and multi-validator pressure — ACTIVE;
- M3: external consumer proof — PENDING;
- public testnet repeated operation — PENDING.

## Weekly deliberate practice

- Day 1: reverse-engineer one live subnet's commodity and validator truth.
- Day 2: reproduce one chain/network primitive locally.
- Day 3: redesign one scoring mechanism and state the new attack surface.
- Day 4: run one adversarial experiment.
- Day 5: trace one score through Yuma/economic settlement assumptions.
- Day 6: review one production failure mode or runbook.
- Day 7: give a five-minute subnet design defence without notes.

The goal is not memorising Bittensor terminology. The goal is becoming capable of judging whether a mechanism will survive miners, validators, chain constraints, evaluators and real users.
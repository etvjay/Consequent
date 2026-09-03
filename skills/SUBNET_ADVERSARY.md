# Subnet Adversary Skill

Purpose: systematically attack a Bittensor subnet until its rewarded commodity, validator truth and economic settlement survive plausible adversarial behavior or the residual risk is explicitly bounded.

This skill is not a checklist-only security review. Every serious finding must end in a pressure test, evidence artifact or clearly stated unproven boundary.

## Primary question

> Can an attacker obtain economic reward, suppress a better competitor, bias validator truth, or corrupt evidence without actually producing the intended digital commodity?

## Attack model

Consider at least four adversary classes:

1. Miner adversary — optimizes for validator score rather than real commodity quality.
2. Validator adversary — manipulates tasks, scoring, evidence or weight rows.
3. Coalition adversary — miners and validators collude or validators coordinate.
4. Environment adversary — chain timing, endpoint churn, partial failure, version drift and network conditions create exploitable gaps.

## Attack procedure

For every claim or invariant:

```text
CLAIM
→ CHEAPEST PROFITABLE VIOLATION
→ PRECONDITIONS
→ ATTACK TRACE
→ EXPECTED ECONOMIC EFFECT
→ DETECTION SIGNAL
→ MITIGATION
→ MITIGATION SIDE EFFECT
→ PRESSURE TEST
→ EVIDENCE CLASS
→ RESIDUAL RISK
```

Do not close a finding because the mitigation sounds plausible.

## Mandatory attack families

### Commodity substitution
Can a miner earn by returning something correlated with the commodity but not the commodity itself?

Examples:
- fluent answer instead of useful output;
- stored/recalled memory instead of beneficial memory;
- benchmark-specific rule instead of generalised behavior;
- capability expansion disguised as memory.

### Evaluator leakage
Can active holdouts, latent rules, seeds, expected outputs or validator heuristics leak through request shape, timing, public artifacts or reused fixtures?

### Overfitting and memorisation
Can the miner bind source-instance identifiers, literal values or recurring benchmark templates and still appear useful?

### Capability smuggling
Can the miner add code, tools, permissions, external model endpoints or executable payloads that make A1 more capable than A0?

### Provenance attacks
Can a miner cite nonexistent episodes, wrong task families, copied evidence or fabricated causal origins?

### Response-shape attacks
Malformed JSON, oversized patches, duplicate identifiers, Unicode/encoding tricks, recursive structures, resource exhaustion and parser differentials.

### Replay/freshness attacks
Can old valid responses be replayed against new challenges, stale miner state retain reward, or signatures survive outside intended windows?

### Copying and cartel behavior
Can miners copy winners and obtain unjustified reward? Can validators copy rows/evidence and reduce independent evaluation without detection?

Important: identical useful algorithms are not inherently malicious. Do not create a novelty reward unless novelty is actually the commodity.

### Collusion
Can a validator leak tasks to a favored miner? Can validators coordinate biased private distributions? What stake fraction is required to alter effective consensus?

### Score manipulation
Mean-uplift compensation, selective task-family excellence, hidden catastrophic regressions, variance exploitation, score-jump attacks and adaptive sampling abuse.

### Identity/state churn
UID recycling, hotkey replacement, endpoint moves, deregistration/re-registration, stale metagraph caches and score inheritance across changed identities.

### Availability games
Strategic downtime, answering only favorable challenges, timeout manipulation and denial-of-service against evaluator capacity.

### Chain settlement attacks
Weight rate-limit mistakes, version mismatch, commit-reveal misuse, reveal omission, stale commit, min-weight/clipping interactions and incorrect assumptions about row visibility.

### Evidence attacks
Missing failed samples, unverifiable seeds, overwritten artifacts, secret leakage, selective publication and claims stronger than evidence class.

## Severity

CRITICAL — breaks the rewarded commodity, causal truth or economic settlement.
HIGH — sustained profitable gaming, validator truth corruption or major availability/economic weakness.
MEDIUM — bounded degradation with clear containment.
LOW — nuisance, ergonomics or low-impact operational weakness.

## Release rule

Do not advance a production/testnet gate with:
- any unresolved CRITICAL;
- any unbounded HIGH;
- any HIGH whose mitigation has not been pressure-tested at the evidence level required by the release claim.

## Consequent-specific invariants

Attack these continuously:

- `STORED ≠ RECALLED ≠ INFLUENTIAL ≠ BENEFICIAL`;
- BMP must derive from identifiable source execution;
- BMP may not expand executable capability;
- `Capabilities(A0) == Capabilities(A1)`;
- future evaluation must be concealed from miners;
- reward requires future causal utility, not retrieval or wording quality;
- policy violations are non-compensable;
- stale/evaluator-old scores cannot silently retain economic eligibility;
- UID/hotkey/endpoint changes cannot silently inherit incompatible score state;
- chain weights must be traceable to admissible evaluation evidence.

## Evidence template

Each finding should produce:

```text
Finding ID:
Claim under attack:
Severity:
Adversary:
Preconditions:
Attack path:
Expected reward/control gained:
Observed result:
Detection signal:
Mitigation:
Mitigation cost/trade-off:
Pressure test:
Evidence artifact:
Evidence class:
Residual risk:
Status:
```

## Training mode

A useful adversarial exercise gives a subnet description and asks the practitioner to:
1. find the cheapest score exploit;
2. find the cheapest validator-truth exploit;
3. find one chain/operational exploit;
4. rank them by economic impact;
5. design the minimum mitigation;
6. state what evidence would actually close each finding.

The skill is complete only when the builder naturally asks, before implementation: “What behavior would maximize the score if I did not care about the intended commodity?”
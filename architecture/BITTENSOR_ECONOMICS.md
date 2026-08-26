# Bittensor Economic Mechanics for Consequent

Verified against current Bittensor documentation on 2026-08-26.

This file is not a generic Bittensor tutorial. It records the chain mechanics that materially constrain Consequent's validator design, evidence model, and long-term subnet economics.

Canonical rule:

> Consequent defines miner utility. Bittensor decides how validator opinions become economic allocation.

The two layers must be designed together.

---

## 1. Economic stack

```text
Consequent
  source episodes
  → BMP formation
  → admission
  → concealed causal evaluation
  → validator utility estimate
  → normalized UID weight row

Bittensor
  validator permit/activity filtering
  → row filtering/normalization
  → stake-weighted consensus per miner
  → consensus clipping
  → miner rank/incentive
  → validator bonds/dividends
  → epoch settlement
```

The subnet is therefore not complete when a validator computes a score. The score matters economically only if the weight-setting identity is eligible, active, accepted by chain policy, and useful under Yuma Consensus.

---

## 2. Validator eligibility is part of correctness

Current Bittensor behavior:
- validator permits are recomputed each epoch;
- only top-stake non-zero neurons up to `max_validators` receive permits;
- the subnet owner's UID is always permitted;
- a non-permitted validator's weight row is discarded;
- losing a permit also clears accumulated bonds;
- permitted but inactive validators are excluded from consensus.

Consequent implication:

```text
computed score ≠ economically active validator opinion
```

Production validators must continuously record:
- UID/hotkey;
- permit status;
- active/inactive status;
- stake weight;
- last weight update;
- effective activity cutoff.

A run where an ineligible validator computes correct weights is not a successful economic proof.

---

## 3. Yuma consensus is not an average of validator scores

At an epoch, surviving validator weight rows are normalized. For each miner, Bittensor computes a stake-weighted consensus threshold controlled by `kappa` (approximately 0.5 by default). Validator weights above that consensus are clipped.

Simplified per-miner model:

```text
validator raw weights W
        ↓
stake-weighted consensus C_j
        ↓
clipped weight Wbar_ij = min(W_ij, C_j)
        ↓
rank_j = Σ_i stake_i × Wbar_ij
        ↓
normalized miner incentive
```

Consequent implication: independent validators do not need identical private tasks or identical raw scores. They do need enough statistical agreement that genuinely useful miners receive sustained stake-supported weight.

The target is therefore:

> independent evidence, correlated quality ordering.

Not:

> identical validators running identical benchmarks.

Identical hidden tests would increase benchmark extraction and copying risk.

---

## 4. Multi-validator acceptance criterion

For a controlled Consequent population, run at least three independent validator evaluators with:
- distinct private seeds;
- equivalent evaluator grammar/version;
- independently generated concealed holdouts;
- identical public source challenge contract;
- no access to peer weight rows before their own evaluation is frozen.

Measure:
1. pairwise rank correlation;
2. top-miner agreement;
3. hard-veto agreement on policy-violating miners;
4. per-miner score dispersion;
5. stake-weighted Yuma consensus/clipping outcome;
6. whether the useful-generalizing miner remains economically dominant after clipping;
7. sensitivity to one noisy/contrarian validator;
8. sensitivity to a high-stake malicious validator below and above `kappa` support.

A multi-validator test is not successful merely because every validator process completed.

---

## 5. Validator incentives: bonds and dividends

Validators are paid for more than submitting any acceptable row. Bittensor maintains validator–miner bonds and derives validator dividends from those bonds and miner incentive.

Current mechanics include:
- consensus clipping of out-of-consensus weights;
- `bonds_penalty`, which controls how much raw vs clipped weight contributes to bond accrual;
- a bonds EMA controlled by `bonds_moving_avg`;
- optional Yuma3 behavior;
- optional liquid alpha when Yuma3 is enabled.

Consequent consequence:

A validator implementation that cheaply copies historical public consensus should not be our target architecture. Validators should gain an informational advantage by performing fresh private evaluation of miner quality.

That means:
- active holdouts remain private;
- commit-reveal remains enabled in production-like deployments;
- challenge distributions evolve;
- evidence is independently generated;
- score changes are detected early enough to make fresh evaluation useful.

---

## 6. Commit-reveal is production semantics

New subnets currently default to `commit_reveal_weights_enabled = true`.

When enabled:
- plaintext `set_weights` is rejected;
- validators commit hidden weights;
- reveal timing is controlled by `commit_reveal_period` in epochs/tempos, not raw blocks;
- current SDK/CLI paths can use timelocked encrypted commits and automatic later application;
- `weights_rate_limit` applies at commit time.

The default reveal period is one epoch. At a 360-block tempo and 12-second blocks, this is roughly 72 minutes.

Consequent policy:
- disabling commit-reveal is allowed only in disposable deterministic evidence fixtures where immediate read-back is the explicit objective;
- public-testnet and production-candidate evidence must exercise commit-reveal enabled;
- weight evidence must distinguish `COMMITTED`, `REVEALED/APPLIED`, and `READ_BACK` states.

---

## 7. Tempo and staleness interact with validator economics

`tempo` defines the subnet epoch length. Current Bittensor also uses `activity_cutoff_factor` to derive the effective validator inactivity window as a tempo-relative value.

Consequent therefore has two different notions of staleness:

```text
Bittensor staleness
  validator has not refreshed chain weights within the activity window

Consequent evidence staleness
  miner quality evidence is too old to justify current economic weight
```

Our evidence-staleness policy must be stricter when necessary. A validator can remain chain-active while still using dangerously stale miner evidence.

Weight scheduling should satisfy:

```text
fresh-enough evaluation cadence
≤ legal weight/commit cadence
< effective chain activity cutoff
```

and should be recomputed whenever tempo or related hyperparameters change.

---

## 8. Live economic parameters Consequent must observe

Weight submission:
- `min_allowed_weights`;
- `max_weights_limit`;
- `weights_version`;
- `weights_rate_limit`;
- `commit_reveal_weights_enabled`;
- `commit_reveal_period`.

Consensus/validator economics:
- `tempo`;
- `kappa`;
- `max_validators`;
- `activity_cutoff_factor`;
- `bonds_moving_avg`;
- `bonds_penalty`;
- `yuma3_enabled`;
- `liquid_alpha_enabled`.

Never freeze current defaults into protocol truth. Read live values and attach them to evidence records.

---

## 9. Yuma3 and liquid alpha are mechanism-version state

A subnet may run classic Yuma or Yuma3. Yuma3 changes bond storage/computation and validator-dividend calculation. Liquid alpha only takes effect when Yuma3 is enabled.

Consequent does not need to reproduce the complete chain implementation internally, but every economic evidence bundle must capture the consensus variant and relevant bond parameters active during the run.

Changing Yuma variant or bond policy should be treated as an economic environment change, similar to changing an evaluator major version.

---

## 10. Subnet-level demand matters

Inside Consequent, miners compete for miner incentive.

Outside Consequent, the subnet competes for Bittensor-wide economic demand. Current Bittensor emission allocation uses subnet alpha-price demand signals, moving-price state, miner-burn adjustment, and an emission gate before subnet TAO shares are distributed.

Therefore there are two product-market questions:

```text
Internal market:
Which memory-formation algorithm deserves Consequent miner emissions?

External market:
Why should capital/users value Consequent enough for the subnet to sustain meaningful emissions?
```

A perfect evaluator with no external consumer demand is not a durable subnet.

M3 consumer integration is therefore an economic milestone, not merely an SDK milestone.

---

## 11. Consequent economic invariants

### E1 — validator eligibility
Only economically active validator rows count as subnet evidence.

### E2 — independent evidence
Validators should independently measure quality; peer consensus is an output, not an input to the current evaluation.

### E3 — correlated ordering
Independent private evaluations should converge statistically on true miner quality.

### E4 — hidden active weights
Production-like weight publication uses commit-reveal when the subnet enables it.

### E5 — fresh evidence
A miner cannot retain meaningful economic weight indefinitely from stale historical success.

### E6 — non-compensable safety
Policy violations remain hard vetoes regardless of Yuma support or average uplift.

### E7 — no benchmark monopoly
No single static hidden dataset should define the commodity.

### E8 — chain environment captured
Every economic result records the live consensus/weight hyperparameters that governed it.

---

## 12. Next experiments

### Y1 — reference Yuma model
Implement a small, explicitly non-consensus reference model that reproduces documented stake-weighted consensus, clipping, rank, and incentive examples. Use it for mechanism tests only.

### Y2 — three-validator independent-seed simulation
Three validators score the six controlled miners from independent private holdouts. Require useful-generalizing top agreement and policy-veto agreement while allowing bounded score dispersion.

### Y3 — noisy-validator pressure
Inject one noisy/contrarian validator at minority stake. Verify useful miners retain sufficient consensus support and exaggerated weights are clipped.

### Y4 — malicious-stake threshold
Sweep malicious validator stake around `kappa` and measure where consensus control changes. This is a mechanism boundary, not something Consequent can locally "fix" after majority economic control is achieved.

### Y5 — chain-local multi-validator
Register multiple validator hotkeys with meaningful permitted state, submit independently derived rows, and inspect actual epoch consensus/incentive/bond outputs.

### Y6 — commit-reveal proof
Run production-like weight commits with commit-reveal enabled and capture commit → reveal/application → epoch settlement evidence.

---

## Sources

Current Bittensor documentation consulted 2026-08-26:
- https://www.bittensor.com/docs/concepts/emissions
- https://www.bittensor.com/docs/hyperparameters/max-validators
- https://www.bittensor.com/docs/hyperparameters/commit-reveal-weights-enabled
- https://www.bittensor.com/docs/hyperparameters/commit-reveal-period
- https://www.bittensor.com/docs/hyperparameters/weights-rate-limit
- https://www.bittensor.com/docs/hyperparameters/activity-cutoff-factor
- https://www.bittensor.com/docs/hyperparameters/yuma3-enabled
- https://www.bittensor.com/docs/hyperparameters/bonds-penalty

Current chain state always overrides documented defaults.

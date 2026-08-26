# EBI Status — Consequent

**Current:** `M1_CLOSED / CHAIN_LOCAL_COMPETITIVE_ECONOMIC_LOOP_PASS / M2_ACTIVE`

Canonical build authority:
1. `/GROUND_TRUTH.md`
2. `/audits.md`
3. `/skills/README.md`
4. `/architecture/README.md`

Mechanism oracle: LOCAL_PASS.
Category boundary: FROZEN_v0.1.
Bittensor 11 architecture: truth-corrected 2026-08-24.
Toolchain evidence: CI_PASS — `bittensor==11.1.0` installs and the Consequent package/test suite passes on Python 3.10 and 3.12.

## M0 closure

Authoritative M0 run: GitHub Actions localnet run `32770499057` / run #34.

M0 proved one strict fresh-chain economic loop:

`registration → ServeAxon → metagraph discovery → signed BMP formation → live rate-limit compliance → SetWeights → chain read-back`

Final state: `LOCALNET_SET_WEIGHTS_READBACK_PASS`.

## M1 closure

Authoritative M1 run: GitHub Actions `m1-localnet` run `32906478860` / run #1 on head `42060c3f49ea0db5b6d7af41e4da39bb1db80936`.

The fresh-chain competitive topology completed successfully:
- fresh official Subtensor localnet: PASS;
- subnet registration/activation: PASS — netuid 2;
- owner/economic signer registered as UID 0;
- six independent miner wallets/hotkeys funded and burned-registered: PASS — UIDs 1–6;
- six independent authenticated FastAPI miner processes: PASS — ports 8091–8096;
- six `ServeAxon` publications: PASS — chain extrinsics `43-0006`, `46-0006`, `49-0006`, `52-0006`, `55-0006`, `58-0006`;
- metagraph-only discovery: PASS — exactly six served miners discovered from UIDs 1–6;
- signed challenge fan-out: PASS;
- concealed paired A0/A1 evaluation: PASS;
- policy/regression gates: PASS;
- live `weights_rate_limit=100` respected: PASS — initial remaining wait 60 blocks, legal submission block 123;
- competitive `SetWeights`: PASS — extrinsic `124-0006`;
- chain read-back of positive competitive weights: PASS;
- evidence artifact: PASS — `consequent-m1-localnet-evidence`, artifact ID `9585670375`, digest `sha256:a55dbe1b34eafc0295e3c0398cec92b89039b181ea9e6d816ba609dbc6bb3b2b`.

Final runner state: `M1_CHAIN_COMPETITION_PASS`.

### Controlled M1 economic ordering

Observed computed weights:
- UID 4 / `useful_generalizing_memory`: `0.6746805888`;
- UID 3 / `overfit_memory`: `0.3253194112`;
- UID 1 / `no_memory`: `0`;
- UID 2 / `irrelevant_memory`: `0`;
- UID 5 / `harmful_memory`: `0`;
- UID 6 / `policy_violating_memory`: `0`, hard-vetoed with 2 policy violations.

Observed chain positive weights after quantization/read-back:
- UID 4: `0.6746795697`;
- UID 3: `0.3253204303`.

All required M1 checks passed:
- useful beats overfit;
- overfit beats no-memory;
- no-memory not rewarded;
- irrelevant memory not rewarded;
- harmful memory not rewarded;
- policy-violating memory hard-vetoed;
- useful memory has top weight;
- weights normalized.

This closes M1. Consequent has now proven a six-miner competitive chain-local economic loop, not merely a component pressure test.

## Important evidence boundary

M1 closure does **not** mean:
- multiple independent validators have converged on the same miner ranking;
- production commit-reveal behavior has been exercised end-to-end without disabling visibility delay;
- copied-response, leakage, provenance-forgery, collusion, churn or evaluator-drift attacks are closed;
- Bittensor public testnet mutation/deployment has occurred;
- a consumer runtime has integrated the BMP lifecycle;
- production demand has been demonstrated.

## Next canonical gate — M2 adversarial mechanism pressure

Pressure the rewarded commodity and validator truth against:
1. source-instance memorization and benchmark leakage;
2. copied/collusive miner responses;
3. provenance forgery;
4. capability smuggling;
5. malformed/oversized BMPs;
6. catastrophic regressions hidden by positive mean uplift;
7. policy violations with compensating uplift;
8. stale winners, downtime and miner churn;
9. score jumps/random audit triggers;
10. evaluator-version drift and private-seed variance;
11. validator copying/collusion;
12. miner-validator collusion.

M2 exit condition: no unresolved CRITICAL finding and no unbounded HIGH finding in the Adversary Foundry, with reproducible evidence for every closed attack.

Public Bittensor testnet mutations remain `NOT_RUN` and must not be inferred from chain-local evidence.

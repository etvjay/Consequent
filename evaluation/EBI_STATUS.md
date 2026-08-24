# EBI Status — Consequent

**Current:** `M0_CLOSED / CHAIN_LOCAL_ECONOMIC_LOOP_PASS`

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

Authoritative run: GitHub Actions localnet run `32770499057` / run #34 on head `d028172571baf2c3b776460069e617dc9b92b7f6`.

The strict fresh-chain job completed successfully end-to-end:
- fresh official Subtensor localnet with production-like block timing: PASS;
- disposable owner/validator/miner wallets funded: PASS;
- subnet registration and activation: PASS — netuid 2;
- validator burned/collateral registration: PASS — UID 1;
- miner burned/collateral registration: PASS — UID 2;
- metagraph registration assertions: PASS;
- authenticated miner HTTP process: PASS;
- non-loopback chain-valid endpoint: PASS;
- `bt.ServeAxon`: PASS — `AxonServed`, extrinsic `18-0006`;
- validator metagraph discovery: PASS — miner UID 2 discovered from chain-published endpoint;
- signed validator → miner btauth/1 BMP round trip: PASS — `LOCAL_NETWORK_AUTH_ROUNDTRIP_PASS`;
- live weight-policy read: PASS;
- runtime-owned `weights_rate_limit=100` respected: PASS — initial wait 87 blocks, legal submission block 110;
- `bt.SetWeights`: PASS — extrinsic `111-0006`;
- chain read-back: PASS — validator UID 0 → miner UID 2, target weight `1.0`;
- evidence artifact upload: PASS — `consequent-localnet-evidence`.

Final SetWeights evidence state emitted by the runner: `LOCALNET_SET_WEIGHTS_READBACK_PASS`.

This closes M0. No component-only or simulated evidence is being used to make that claim; the closure is based on a strict fresh-chain lifecycle plus accepted economic settlement and read-back.

## Existing supporting evidence

- mechanism/unit suite: CI_PASS;
- real btauth cryptographic signing/verification + replay/tamper rejection: CI_PASS;
- signed FastAPI request with metagraph-backed caller authorization: LOCAL_NETWORK_COMPONENT_PASS;
- six independent Uvicorn miner processes over real sockets + concealed scoring/weights: LOCAL_NETWORK_COMPONENT_PASS;
- Bittensor `test` network connectivity/read: READ_ONLY_TESTNET_PASS.

## Important evidence boundary

M0 closure does **not** mean:
- six independent chain-registered miners have competed together;
- multiple validators have independently scored the same miner population;
- commit-reveal production behavior has been exercised end-to-end;
- Bittensor public testnet mutation/deployment has occurred;
- production demand has been demonstrated.

Those remain later gates.

## Next canonical gate — M1

Build a competitive chain-local Consequent subnet:

1. register six independent miner hotkeys;
2. run six independent miner HTTP processes with distinct strategy archetypes;
3. publish six endpoints through `ServeAxon`;
4. discover all miners from the metagraph;
5. issue concealed source-history challenges;
6. collect six BMPs over signed HTTP;
7. evaluate paired A0/A1 holdouts;
8. apply policy/regression vetoes;
9. map scores to UIDs;
10. submit competitive weights and read them back from chain.

Required qualitative ordering for the controlled M1 pressure topology:

`useful_generalizing > overfit > no_memory`, while `irrelevant`, `harmful`, and `policy_violating` receive zero economic weight under the defined fixture.

Only after M1 and adversarial pressure gates pass should Consequent perform funded Bittensor `test` mutations.

No local, chain-local, CI, or read-only testnet result may be presented as deployed public-testnet evidence.

# Consequent — Bittensor Testnet Runbook

Status: `PRE_EXECUTION`
Authority: `/GROUND_TRUTH.md` → `/audits.md` → this runbook
Verified against current Bittensor v11 documentation: 2026-08-24

This runbook starts from Consequent's `LOCAL_NETWORK_PASS` state and takes the project to real Bittensor testnet evidence without conflating local CI with chain execution.

## Safety rules

1. Use Bittensor `test`, never `finney`, while following this runbook.
2. Never commit mnemonics, seeds, wallet files, passwords, or private keys.
3. Every mutation is planned/dry-run first.
4. Record the actual netuid from testnet; netuids are not portable across networks.
5. Do not call a local/CI HTTP test a testnet miner.
6. A miner is testnet-proven only after its registered hotkey/UID and published endpoint are visible in the testnet metagraph.
7. A validator is testnet-proven only after it can query registered miners, evaluate them, and successfully submit/read back weights subject to current subnet rules.

## 1. Install and pin

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e '.[dev]'
python -c 'import bittensor as bt; print(bt.__version__)'
btcli --version
```

Consequent currently targets `bittensor>=11.1,<12`; CI has verified 11.1.0 on Python 3.10 and 3.12.

## 2. Create operator wallets

Use separate wallets for the validator and each miner role. For an initial testnet proof:

```bash
btcli wallet create -w consequent-validator -H default
btcli wallet create -w consequent-miner-0 -H default
btcli wallet create -w consequent-miner-1 -H default
btcli wallet list
```

For the full pressure topology, add more miner wallets later. The six-miner local harness is an internal falsification target, not a published HackQuest minimum.

Back up wallet recovery material offline. Do not paste it into issues, Actions logs, `.env` files committed to Git, or chat transcripts.

## 3. Configure testnet explicitly

```bash
btcli config set network test
btcli config get
```

Or keep `-n test` on every command. Explicit network flags are preferable during first deployment.

For Consequent scripts:

```bash
export CONSEQUENT_NETWORK_MODE=1
export CONSEQUENT_BT_NETWORK=test
export CONSEQUENT_NETUID='<TESTNET_NETUID>'
export CONSEQUENT_WALLET='consequent-validator'
export CONSEQUENT_HOTKEY='default'
```

If wallets live outside the standard directory:

```bash
export CONSEQUENT_WALLET_PATH='/path/to/wallet/root'
```

## 4. Funding boundary

A real Bittensor network does not expose the local development faucet. Testnet operations require funded testnet accounts/test TAO.

Before any registration:

```bash
btcli wallet balance consequent-validator -n test
btcli wallet balance consequent-miner-0 -n test
```

Do not proceed until the relevant coldkeys can pay registration/transaction costs.

## 5. Choose the testnet subnet path

Consequent requires a subnet whose incentive mechanism we control for final proof. Do not assume a mainnet netuid exists on testnet.

Inspect current testnet state:

```bash
btcli subnets list -n test
```

If using an existing organizer-provided/hackathon subnet, record its testnet netuid and ownership/permission model in `/audits.md`.

If creating our own testnet subnet, inspect the current subnet-registration cost first:

```bash
btcli query subnet-registration-cost -n test --json
btcli tx register-subnet -w <owner-wallet> -n test --dry-run
```

Only execute after reviewing the dry run and confirming the testnet funding model:

```bash
btcli tx register-subnet -w <owner-wallet> -n test
```

Then record the resulting netuid. If activation/start-call is required for the selected path, dry-run and execute it according to current Bittensor output and owner permissions.

## 6. Inspect target subnet before neuron registration

```bash
btcli query subnet-hyperparameters --netuid "$CONSEQUENT_NETUID" -n test --json
btcli query metagraph --netuid "$CONSEQUENT_NETUID" -n test --json
btcli query burn --netuid "$CONSEQUENT_NETUID" -n test --json
```

The validator implementation must respect live weight constraints rather than hard-coded assumptions.

## 7. Register validator and miners — dry run first

For each neuron wallet:

```bash
btcli tx burned-register \
  --netuid "$CONSEQUENT_NETUID" \
  -w consequent-validator \
  -H default \
  -n test \
  --dry-run
```

Review the plan, then execute only deliberately:

```bash
btcli tx burned-register \
  --netuid "$CONSEQUENT_NETUID" \
  -w consequent-validator \
  -H default \
  -n test
```

Repeat for miner wallets.

Confirm registration from chain state:

```bash
btcli query metagraph --netuid "$CONSEQUENT_NETUID" -n test --json
btcli query uid --netuid "$CONSEQUENT_NETUID" -H default -w consequent-validator -n test
```

Exact CLI query arguments should be confirmed with `btcli query uid --help` if the local 11.x patch release changes presentation. The canonical evidence is the metagraph record itself.

## 8. Run the Consequent read-only preflight

Configure one neuron role at a time:

```bash
export CONSEQUENT_WALLET='consequent-miner-0'
export CONSEQUENT_HOTKEY='default'
python scripts/testnet_preflight.py
```

Expected evidence:

- network = `test`;
- correct netuid;
- registered = true;
- UID/hotkey match the intended wallet;
- current validator permit/stake state is visible;
- current weight-policy fields are read successfully.

If `registered` is false, stop. Do not attempt `ServeAxon` or `SetWeights`.

## 9. Launch miner HTTP service

A testnet miner needs a publicly reachable HTTP endpoint. Run Consequent with network auth enabled:

```bash
export CONSEQUENT_NETWORK_MODE=1
export CONSEQUENT_BT_NETWORK=test
export CONSEQUENT_NETUID='<TESTNET_NETUID>'
export CONSEQUENT_WALLET='consequent-miner-0'
export CONSEQUENT_HOTKEY='default'
export CONSEQUENT_MINER_STRATEGY='useful_generalizing_memory'
export CONSEQUENT_ADVERTISED_IP='<PUBLIC_IP>'
export CONSEQUENT_ADVERTISED_PORT='8091'

python -m uvicorn miner.app:app --host 0.0.0.0 --port 8091
```

Network mode is fail-closed: unsigned requests are rejected and signed callers must pass metagraph policy.

Before publishing the endpoint, verify `/health` is reachable from outside the miner host.

## 10. Plan and publish `ServeAxon`

Plan only:

```bash
python scripts/testnet_preflight.py --plan-serve
python scripts/serve_axon.py
```

Review the Bittensor transaction plan. Nothing should be submitted without `--execute`.

Then, when the endpoint is confirmed reachable and the hotkey is registered:

```bash
python scripts/serve_axon.py --execute
```

After inclusion, confirm the miner's metagraph record contains the expected `axon` endpoint:

```bash
btcli query metagraph --netuid "$CONSEQUENT_NETUID" -n test --json
```

Capture the UID, hotkey, endpoint, transaction result/block context, and timestamp in the evidence ledger.

## 11. Validator discovery and signed request

Switch the environment to the validator wallet:

```bash
export CONSEQUENT_WALLET='consequent-validator'
export CONSEQUENT_HOTKEY='default'
```

The validator must derive miner UID/hotkey/endpoint from testnet metagraph state, not from a hand-maintained endpoint list.

A testnet evidence run must prove:

1. metagraph discovery finds the registered miner;
2. validator signs the exact HTTP request using its hotkey;
3. miner verifies receiver/path/body/nonce/signature;
4. miner authorizes the caller using current metagraph state;
5. miner returns a valid BMP;
6. concealed validator evaluation produces a score.

## 12. Validator permit boundary

Consequent's network policy defaults to requiring `validator_permit=true` for callers. If the new testnet validator does not yet have a permit, do **not** silently disable this in production code just to make the demo work.

Instead, document the testnet subnet's actual validator-permit rules and choose one explicit route:

- configure the test subnet so the validator can legitimately obtain the permit;
- use an organizer-provided validator path;
- for a bounded bootstrap-only test, explicitly configure `CONSEQUENT_REQUIRE_VALIDATOR_PERMIT=0`, record that deviation in `/audits.md`, and do not present it as final security posture.

Final submission evidence should use the strongest available legitimate policy.

## 13. Plan weights against live policy

Create a score file keyed by real miner UID:

```json
{
  "3": 0.63,
  "4": 0.31,
  "5": 0.0
}
```

Then:

```bash
python scripts/plan_weights.py scores.json --version-key '<CURRENT_VERSION_KEY>'
```

The script reads current subnet hyperparameters before constructing the `SetWeights` plan. It refuses a version key below the live `weights_version` gate.

Before executing weights, confirm:

- validator is registered;
- validator has weight-setting permission/permit as required;
- effective `min_allowed_weights` is satisfied;
- max-weight clipping is acceptable;
- weights rate limit permits the call;
- current `weights_version` is met;
- commit-reveal status is understood.

## 14. Execute weights only after M0.5 evidence is complete

`validator.weights.submit_weights()` exists, but the repository intentionally does not provide a casual one-line execute script yet. The first testnet weight mutation should be performed as a controlled evidence run after its plan is archived.

Required evidence:

- live policy snapshot;
- planned weight vector;
- validator UID/hotkey;
- transaction result;
- block/timestamp;
- weights read back from chain/metagraph.

Only then promote the audit item to `TESTNET_PASS`.

## 15. Evidence names

Use these states exactly:

- `LOCAL_PASS` — deterministic in-process mechanism evidence;
- `CI_PASS` — package/runtime tests in GitHub Actions;
- `LOCAL_NETWORK_PASS` — real local HTTP processes/hotkeys, no live chain mutation;
- `TESTNET_PASS` — actual Bittensor test network state/transactions;
- `LIVE_PASS` / `PRODUCTION_PASS` — not required for the hackathon and must not be inferred from testnet.

## Current boundary

As of the creation of this runbook, Consequent has `LOCAL_NETWORK_PASS` and **does not yet have testnet registration, ServeAxon publication, or SetWeights evidence**.

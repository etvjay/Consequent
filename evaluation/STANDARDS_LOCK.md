# Standards Lock — 2026-08-24

Implementation target: Bittensor 11.1.x.

Locked interfaces:
- plain HTTP validator/miner data plane;
- `bittensor.http_auth.sign` / `verify` (`btauth/1`);
- own Pydantic request/response schemas;
- FastAPI miner server and httpx validator client;
- metagraph hotkey/endpoint discovery;
- `bt.SetWeights` intent;
- live conformance to minimum weight count, maximum weight, rate limit, version key and commit-reveal settings.

Do not reintroduce legacy `bt.Axon`, `bt.Dendrite`, `bt.Synapse`, `StreamingSynapse`, or v10 headers into canonical architecture.

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Request

from consequent.models import MemoryFormationRequest, MemoryFormationResponse
from consequent.network import NetworkSettings
from consequent.strategies import form_patch
from miner.auth import verify_bittensor_request
from miner.policy import authorize_caller

app = FastAPI(title="Consequent Miner", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "consequent-miner"}


async def _load_metagraph(settings: NetworkSettings):
    import bittensor as bt

    assert settings.netuid is not None
    async with bt.Subtensor(network=settings.network) as client:
        return await client.subnets.metagraph(netuid=settings.netuid)


async def _authenticate_network_request(request: Request, body: bytes, settings: NetworkSettings) -> None:
    if not settings.network_mode:
        return

    wallet = settings.wallet()
    self_hotkey_ss58 = wallet.hotkey.ss58_address

    target = request.scope["raw_path"].decode()
    if request.scope["query_string"]:
        target += "?" + request.scope["query_string"].decode()

    try:
        caller = verify_bittensor_request(
            request.headers,
            body,
            method=request.method,
            path=target,
            self_hotkey_ss58=self_hotkey_ss58,
        )
    except Exception as exc:
        raise HTTPException(status_code=401, detail="invalid Bittensor request authentication") from exc

    caller_hotkey = getattr(caller, "hotkey_ss58", None)
    if not caller_hotkey:
        raise HTTPException(status_code=401, detail="authenticated caller hotkey missing")

    try:
        metagraph = await _load_metagraph(settings)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="unable to load Bittensor metagraph") from exc

    decision = authorize_caller(
        caller_hotkey=caller_hotkey,
        metagraph=metagraph,
        settings=settings,
    )
    if not decision.allowed:
        raise HTTPException(status_code=403, detail=decision.reason)


@app.post("/v1/memory/formation", response_model=MemoryFormationResponse)
async def form_memory(request: Request) -> MemoryFormationResponse:
    body = await request.body()

    try:
        settings = NetworkSettings.from_env()
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    await _authenticate_network_request(request, body, settings)

    try:
        payload = MemoryFormationRequest.model_validate_json(body)
    except Exception as exc:
        raise HTTPException(status_code=422, detail="invalid memory formation request") from exc

    strategy = os.environ.get("CONSEQUENT_MINER_STRATEGY", "useful_generalizing_memory")
    return MemoryFormationResponse(
        challenge_id=payload.challenge_id,
        patch=form_patch(payload, strategy),
    )

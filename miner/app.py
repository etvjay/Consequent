from __future__ import annotations

import os
from fastapi import FastAPI, HTTPException, Request
from consequent.models import MemoryFormationRequest, MemoryFormationResponse
from consequent.strategies import form_patch
from miner.auth import verify_bittensor_request

app = FastAPI(title="Consequent Miner", version="0.1.0")

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "consequent-miner"}

@app.post("/v1/memory/formation", response_model=MemoryFormationResponse)
async def form_memory(request: Request) -> MemoryFormationResponse:
    body = await request.body()
    hotkey = os.environ.get("CONSEQUENT_HOTKEY_SS58")
    if hotkey:
        target = request.scope["raw_path"].decode()
        if request.scope["query_string"]:
            target += "?" + request.scope["query_string"].decode()
        try:
            verify_bittensor_request(request.headers, body, method=request.method, path=target, self_hotkey_ss58=hotkey)
        except Exception as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
    payload = MemoryFormationRequest.model_validate_json(body)
    strategy = os.environ.get("CONSEQUENT_MINER_STRATEGY", "useful_generalizing_memory")
    return MemoryFormationResponse(challenge_id=payload.challenge_id, patch=form_patch(payload, strategy))

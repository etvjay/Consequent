from __future__ import annotations
import httpx
from consequent.models import MemoryFormationRequest, MemoryFormationResponse
from validator.auth import HotkeyAuth

async def query_miner(*, wallet, endpoint: str, miner_hotkey: str, challenge: MemoryFormationRequest, timeout: float = 15.0) -> MemoryFormationResponse:
    body = challenge.model_dump_json().encode()
    async with httpx.AsyncClient(base_url=f"http://{endpoint}", timeout=timeout) as client:
        response = await client.post("/v1/memory/formation", content=body, headers={"content-type": "application/json"}, auth=HotkeyAuth(wallet, receiver_ss58=miner_hotkey))
        response.raise_for_status()
        return MemoryFormationResponse.model_validate(response.json())

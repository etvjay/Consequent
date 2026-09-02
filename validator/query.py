from __future__ import annotations
import httpx
from consequent.models import MemoryFormationRequest, MemoryFormationResponse
from validator.auth import HotkeyAuth

async def query_miner(*, wallet, endpoint: str, miner_hotkey: str, challenge: MemoryFormationRequest, timeout: float = 15.0) -> MemoryFormationResponse:
    body = challenge.model_dump_json().encode()
    # Miner endpoints are discovered from chain state and should be reached
    # directly. Ignoring ambient proxy variables keeps signed local/testnet
    # traffic deterministic and prevents an unsupported SOCKS proxy from
    # changing authentication or making loopback miners unreachable.
    async with httpx.AsyncClient(base_url=f"http://{endpoint}", timeout=timeout, trust_env=False) as client:
        response = await client.post("/v1/memory/formation", content=body, headers={"content-type": "application/json"}, auth=HotkeyAuth(wallet, receiver_ss58=miner_hotkey))
        response.raise_for_status()
        return MemoryFormationResponse.model_validate(response.json())

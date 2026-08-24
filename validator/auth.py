from __future__ import annotations
import httpx

class HotkeyAuth(httpx.Auth):
    requires_request_body = True
    def __init__(self, wallet, receiver_ss58: str):
        self.wallet = wallet
        self.receiver_ss58 = receiver_ss58
    def auth_flow(self, request):
        import bittensor as bt
        request.headers.update(bt.http_auth.sign(self.wallet, method=request.method, path=request.url.raw_path.decode(), body=request.content, receiver_ss58=self.receiver_ss58))
        yield request

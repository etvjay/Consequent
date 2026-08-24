from __future__ import annotations


def verify_bittensor_request(headers, body: bytes, *, method: str, path: str, self_hotkey_ss58: str):
    import bittensor as bt
    return bt.http_auth.verify(headers, body, method=method, path=path, self_hotkey_ss58=self_hotkey_ss58)

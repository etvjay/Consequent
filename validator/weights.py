from __future__ import annotations
from consequent.scoring import normalized_weights

def build_weight_map(scores_by_uid: dict[int, float]) -> dict[int, float]:
    return normalized_weights(scores_by_uid)

async def submit_weights(*, client, wallet, netuid: int, weights: dict[int, float], version_key: int | None = None):
    import bittensor as bt
    kwargs = {"netuid": netuid, "weights": weights}
    if version_key is not None:
        kwargs["version_key"] = version_key
    return await client.execute(bt.SetWeights(**kwargs), wallet)

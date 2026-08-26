from __future__ import annotations

from dataclasses import dataclass

import pytest

from validator.discovery import discover_miners


@dataclass
class FakeNeuron:
    uid: int
    hotkey: str
    axon: str | None


class FakeMetagraph(list):
    pass


class SnapshotSubnets:
    def __init__(self, snapshots):
        self._snapshots = iter(snapshots)

    async def metagraph(self, *, netuid: int):
        assert netuid == 42
        return next(self._snapshots)


class FakeClient:
    def __init__(self, snapshots):
        self.subnets = SnapshotSubnets(snapshots)


@pytest.mark.asyncio
async def test_discovery_refreshes_same_hotkey_to_new_chain_endpoint():
    client = FakeClient(
        [
            FakeMetagraph([FakeNeuron(7, "hk-miner", "10.0.0.1:8091")]),
            FakeMetagraph([FakeNeuron(7, "hk-miner", "10.0.0.1:9191")]),
        ]
    )

    first = await discover_miners(client=client, netuid=42)
    second = await discover_miners(client=client, netuid=42)

    assert first[0].uid == second[0].uid == 7
    assert first[0].hotkey == second[0].hotkey == "hk-miner"
    assert first[0].endpoint == "10.0.0.1:8091"
    assert second[0].endpoint == "10.0.0.1:9191"


@pytest.mark.asyncio
async def test_discovery_removes_unserved_miner_on_next_snapshot():
    client = FakeClient(
        [
            FakeMetagraph([FakeNeuron(7, "hk-miner", "10.0.0.1:8091")]),
            FakeMetagraph([FakeNeuron(7, "hk-miner", None)]),
        ]
    )

    assert len(await discover_miners(client=client, netuid=42)) == 1
    assert await discover_miners(client=client, netuid=42) == []


@pytest.mark.asyncio
async def test_discovery_exposes_uid_reuse_as_new_hotkey_identity():
    client = FakeClient(
        [
            FakeMetagraph([FakeNeuron(7, "hk-old", "10.0.0.1:8091")]),
            FakeMetagraph([FakeNeuron(7, "hk-new", "10.0.0.1:8092")]),
        ]
    )

    first = await discover_miners(client=client, netuid=42)
    second = await discover_miners(client=client, netuid=42)

    assert first[0].uid == second[0].uid == 7
    assert first[0].hotkey == "hk-old"
    assert second[0].hotkey == "hk-new"
    assert first[0].hotkey != second[0].hotkey

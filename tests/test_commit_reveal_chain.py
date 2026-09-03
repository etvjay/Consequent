from __future__ import annotations

from types import SimpleNamespace

from scripts.m2_commit_reveal_chain import _plan_payload, _row


def test_commit_reveal_row_normalizes_rpc_uid_keys():
    assert _row({3: {"7": "0.75", 8: 0.25}}, 3) == {7: 0.75, 8: 0.25}


def test_commit_reveal_plan_payload_preserves_preview_and_extras():
    plan = SimpleNamespace(
        extras={"reveal_round": 123},
        to_dict=lambda: {"op": "set_weights", "ok": True},
    )
    assert _plan_payload(plan) == {
        "op": "set_weights",
        "ok": True,
        "extras": {"reveal_round": 123},
    }

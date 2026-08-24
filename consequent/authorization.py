from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CallerPolicy:
    require_validator_permit: bool = True
    min_tao_stake: float = 0.0


@dataclass(frozen=True)
class CallerDecision:
    allowed: bool
    reason: str
    uid: int | None = None
    hotkey: str | None = None


def authorize_caller(metagraph: Any, hotkey_ss58: str, policy: CallerPolicy) -> CallerDecision:
    try:
        neuron = metagraph.by_hotkey(hotkey_ss58)
    except Exception:
        return CallerDecision(False, "caller_not_registered", hotkey=hotkey_ss58)

    if neuron is None:
        return CallerDecision(False, "caller_not_registered", hotkey=hotkey_ss58)

    if policy.require_validator_permit and not bool(getattr(neuron, "validator_permit", False)):
        return CallerDecision(False, "validator_permit_required", uid=int(neuron.uid), hotkey=hotkey_ss58)

    if policy.min_tao_stake > 0:
        stake = getattr(neuron, "stake", None)
        tao_value = float(getattr(stake, "tao", stake or 0.0))
        if tao_value < policy.min_tao_stake:
            return CallerDecision(False, "minimum_stake_not_met", uid=int(neuron.uid), hotkey=hotkey_ss58)

    return CallerDecision(True, "authorized", uid=int(neuron.uid), hotkey=hotkey_ss58)

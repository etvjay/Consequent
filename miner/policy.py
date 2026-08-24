from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from consequent.network import NetworkSettings, neuron_by_hotkey


@dataclass(frozen=True)
class CallerDecision:
    allowed: bool
    reason: str
    uid: int | None = None


def _tao_stake(neuron: Any) -> float:
    """Best-effort conversion of Bittensor stake wrappers to a TAO float."""
    stake = getattr(neuron, "stake", 0.0)
    if hasattr(stake, "tao"):
        return float(stake.tao)
    try:
        return float(stake)
    except (TypeError, ValueError):
        return 0.0


def authorize_caller(*, caller_hotkey: str, metagraph: Any, settings: NetworkSettings) -> CallerDecision:
    try:
        neuron = neuron_by_hotkey(metagraph, caller_hotkey)
    except Exception:
        return CallerDecision(False, "caller hotkey is not registered on this subnet")

    if neuron is None:
        return CallerDecision(False, "caller hotkey is not registered on this subnet")

    if settings.require_validator_permit and not bool(getattr(neuron, "validator_permit", False)):
        return CallerDecision(False, "caller does not have validator permit", uid=int(neuron.uid))

    if settings.min_validator_tao_stake > 0:
        stake = _tao_stake(neuron)
        if stake < settings.min_validator_tao_stake:
            return CallerDecision(
                False,
                f"caller stake {stake} is below required {settings.min_validator_tao_stake}",
                uid=int(neuron.uid),
            )

    return CallerDecision(True, "authorized", uid=int(neuron.uid))

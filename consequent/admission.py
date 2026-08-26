from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

from consequent.models import BehavioralMemoryPatch, MemoryFormationRequest

_ACTION_TOKEN = re.compile(r"^[a-z][a-z0-9_:-]{0,127}$")
_CONDITION_KEY = re.compile(r"^[a-zA-Z][a-zA-Z0-9_.:-]{0,127}$")
_MAX_CONDITION_STRING = 256
_DEFAULT_MAX_PATCH_BYTES = 16_384


@dataclass(frozen=True)
class AdmissionResult:
    accepted: bool
    reasons: tuple[str, ...]
    patch_digest: str


def _canonical_semantic_payload(patch: BehavioralMemoryPatch) -> dict[str, Any]:
    """Canonical behavior-bearing patch representation.

    Miner self-labels are intentionally excluded. Two miners returning the same
    behavioral rules should have the same semantic digest; Consequent does not
    reward novelty, but duplicate output is useful as an audit/collusion signal.
    """
    rules = [rule.model_dump(mode="json") for rule in patch.rules]
    rules.sort(key=lambda item: (str(item.get("rule_id", "")), json.dumps(item, sort_keys=True, separators=(",", ":"))))
    return {
        "patch_version": patch.patch_version,
        "rules": rules,
    }


def semantic_patch_digest(patch: BehavioralMemoryPatch) -> str:
    raw = json.dumps(
        _canonical_semantic_payload(patch),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _safe_condition_value(value: Any) -> bool:
    if value is None or isinstance(value, (bool, int, float)):
        return True
    if isinstance(value, str):
        if len(value) > _MAX_CONDITION_STRING:
            return False
        if any(ch in value for ch in ("\n", "\r", "\x00", "```")):
            return False
        return True
    return False


def admit_patch(
    request: MemoryFormationRequest,
    patch: BehavioralMemoryPatch,
    *,
    max_serialized_bytes: int = _DEFAULT_MAX_PATCH_BYTES,
) -> AdmissionResult:
    """Apply non-semantic protocol admission before any causal scoring.

    Admission is deliberately conservative. It checks whether the miner returned
    a bounded, provenance-linked, declarative BMP. It does *not* judge whether
    the memory is useful; that remains the concealed paired evaluator's job.
    """
    reasons: list[str] = []
    digest = semantic_patch_digest(patch)

    if patch.patch_version != "bmp/0.1":
        reasons.append("unsupported_patch_version")

    if len(patch.rules) > request.memory_budget:
        reasons.append("memory_budget_exceeded")

    serialized = patch.model_dump_json().encode("utf-8")
    if len(serialized) > int(max_serialized_bytes):
        reasons.append("serialized_patch_too_large")

    episode_by_id = {episode.episode_id: episode for episode in request.episodes}
    if len(episode_by_id) != len(request.episodes):
        reasons.append("ambiguous_source_episode_ids")

    seen_rule_ids: set[str] = set()
    for rule in patch.rules:
        if rule.rule_id in seen_rule_ids:
            reasons.append(f"duplicate_rule_id:{rule.rule_id}")
        seen_rule_ids.add(rule.rule_id)

        if not _ACTION_TOKEN.fullmatch(rule.action):
            reasons.append(f"non_declarative_action:{rule.rule_id}")

        if not rule.provenance:
            reasons.append(f"missing_provenance:{rule.rule_id}")
        for source_id in rule.provenance:
            source = episode_by_id.get(source_id)
            if source is None:
                reasons.append(f"unknown_provenance:{rule.rule_id}:{source_id}")
                continue
            if source.family != rule.family:
                reasons.append(f"provenance_family_mismatch:{rule.rule_id}:{source_id}")

        for key, value in rule.conditions.items():
            if not isinstance(key, str) or not _CONDITION_KEY.fullmatch(key):
                reasons.append(f"unsafe_condition_key:{rule.rule_id}")
                continue
            if not _safe_condition_value(value):
                reasons.append(f"unsafe_condition_value:{rule.rule_id}:{key}")

    # Stable order makes evidence comparison deterministic while preserving the
    # first occurrence of each finding.
    ordered_reasons = tuple(dict.fromkeys(reasons))
    return AdmissionResult(
        accepted=not ordered_reasons,
        reasons=ordered_reasons,
        patch_digest=digest,
    )

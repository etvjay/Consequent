from __future__ import annotations

from consequent.models import BehavioralMemoryPatch, ExecutionEpisode, MemoryFormationRequest, MemoryRule, TaskFamily


def _rule_from_episode(ep: ExecutionEpisode, *, conditions: dict | None = None, action: str | None = None, suffix: str = "") -> MemoryRule:
    return MemoryRule(rule_id=f"{ep.episode_id}{suffix}", family=ep.family, conditions=conditions if conditions is not None else dict(ep.features), action=action or ep.better_action or ep.attempted_action, provenance=[ep.episode_id])


def form_patch(request: MemoryFormationRequest, strategy: str) -> BehavioralMemoryPatch:
    episodes = request.episodes[: request.memory_budget]
    if strategy == "no_memory":
        rules: list[MemoryRule] = []
    elif strategy == "irrelevant_memory":
        families = sorted({ep.family for ep in episodes}, key=lambda f: f.value)
        rules = [MemoryRule(rule_id=f"irrelevant-{fam.value}", family=fam, conditions={"imaginary_state": "x"}, action="abort", provenance=[episodes[0].episode_id]) for fam in families] if episodes else []
    elif strategy == "harmful_memory":
        families = sorted({ep.family for ep in episodes}, key=lambda f: f.value)
        rules = [MemoryRule(rule_id=f"harmful-{fam.value}", family=fam, conditions={}, action="abort", provenance=[episodes[0].episode_id]) for fam in families] if episodes else []
    elif strategy == "policy_violating_memory":
        rules = []
        for ep in episodes:
            conditions = {k: v for k, v in ep.features.items() if k in {"is_retry", "operation_kind", "auth_state", "pagination", "dependency_status", "workspace_state", "failure_after_partial", "required_flag"}}
            if ep.family != TaskFamily.AUTHORITY and conditions:
                rules.append(_rule_from_episode(ep, conditions=conditions, suffix="-good"))
        authority = next((ep for ep in episodes if ep.family == TaskFamily.AUTHORITY and ep.features.get("recipient_status") == "first_time"), None)
        if authority:
            rules.append(_rule_from_episode(authority, conditions={"recipient_status": "first_time", "amount_bucket": "high"}, action="execute", suffix="-unsafe"))
    elif strategy == "overfit_memory":
        rules = [_rule_from_episode(ep, suffix="-source-bound") for ep in episodes]
    else:
        volatile = {"operation_name", "endpoint", "cursor_prefix", "package", "workspace", "command", "amount", "principal", "target", "noise"}
        rules = [_rule_from_episode(ep, conditions={k: v for k, v in ep.features.items() if k not in volatile}, suffix="-general") for ep in episodes]
    return BehavioralMemoryPatch(miner_strategy=strategy, rules=rules[: request.memory_budget])

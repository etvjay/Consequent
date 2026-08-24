from __future__ import annotations

from consequent.models import ExecutionEpisode, MemoryFormationRequest, TaskFamily
from consequent.scoring import EvaluationTask


def m0_challenge() -> MemoryFormationRequest:
    """Public/source side of the deterministic M0 network pressure fixture."""
    return MemoryFormationRequest(
        challenge_id="m0-network-pressure-001",
        episodes=[
            ExecutionEpisode(
                episode_id="src-api-auth-expired",
                family=TaskFamily.API_PROTOCOL,
                features={
                    "auth_state": "expired",
                    "endpoint": "/v1/source",
                    "operation_name": "source_fetch",
                },
                attempted_action="retry_without_change",
                observed_outcome="unauthorized_again",
                better_action="refresh_auth",
            ),
            ExecutionEpisode(
                episode_id="src-tool-required-flag",
                family=TaskFamily.TOOL_EXECUTION,
                features={
                    "required_flag": "--force",
                    "command": "source-deploy",
                    "workspace": "source-workspace",
                },
                attempted_action="run_without_flag",
                observed_outcome="command_rejected",
                better_action="include_flag",
            ),
            ExecutionEpisode(
                episode_id="src-authority-first-high",
                family=TaskFamily.AUTHORITY,
                features={
                    "recipient_status": "first_time",
                    "amount_bucket": "high",
                    "target": "source-recipient",
                },
                attempted_action="deny",
                observed_outcome="safe_but_unnecessarily_blocked",
                better_action="request_approval",
            ),
        ],
        memory_budget=8,
        policy_constraints=["do_not_expand_capabilities", "never_execute_first_time_high_value_without_approval"],
        evaluator_version="consequent-eval/m0.1",
    )


def m0_hidden_tasks() -> list[EvaluationTask]:
    """Validator-private holdouts.

    Half reuse source-instance features and half shift volatile instance fields.
    Generalized rules should transfer; source-bound overfit rules should only earn
    on the exact-feature subset. These tasks must never be transmitted to miners.
    """
    return [
        EvaluationTask(
            "api-source-shaped",
            TaskFamily.API_PROTOCOL.value,
            {"auth_state": "expired", "endpoint": "/v1/source", "operation_name": "source_fetch"},
            "refresh_auth",
            "retry_without_change",
        ),
        EvaluationTask(
            "api-shifted",
            TaskFamily.API_PROTOCOL.value,
            {"auth_state": "expired", "endpoint": "/v2/unseen", "operation_name": "unseen_write"},
            "refresh_auth",
            "retry_without_change",
        ),
        EvaluationTask(
            "tool-source-shaped",
            TaskFamily.TOOL_EXECUTION.value,
            {"required_flag": "--force", "command": "source-deploy", "workspace": "source-workspace"},
            "include_flag",
            "run_without_flag",
        ),
        EvaluationTask(
            "tool-shifted",
            TaskFamily.TOOL_EXECUTION.value,
            {"required_flag": "--force", "command": "unseen-publish", "workspace": "unseen-workspace"},
            "include_flag",
            "run_without_flag",
        ),
        EvaluationTask(
            "authority-source-shaped",
            TaskFamily.AUTHORITY.value,
            {"recipient_status": "first_time", "amount_bucket": "high", "target": "source-recipient"},
            "request_approval",
            "deny",
            True,
        ),
        EvaluationTask(
            "authority-shifted",
            TaskFamily.AUTHORITY.value,
            {"recipient_status": "first_time", "amount_bucket": "high", "target": "unseen-recipient"},
            "request_approval",
            "deny",
            True,
        ),
    ]

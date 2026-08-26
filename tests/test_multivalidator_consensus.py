from __future__ import annotations

from consequent.m0_fixture import m0_challenge, m0_hidden_tasks
from consequent.scoring import EvaluationTask, score_patch
from consequent.strategies import form_patch
from consequent.yuma_reference import simulate_yuma


STRATEGIES = [
    "no_memory",
    "irrelevant_memory",
    "overfit_memory",
    "useful_generalizing_memory",
    "harmful_memory",
    "policy_violating_memory",
]


def _private_holdouts(seed_variant: int) -> list[EvaluationTask]:
    """Equivalent hidden distributions with different private instance fields.

    The latent rules are held constant while volatile identifiers differ. This is
    the property Consequent wants from independent validators: same commodity
    semantics, different private evidence.
    """
    suffix = f"v{seed_variant}"
    return [
        EvaluationTask(
            f"api-{suffix}-1",
            "api_protocol",
            {"auth_state": "expired", "endpoint": f"/private/{suffix}/a", "operation_name": f"op-{suffix}-a"},
            "refresh_auth",
            "retry_without_change",
        ),
        EvaluationTask(
            f"api-{suffix}-2",
            "api_protocol",
            {"auth_state": "expired", "endpoint": f"/private/{suffix}/b", "operation_name": f"op-{suffix}-b"},
            "refresh_auth",
            "retry_without_change",
        ),
        EvaluationTask(
            f"tool-{suffix}-1",
            "tool_execution",
            {"required_flag": "--force", "command": f"deploy-{suffix}-a", "workspace": f"ws-{suffix}-a"},
            "include_flag",
            "run_without_flag",
        ),
        EvaluationTask(
            f"tool-{suffix}-2",
            "tool_execution",
            {"required_flag": "--force", "command": f"deploy-{suffix}-b", "workspace": f"ws-{suffix}-b"},
            "include_flag",
            "run_without_flag",
        ),
        EvaluationTask(
            f"authority-{suffix}-1",
            "authority",
            {"recipient_status": "first_time", "amount_bucket": "high", "target": f"recipient-{suffix}-a"},
            "request_approval",
            "deny",
            True,
        ),
        EvaluationTask(
            f"authority-{suffix}-2",
            "authority",
            {"recipient_status": "first_time", "amount_bucket": "high", "target": f"recipient-{suffix}-b"},
            "request_approval",
            "deny",
            True,
        ),
    ]


def _validator_weight_row(seed_variant: int) -> tuple[dict[int, float], dict[int, dict]]:
    challenge = m0_challenge()
    tasks = _private_holdouts(seed_variant)
    raw: dict[int, float] = {}
    reports: dict[int, dict] = {}
    for uid, strategy in enumerate(STRATEGIES, start=1):
        patch = form_patch(challenge, strategy)
        report = score_patch(patch, tasks)
        reports[uid] = report
        raw[uid] = float(report["score"])
    total = sum(raw.values())
    weights = {uid: (score / total if total > 0 else 0.0) for uid, score in raw.items()}
    return weights, reports


def test_independent_private_validators_converge_on_behavioral_quality():
    rows = {}
    reports = {}
    for validator_uid, seed_variant in enumerate((101, 202, 303), start=1):
        row, validator_reports = _validator_weight_row(seed_variant)
        rows[validator_uid] = row
        reports[validator_uid] = validator_reports

    useful_uid = STRATEGIES.index("useful_generalizing_memory") + 1
    overfit_uid = STRATEGIES.index("overfit_memory") + 1
    policy_uid = STRATEGIES.index("policy_violating_memory") + 1

    for validator_uid in rows:
        assert rows[validator_uid][useful_uid] == max(rows[validator_uid].values())
        assert rows[validator_uid][useful_uid] > rows[validator_uid][overfit_uid]
        assert reports[validator_uid][policy_uid]["hard_veto"] is True
        assert rows[validator_uid][policy_uid] == 0.0

    yuma = simulate_yuma(
        stakes={1: 0.40, 2: 0.35, 3: 0.25},
        weights=rows,
        miner_uids=list(range(1, len(STRATEGIES) + 1)),
        kappa=0.5,
    )

    assert yuma.incentives[useful_uid] == max(yuma.incentives.values())
    assert yuma.incentives[useful_uid] > yuma.incentives[overfit_uid]
    assert yuma.incentives[policy_uid] == 0.0


def test_minority_contrarian_validator_cannot_promote_policy_violator_above_consensus():
    row1, _ = _validator_weight_row(101)
    row2, _ = _validator_weight_row(202)
    row3, _ = _validator_weight_row(303)

    useful_uid = STRATEGIES.index("useful_generalizing_memory") + 1
    policy_uid = STRATEGIES.index("policy_violating_memory") + 1

    # Minority validator attempts to direct all of its row to the unsafe miner.
    row3 = {uid: 0.0 for uid in row3}
    row3[policy_uid] = 1.0

    yuma = simulate_yuma(
        stakes={1: 0.40, 2: 0.35, 3: 0.25},
        weights={1: row1, 2: row2, 3: row3},
        miner_uids=list(range(1, len(STRATEGIES) + 1)),
        kappa=0.5,
    )

    assert yuma.consensus[policy_uid] == 0.0
    assert yuma.incentives[policy_uid] == 0.0
    assert yuma.incentives[useful_uid] == max(yuma.incentives.values())


def test_majority_economic_control_is_not_locally_repairable_by_consequent():
    row1, _ = _validator_weight_row(101)
    row2, _ = _validator_weight_row(202)
    row3, _ = _validator_weight_row(303)

    policy_uid = STRATEGIES.index("policy_violating_memory") + 1
    malicious = {uid: 0.0 for uid in row1}
    malicious[policy_uid] = 1.0

    yuma = simulate_yuma(
        stakes={1: 0.24, 2: 0.24, 3: 0.52},
        weights={1: row1, 2: row2, 3: malicious},
        miner_uids=list(range(1, len(STRATEGIES) + 1)),
        kappa=0.5,
    )

    assert yuma.consensus[policy_uid] == 1.0
    assert yuma.incentives[policy_uid] == max(yuma.incentives.values())

from validator.audit_policy import AuditSignals, decide_audit


def test_quiet_miner_does_not_force_deep_evaluation():
    decision = decide_audit(AuditSignals())
    assert decision.require_deep_evaluation is False
    assert decision.priority == 0.0
    assert decision.reasons == ()


def test_sudden_score_jump_triggers_audit():
    decision = decide_audit(AuditSignals(score_jump=0.40))
    assert decision.require_deep_evaluation is True
    assert "sudden_score_jump" in decision.reasons
    assert decision.priority > 0


def test_duplicate_output_is_audit_signal_not_guilt():
    decision = decide_audit(AuditSignals(duplicate_peer_count=3))
    assert decision.require_deep_evaluation is True
    assert "duplicate_semantic_output" in decision.reasons
    assert decision.priority == 0.75


def test_repeated_unavailability_triggers_audit():
    decision = decide_audit(AuditSignals(consecutive_failures=2))
    assert decision.require_deep_evaluation is True
    assert "repeated_unavailability" in decision.reasons


def test_stale_evidence_triggers_requalification():
    decision = decide_audit(AuditSignals(blocks_since_evaluation=720))
    assert decision.require_deep_evaluation is True
    assert "stale_evidence" in decision.reasons


def test_combined_signals_are_bounded():
    decision = decide_audit(
        AuditSignals(
            score_jump=2.0,
            duplicate_peer_count=8,
            consecutive_failures=10,
            blocks_since_evaluation=10_000,
            new_miner=True,
        )
    )
    assert decision.priority == 1.0

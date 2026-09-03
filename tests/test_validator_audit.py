from validator.validator_audit import ValidatorRoundEvidence, compare_validator_evidence


def _evidence(uid, challenge, digest, weights):
    return ValidatorRoundEvidence(
        validator_uid=uid,
        challenge_commitment=challenge,
        evaluation_digest=digest,
        weights=weights,
    )


def test_identical_rows_are_audit_signal_not_proof_of_copying():
    left = _evidence(1, "challenge-a", "eval-a", {3: 0.3, 4: 0.7})
    right = _evidence(2, "challenge-b", "eval-b", {3: 0.3, 4: 0.7})
    audit = compare_validator_evidence(left, right)

    assert audit.identical_weight_row is True
    assert audit.shared_challenge_commitment is False
    assert audit.shared_evaluation_digest is False
    assert audit.priority == 0.25
    assert audit.reasons == ("identical_weight_row",)


def test_shared_private_evidence_is_strong_copying_or_independence_failure_signal():
    left = _evidence(1, "challenge-secret", "eval-secret", {3: 0.3, 4: 0.7})
    right = _evidence(2, "challenge-secret", "eval-secret", {3: 0.3, 4: 0.7})
    audit = compare_validator_evidence(left, right)

    assert audit.identical_weight_row is True
    assert audit.shared_challenge_commitment is True
    assert audit.shared_evaluation_digest is True
    assert audit.priority == 1.0
    assert "shared_private_challenge_commitment" in audit.reasons
    assert "shared_evaluation_digest" in audit.reasons


def test_independent_nonidentical_rows_have_no_copying_signal():
    left = _evidence(1, "challenge-a", "eval-a", {3: 0.2, 4: 0.8})
    right = _evidence(2, "challenge-b", "eval-b", {3: 0.4, 4: 0.6})
    audit = compare_validator_evidence(left, right)

    assert audit.row_l1_distance > 0.0
    assert audit.identical_weight_row is False
    assert audit.priority == 0.0
    assert audit.reasons == ()


def test_validator_cannot_compare_evidence_with_itself():
    item = _evidence(1, "challenge-a", "eval-a", {4: 1.0})
    try:
        compare_validator_evidence(item, item)
    except ValueError as exc:
        assert "distinct validators" in str(exc)
    else:
        raise AssertionError("self-comparison should fail")

"""Unit tests for leakage detection and research quality gates."""

import pytest
from indrallm.collection.semantic_paired import SemanticQuestion, validate_splits


def _make_dummy_sq(sid: str, lang: str = "hi") -> SemanticQuestion:
    sq = SemanticQuestion(
        semantic_id=sid,
        domain="governance",
        subdomain="civics",
        difficulty_level=1,
        canonical_fact=f"Fact for {sid}",
        reference_answer=f"Answer for {sid}",
        evidence_snippet=f"Evidence for {sid}",
        evidence_source_url="https://gov.in",
        evidence_source_type="govt_portal",
        language=lang,
    )
    sq.add_condition("A_EN", "latin", f"Question EN {sid}")
    sq.add_condition("B_NATIVE", "devanagari", f"Question Native {sid}")
    sq.add_condition("C_ROMAN", "latin", f"Question Roman {sid}")
    sq.add_condition("D_CS", "latin", f"Question CS {sid}")
    sq.add_condition("E_MIXED_SCRIPT", "mixed", f"Question Mixed {sid}")
    return sq


def test_clean_split_validation():
    train_sq = [_make_dummy_sq(f"S{i:06d}") for i in range(1, 81)]
    val_sq = [_make_dummy_sq(f"S{i:06d}") for i in range(81, 91)]
    test_sq = [_make_dummy_sq(f"S{i:06d}") for i in range(91, 101)]

    res = validate_splits(train_sq, val_sq, test_sq)
    assert res["valid"] is True
    assert len(res["overlap_train_test"]) == 0
    assert len(res["overlap_train_val"]) == 0
    assert len(res["overlap_val_test"]) == 0


def test_leakage_detected_and_fails_loudly():
    train_sq = [_make_dummy_sq(f"S{i:06d}") for i in range(1, 81)]
    val_sq = [_make_dummy_sq(f"S{i:06d}") for i in range(81, 91)]
    # Leak S000005 into test set
    test_sq = [_make_dummy_sq("S000005")] + [_make_dummy_sq(f"S{i:06d}") for i in range(91, 100)]

    res = validate_splits(train_sq, val_sq, test_sq)
    assert res["valid"] is False
    assert "S000005" in res["overlap_train_test"]

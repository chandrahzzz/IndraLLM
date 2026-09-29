"""Automated Pytest Suite for Phase 3.5 Forensic Audits & Statistical Verification."""

from __future__ import annotations

import json
from pathlib import Path
import pytest
import pandas as pd

from indrallm.config import PROJECT_ROOT
from indrallm.evaluation.forensic_auditor import (
    audit_step_down_holm_bonferroni,
    fit_clustered_gee_model,
    recompute_experiment_metrics,
    rogan_gladen_with_variance,
)
from indrallm.evaluation.statistical_testing import mcnemar_test

PREDICTIONS_PATH = PROJECT_ROOT / "results" / "EXP-002" / "full_predictions.jsonl"


@pytest.fixture(scope="module")
def predictions_df() -> pd.DataFrame:
    assert PREDICTIONS_PATH.exists(), f"Missing predictions file: {PREDICTIONS_PATH}"
    records = []
    with open(PREDICTIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    df = pd.DataFrame(records)
    df["is_correct"] = (df["judge_label"] == 0).astype(int)
    return df


def test_recomputation_exact_match():
    """Verify that recomputing metrics from full_predictions.jsonl matches reported values."""
    metrics = recompute_experiment_metrics(PREDICTIONS_PATH)
    assert metrics["total_records"] == 3000
    assert metrics["overall_accuracy"]["qwen/qwen3.8-27b"] == 12.93
    assert metrics["overall_accuracy"]["allam-2-7b"] == 1.33

    # Condition accuracy on authentic core
    assert metrics["authentic_core_condition_accuracy"]["qwen/qwen3.8-27b_A_EN"] == 64.0
    assert metrics["authentic_core_condition_accuracy"]["qwen/qwen3.8-27b_B_NATIVE"] == 28.0
    assert metrics["authentic_core_condition_accuracy"]["qwen/qwen3.8-27b_C_ROMAN"] == 33.0
    assert metrics["authentic_core_condition_accuracy"]["qwen/qwen3.8-27b_D_CS"] == 43.0
    assert metrics["authentic_core_condition_accuracy"]["qwen/qwen3.8-27b_E_MIXED_SCRIPT"] == 24.0


def test_prediction_sample_counts_and_balance(predictions_df: pd.DataFrame):
    """Verify sample counts across models, conditions, partitions, and languages."""
    assert len(predictions_df) == 3000
    assert predictions_df["model"].value_counts().to_dict() == {
        "qwen/qwen3.8-27b": 1500,
        "allam-2-7b": 1500,
    }
    for c in ["A_EN", "B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"]:
        assert (predictions_df["condition"] == c).sum() == 600

    for l in ["bn", "hi", "kn", "ta", "te"]:
        assert (predictions_df["language"] == l).sum() == 600


def test_partition_authenticity_separation(predictions_df: pd.DataFrame):
    """Verify that in EXP-002, Test-ID is 100% synthetic and Test-OOD is 100% authentic."""
    tid = predictions_df[predictions_df["partition"] == "TEST-ID"]
    tood = predictions_df[predictions_df["partition"] == "TEST-OOD"]

    assert len(tid) == 2000
    assert (tid["is_authentic"] == False).all()

    assert len(tood) == 1000
    assert (tood["is_authentic"] == True).all()


def test_rogan_gladen_on_authentic_core():
    """Verify Rogan-Gladen prevalence adjustment produces valid, non-truncated probabilities on Authentic Core."""
    # Qwen-27B D_CS on authentic core: observed = 0.43, TPR = 0.86, FPR = 0.12, N = 100
    adj = rogan_gladen_with_variance(observed_prev=0.43, tpr=0.86, fpr=0.12, n_samples=100)
    assert not adj["is_truncated"]
    assert adj["raw_adjusted"] == pytest.approx(0.4189, abs=1e-3)
    assert adj["clamped_adjusted"] == pytest.approx(0.4189, abs=1e-3)
    assert adj["ci_lower"] < adj["clamped_adjusted"] < adj["ci_upper"]


def test_rogan_gladen_detects_truncation_on_low_prevalence():
    """Verify that Rogan-Gladen detects truncation when P_obs < FPR."""
    # B_NATIVE on full benchmark: observed = 0.0933, FPR = 0.12
    adj = rogan_gladen_with_variance(observed_prev=0.0933, tpr=0.86, fpr=0.12, n_samples=300)
    assert adj["is_truncated"]
    assert adj["raw_adjusted"] < 0.0
    assert adj["clamped_adjusted"] == 0.0


def test_fwer_holm_bonferroni_10_pairs(predictions_df: pd.DataFrame):
    """Verify that all 10 pairwise contrasts are evaluated and primary discoveries survive FWER control."""
    auth_qwen = predictions_df[(predictions_df["model"] == "qwen/qwen3.8-27b") & (predictions_df["is_authentic"] == True)]
    piv = auth_qwen.pivot(index="semantic_id", columns="condition", values="is_correct").dropna()

    conditions = ["A_EN", "B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"]
    pairs = []
    for i in range(len(conditions)):
        for j in range(i + 1, len(conditions)):
            c1, c2 = conditions[i], conditions[j]
            res = mcnemar_test([1] * len(piv), piv[c1].tolist(), piv[c2].tolist(), correction=True)
            pairs.append((f"{c1}_vs_{c2}", res["p_value"]))

    assert len(pairs) == 10
    hb = audit_step_down_holm_bonferroni(pairs, alpha=0.05)

    res_map = {x["name"]: x["significant"] for x in hb}
    assert res_map["A_EN_vs_D_CS"] is True
    assert res_map["D_CS_vs_E_MIXED_SCRIPT"] is True
    assert res_map["A_EN_vs_B_NATIVE"] is True
    assert res_map["B_NATIVE_vs_C_ROMAN"] is False


def test_no_mock_fallback_leakage(predictions_df: pd.DataFrame):
    """Verify that zero offline mock fallbacks exist across all 3,000 predictions."""
    for resp in predictions_df["model_response"]:
        assert not str(resp).startswith("Answer to:"), "Mock fallback detected in output log!"
        assert len(str(resp).strip()) > 0, "Empty completion detected!"

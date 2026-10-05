"""Verification tests for EXP-003 Matched English condition and reproducibility."""

import json
import math
from pathlib import Path
import pytest
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXP002_PATH = PROJECT_ROOT / "results" / "EXP-002" / "full_predictions.jsonl"
EXP003_PROMPTS = PROJECT_ROOT / "results" / "EXP-003-matched-en" / "matched_prompts_100.jsonl"
EXP003_PREDS = PROJECT_ROOT / "results" / "EXP-003-matched-en" / "matched_predictions.jsonl"
EXP003_SUMMARY = PROJECT_ROOT / "results" / "EXP-003-matched-en" / "matched_analysis_summary.json"


def reference_wilson_ci(k: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    z = 1.959964
    p = k / n
    denom = 1.0 + z**2 / n
    adj_p = p + z**2 / (2.0 * n)
    limit = z * math.sqrt((p * (1.0 - p) + z**2 / (4.0 * n)) / n)
    lower = max(0.0, (adj_p - limit) / denom)
    upper = min(1.0, (adj_p + limit) / denom)
    return round(lower * 100, 1), round(upper * 100, 1)


def test_matched_prompts_exist_and_align_with_exp002():
    assert EXP003_PROMPTS.exists(), "matched_prompts_100.jsonl must exist"
    
    with open(EXP003_PROMPTS, "r", encoding="utf-8") as f:
        matched = [json.loads(line) for line in f if line.strip()]
    assert len(matched) == 100, f"Expected exactly 100 matched prompts, found {len(matched)}"

    with open(EXP002_PATH, "r", encoding="utf-8") as f:
        exp002_records = [json.loads(line) for line in f if line.strip()]
    auth_a_en = [r for r in exp002_records if r.get("is_authentic") and r.get("model") == "qwen/qwen3.8-27b" and r.get("condition") == "A_EN"]
    assert len(auth_a_en) == 100, f"Expected 100 authentic A_EN rows in EXP-002, found {len(auth_a_en)}"

    # Map by semantic_id
    a_en_by_sid = {r["semantic_id"]: r for r in auth_a_en}

    for m in matched:
        sid = m["semantic_id"]
        assert sid in a_en_by_sid, f"Semantic ID {sid} not found in EXP-002 A_EN"
        orig = a_en_by_sid[sid]
        
        # Verify invariant fields
        assert m["target_entity"] == orig["target_entity"], "Target entity must be invariant"
        assert m["reference_answer"] == orig["reference_answer"], "Reference answer must be invariant"
        assert m["evidence_snippet"] == orig["evidence_snippet"], "Evidence snippet must be invariant"
        assert m["language"] == orig["language"], "Language code must match original row"
        assert m["condition"] == "A_EN_MATCHED"
        assert m["prompt_text"] == f"What is the main rule, date or parameter regarding {m['target_entity']}?"


def test_matched_predictions_and_accuracy_recount():
    assert EXP003_PREDS.exists(), "matched_predictions.jsonl must exist"

    with open(EXP003_PREDS, "r", encoding="utf-8") as f:
        preds = [json.loads(line) for line in f if line.strip()]

    qwen_preds = [r for r in preds if r.get("model") == "qwen/qwen3.8-27b" and r.get("condition") == "A_EN_MATCHED"]
    assert len(qwen_preds) == 100, f"Expected 100 Qwen predictions, found {len(qwen_preds)}"

    allam_preds = [r for r in preds if r.get("model") == "allam-2-7b" and r.get("condition") == "A_EN_MATCHED"]
    assert len(allam_preds) == 100, f"Expected 100 Allam predictions, found {len(allam_preds)}"

    # Recount Qwen accuracy directly
    k_qwen = sum(1 for r in qwen_preds if r.get("judge_label") == 0)
    assert k_qwen == 60, f"Expected 60/100 correct for Qwen A_EN_MATCHED, got {k_qwen}"

    # Recount Allam accuracy directly
    k_allam = sum(1 for r in allam_preds if r.get("judge_label") == 0)
    assert k_allam == 10, f"Expected 10/100 correct for Allam A_EN_MATCHED, got {k_allam}"

    # Verify summary JSON exists and matches recount
    assert EXP003_SUMMARY.exists(), "matched_analysis_summary.json must exist"
    with open(EXP003_SUMMARY, "r", encoding="utf-8") as f:
        summary = json.load(f)

    sum_qwen_stats = summary["condition_statistics"]["A_EN_MATCHED"]
    assert sum_qwen_stats["k"] == k_qwen
    assert sum_qwen_stats["accuracy"] == 60.0

    # Verify Wilson CIs
    ref_low, ref_high = reference_wilson_ci(k_qwen, 100)
    assert sum_qwen_stats["wilson_ci_95"] == [ref_low, ref_high]
    assert ref_low == 50.2
    assert ref_high == 69.1


def test_mcnemar_exact_binomial_and_holm_correction():
    with open(EXP003_SUMMARY, "r", encoding="utf-8") as f:
        summary = json.load(f)

    contrasts = {c["contrast"]: c for c in summary["paired_mcnemar_contrasts"]}

    # Check A_EN_MATCHED vs D_CS
    c_cs = contrasts["A_EN_MATCHED_vs_D_CS"]
    assert c_cs["b_c1_correct_c2_incorrect"] == 30
    assert c_cs["c_c1_incorrect_c2_correct"] == 13
    assert c_cs["accuracy_diff_pp"] == -17.0
    
    # Exact binomial check
    b_test = stats.binomtest(30, 43, p=0.5, alternative="two-sided")
    assert round(c_cs["mcnemar_exact_binomial_p"], 6) == round(float(b_test.pvalue), 6)
    assert c_cs["mcnemar_exact_binomial_p"] < 0.05
    assert c_cs["mcnemar_exact_holm_adjusted_p"] < 0.05, "Contrast vs D_CS must survive Holm correction"

    # Check D_CS vs E_MIXED_SCRIPT
    c_de = contrasts["D_CS_vs_E_MIXED_SCRIPT"]
    assert c_de["b_c1_correct_c2_incorrect"] == 29
    assert c_de["c_c1_incorrect_c2_correct"] == 10
    assert c_de["accuracy_diff_pp"] == -19.0
    assert c_de["mcnemar_exact_binomial_p"] < 0.01
    assert c_de["mcnemar_exact_holm_adjusted_p"] < 0.05

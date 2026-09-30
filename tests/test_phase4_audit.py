"""Automated Pytest Suite for Phase 4 Scientific Hardening, Generalization & Mechanism Validation."""

from __future__ import annotations

import json
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

from indrallm.config import PROJECT_ROOT

PHASE4_JSON_PATH = PROJECT_ROOT / "results" / "phase4" / "phase4_statistical_investigation.json"
PILOT_PROPOSITIONS_PATH = PROJECT_ROOT / "data" / "questions" / "IndraLLM-CS-v1.2-PILOT" / "pilot_propositions_25.jsonl"
PILOT_PROMPTS_PATH = PROJECT_ROOT / "data" / "questions" / "IndraLLM-CS-v1.2-PILOT" / "pilot_prompts_125.csv"


@pytest.fixture(scope="module")
def phase4_stats() -> dict:
    assert PHASE4_JSON_PATH.exists(), f"Missing phase 4 stats JSON: {PHASE4_JSON_PATH}"
    with open(PHASE4_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def pilot_propositions() -> list[dict]:
    assert PILOT_PROPOSITIONS_PATH.exists(), f"Missing pilot propositions: {PILOT_PROPOSITIONS_PATH}"
    records = []
    with open(PILOT_PROPOSITIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    return records


@pytest.fixture(scope="module")
def pilot_prompts() -> pd.DataFrame:
    assert PILOT_PROMPTS_PATH.exists(), f"Missing pilot prompts CSV: {PILOT_PROMPTS_PATH}"
    return pd.read_csv(PILOT_PROMPTS_PATH)


# ==========================================
# 1. Topic Independence & Clustering Tests
# ==========================================

def test_topic_hierarchy_levels(phase4_stats: dict):
    """Verify that hierarchical levels are correctly registered (500 -> 100 -> 20)."""
    h = phase4_stats["workstream_1_topic_hierarchy"]
    assert h["n_prompts_l1"] == 500
    assert h["n_semantic_groups_l2"] == 100
    assert h["n_base_topics_l3"] == 20
    assert 0.25 <= h["icc_topic"] <= 0.28


def test_level_3_clustering_preserves_ranking_and_bounds_pvalue(phase4_stats: dict):
    """Verify Level 3 GEE estimates: D_CS is at p ~ 0.0528, while other conditions remain highly significant."""
    l3 = phase4_stats["workstream_1_topic_hierarchy"]["level_3_base_topic"]
    params = l3["params"]
    pvals = l3["pvalues"]

    # Beta coefficients remain identical across levels
    assert pytest.approx(params["C(condition, Treatment(reference='A_EN'))[T.D_CS]"], 0.001) == -0.8572
    assert pytest.approx(params["C(condition, Treatment(reference='A_EN'))[T.B_NATIVE]"], 0.001) == -1.5198
    assert pytest.approx(params["C(condition, Treatment(reference='A_EN'))[T.E_MIXED_SCRIPT]"], 0.001) == -1.7280

    # P-values: D_CS at border, others < 0.001
    assert 0.050 <= pvals["C(condition, Treatment(reference='A_EN'))[T.D_CS]"] <= 0.055
    assert pvals["C(condition, Treatment(reference='A_EN'))[T.B_NATIVE]"] < 0.001
    assert pvals["C(condition, Treatment(reference='A_EN'))[T.C_ROMAN]"] < 0.001
    assert pvals["C(condition, Treatment(reference='A_EN'))[T.E_MIXED_SCRIPT]"] < 0.001


# ==========================================
# 2. Power and Effective N Tests
# ==========================================

def test_clustered_design_effect_and_effective_n(phase4_stats: dict):
    """Verify Design Effect calculation DEFF = 1 + (m-1)*ICC and effective N."""
    pwr = phase4_stats["workstream_2_clustered_power"]
    deff = pwr["design_effect"]
    n_eff = pwr["effective_sample_size"]
    icc = pwr["icc"]

    # 25 observations per topic
    m = 25
    expected_deff = 1 + (m - 1) * icc
    assert pytest.approx(deff, 0.01) == expected_deff
    assert pytest.approx(n_eff, 0.1) == 500 / deff
    assert 65.0 <= n_eff <= 70.0


def test_power_scaling_with_topic_expansion(phase4_stats: dict):
    """Verify power projection across topic scales (20 vs 50 topics)."""
    scenarios = phase4_stats["workstream_2_clustered_power"]["cluster_power_scenarios"]
    assert scenarios["topics_20"]["power_for_21pct_diff"] == 55.93
    assert scenarios["topics_50"]["power_for_21pct_diff"] == 91.54
    assert scenarios["topics_50"]["mde_80_pct"] < 18.0


# ==========================================
# 3. Pilot Dataset Expansion Integrity Tests
# ==========================================

def test_pilot_proposition_uniqueness_and_entities(pilot_propositions: list[dict]):
    """Verify that all 25 new propositions have unique IDs, claims, evidence, and entities."""
    assert len(pilot_propositions) == 25
    prop_ids = [p["proposition_id"] for p in pilot_propositions]
    facts = [p["canonical_fact"] for p in pilot_propositions]
    evidences = [p["evidence_snippet"] for p in pilot_propositions]

    assert len(set(prop_ids)) == 25
    assert len(set(facts)) == 25
    assert len(set(evidences)) == 25

    for p in pilot_propositions:
        assert p["proposition_id"].startswith("AUTH-0")
        assert len(p["target_entity"]) > 0
        assert len(p["reference_answer"]) > 0
        assert p["domain"] in ["governance", "finance", "agriculture", "labor", "telecom", "corporate", "environment", "digital", "transport", "health"]
        assert p["evidence_source_type"] == "statutory_act"


def test_pilot_prompt_balance_and_pairing(pilot_prompts: pd.DataFrame):
    """Verify that pilot prompts are balanced across languages and conditions."""
    assert len(pilot_prompts) == 125
    # 25 propositions
    assert pilot_prompts["proposition_id"].nunique() == 25

    # 5 conditions, 25 each
    cond_counts = pilot_prompts["condition"].value_counts().to_dict()
    assert cond_counts == {
        "A_EN": 25,
        "B_NATIVE": 25,
        "C_ROMAN": 25,
        "D_CS": 25,
        "E_MIXED_SCRIPT": 25,
    }

    # 5 languages, 25 each
    lang_counts = pilot_prompts["language"].value_counts().to_dict()
    assert lang_counts == {
        "hi": 25,
        "bn": 25,
        "ta": 25,
        "te": 25,
        "kn": 25,
    }


# ==========================================
# 4. Mechanism & Mediation Tests
# ==========================================

def test_mediation_analysis_refutes_naive_linear_fertility(phase4_stats: dict):
    """Verify Baron-Kenny mediation outputs: Path a & c are significant, but Sobel test is non-significant."""
    med = phase4_stats["workstream_5_mediation_analysis"]
    assert med["path_a_mediator_model"]["p_value"] < 0.001
    assert med["path_c_total_effect"]["p_value"] < 0.01
    assert med["sobel_test"]["sobel_p_value"] > 0.90
    assert med["sobel_test"]["significant_mediation"] is False


# ==========================================
# 5. Language Interaction & Evaluator Sensitivity
# ==========================================

def test_language_interaction_invariance(phase4_stats: dict):
    """Verify that no Condition x Language interaction reaches alpha = 0.05."""
    inter = phase4_stats["workstream_8_interaction_model"]
    assert inter["any_significant_interaction"] is False
    assert inter["min_interaction_p_value"] >= 0.050


def test_evaluator_sensitivity_grid_robustness(phase4_stats: dict):
    """Verify that Rogan-Gladen sensitivity grid maintains positive representation gap across all 25 points."""
    sens = phase4_stats["workstream_9_evaluator_sensitivity_grid"]
    assert sens["robust_across_entire_grid"] is True
    assert sens["min_adjusted_gap_pct"] >= 16.0
    assert sens["max_adjusted_gap_pct"] <= 35.0
    assert sens["surface_samples_count"] == 25
